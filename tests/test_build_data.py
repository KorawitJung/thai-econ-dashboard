import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import bot_api  # noqa: E402
import build_data  # noqa: E402
import series  # noqa: E402
from sources import SourceError  # noqa: E402


def frame(days_ago: list[int], value: float = 1.0) -> pd.DataFrame:
    today = date.today()
    return pd.DataFrame({"date": pd.to_datetime([today - timedelta(days=d) for d in days_ago]), "value": value})


def a_meeting() -> bot_api.Meeting:
    return bot_api.Meeting(date.today() - timedelta(days=20), "คงอัตรา", "Held the rate")


def with_fetches(monkeypatch, meeting=a_meeting, **by_id):
    """Point every series at a local fetch so no test touches the network."""
    regs = [series.Series(**{**vars(s), "fetch": by_id.get(s.id, lambda st, e: frame([400, 30, 1])),
                             "meeting": meeting if s.meeting else None}) for s in series.SERIES]
    monkeypatch.setattr(build_data, "SERIES", regs)


class Reply:
    def __init__(self, js):
        self.js = js

    def json(self):
        return self.js


def test_sample_writes_every_series_in_the_shape_the_app_reads(tmp_path):
    out = tmp_path / "dashboard.json"
    build_data.main(["--sample", "--out", str(out)])
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["source"] == "sample"
    assert [s["id"] for s in data["series"]] == [s.id for s in series.SERIES]
    for s in data["series"]:
        dates = [p[0] for p in s["points"]]
        assert dates == sorted(dates), f"{s['id']} points are in date order"
        assert all(isinstance(p[1], float) for p in s["points"])
        assert s["group"] in {g["id"] for g in data["groups"]}
        assert s["change"] in {"pct", "diff"}


def test_a_failing_source_writes_nothing(tmp_path, monkeypatch):
    def down(start, end):
        raise SourceError("HTTP 503")
    with_fetches(monkeypatch, cpi_yoy=down)
    out = tmp_path / "dashboard.json"
    with pytest.raises(SystemExit, match="Could not get cpi_yoy: HTTP 503"):
        build_data.main(["--out", str(out)])
    assert not out.exists()


def test_stale_daily_series_writes_nothing(tmp_path, monkeypatch):
    with_fetches(monkeypatch, usd_thb=lambda s, e: frame([40, 8]))
    out = tmp_path / "dashboard.json"
    with pytest.raises(SystemExit, match="more than 7 days ago"):
        build_data.main(["--out", str(out)])
    assert not out.exists()


def test_policy_rate_is_carried_from_the_last_decision_to_today(monkeypatch, tmp_path):
    decisions = pd.DataFrame({"date": pd.to_datetime(["2020-06-01", date.today() - timedelta(days=200)]), "value": [0.5, 2.0]})
    with_fetches(monkeypatch, policy_rate=lambda st, e: decisions)
    out = tmp_path / "dashboard.json"
    build_data.main(["--out", str(out)])
    policy = next(s for s in json.loads(out.read_text(encoding="utf-8"))["series"] if s["frequency"] == "event")
    assert policy["points"][0][1] == 0.5, "value in force at the window start"
    assert policy["points"][-1] == [date.today().isoformat(), 2.0], "last decision extends to today"


def test_daily_policy_rate_keeps_only_decision_days(monkeypatch, tmp_path):
    days = pd.date_range(date.today() - timedelta(days=60), date.today())
    daily = pd.DataFrame({"date": days, "value": [1.25] * 30 + [1.0] * (len(days) - 30)})
    old = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "value": [1.25]})
    with_fetches(monkeypatch, policy_rate=lambda st, e: pd.concat([old, daily]))
    out = tmp_path / "dashboard.json"
    build_data.main(["--out", str(out)])
    policy = next(s for s in json.loads(out.read_text(encoding="utf-8"))["series"] if s["id"] == "policy_rate")
    values = [v for _, v in policy["points"]]
    assert values == [1.25, 1.0, 1.0], "window start, the cut, and today"
    dates = [d for d, _ in policy["points"]]
    assert len(dates) == len(set(dates)), "no date appears twice"


def test_missing_bot_token_names_the_variable_and_writes_nothing(monkeypatch, tmp_path):
    monkeypatch.delenv(bot_api.EXCHANGE_TOKEN, raising=False)
    bot_api._mid_rates.cache_clear()
    with_fetches(monkeypatch, usd_thb=lambda st, e: bot_api.mid_rate("USD", st, e))
    out = tmp_path / "dashboard.json"
    with pytest.raises(SystemExit, match=f"Could not get usd_thb: {bot_api.EXCHANGE_TOKEN} is not set"):
        build_data.main(["--out", str(out)])
    assert not out.exists()


def test_bot_mid_rate_keeps_one_currency_oldest_first_and_skips_blank_days(monkeypatch):
    rows = [
        {"period": "2026-11-25", "currency_id": "USD", "mid_rate": "33.9925000"},
        {"period": "2026-11-25", "currency_id": "JPY", "mid_rate": "21.3603000"},
        {"period": "2026-11-24", "currency_id": "USD", "mid_rate": ""},
        {"period": "2026-11-23", "currency_id": "USD ", "mid_rate": "33.9000000"},
    ]
    calls = []

    def fake(url, params, headers):
        calls.append(params)
        return Reply({"result": {"data": {"data_detail": rows}}})
    monkeypatch.setenv(bot_api.EXCHANGE_TOKEN, "test-token")
    monkeypatch.setattr(bot_api, "http_get", fake)
    bot_api._mid_rates.cache_clear()
    usd = bot_api.mid_rate("USD", date(2026, 11, 20), date(2026, 11, 25))
    jpy = bot_api.mid_rate("JPY", date(2026, 11, 20), date(2026, 11, 25))
    assert [d.date().isoformat() for d in usd["date"]] == ["2026-11-23", "2026-11-25"]
    assert usd["value"].tolist() == [33.9, 33.9925]
    assert jpy["value"].tolist() == [21.3603]
    assert len(calls) == 1, "every currency comes from the same requests"
    assert "currency" not in calls[0]


def test_bot_mid_rates_ask_for_at_most_31_days_at_a_time(monkeypatch):
    periods = []

    def fake(url, params, headers):
        periods.append((date.fromisoformat(params["start_period"]), date.fromisoformat(params["end_period"])))
        return Reply({"result": {"data": {"data_detail": []}}})
    monkeypatch.setenv(bot_api.EXCHANGE_TOKEN, "test-token")
    monkeypatch.setattr(bot_api, "http_get", fake)
    bot_api._mid_rates.cache_clear()
    bot_api.mid_rate("USD", date(2026, 1, 1), date(2026, 3, 15))
    assert all((b - a).days < 31 for a, b in periods), "each request spans 31 days or fewer"
    assert periods[0][0] == date(2026, 1, 1) and periods[-1][1] == date(2026, 3, 15)
    assert all(nxt[0] - prev[1] == timedelta(days=1) for prev, nxt in zip(periods, periods[1:])), "no gaps or overlaps"


def test_bot_statistic_dates_monthly_values_on_the_first_and_applies_the_scale(monkeypatch):
    seen = {}

    def fake(url, params, headers):
        seen.update(params)
        return Reply({"result": {"series": [{"series_code": "X", "observations": [
            {"period_start": "2026-09", "value": "246322.7100000"},
            {"period_start": "2026-08", "value": ""},
            {"period_start": "2026-07", "value": "238090.1100000"},
        ]}]}})
    monkeypatch.setenv(bot_api.STATISTICS_TOKEN, "test-token")
    monkeypatch.setattr(bot_api, "http_get", fake)
    df = bot_api.statistic("X", date(2026, 1, 1), date(2026, 11, 26), scale=1e-3)
    assert [d.date().isoformat() for d in df["date"]] == ["2026-07-01", "2026-09-01"]
    assert df["value"].round(5).tolist() == [238.09011, 246.32271]
    assert seen == {"series_code": "X", "start_period": "2026-01-01", "end_period": "2026-11-26"}


def test_daily_statistics_are_asked_for_a_quarter_at_a_time(monkeypatch):
    periods = []

    def fake(url, params, headers):
        a, b = date.fromisoformat(params["start_period"]), date.fromisoformat(params["end_period"])
        periods.append((a, b))
        return Reply({"result": {"series": [{"observations": [{"period_start": b.isoformat(), "value": "1.0"}]}]}})
    monkeypatch.setenv(bot_api.STATISTICS_TOKEN, "test-token")
    monkeypatch.setattr(bot_api, "http_get", fake)
    thor = next(s for s in series.SERIES if s.id == "thor")
    df = thor.fetch(date(2023, 11, 27), date(2026, 11, 26))
    assert all((b - a).days < bot_api.DAILY_CHUNK_DAYS for a, b in periods)
    assert periods[0][0] == date(2023, 11, 27) and periods[-1][1] == date(2026, 11, 26)
    assert all(nxt[0] - prev[1] == timedelta(days=1) for prev, nxt in zip(periods, periods[1:])), "no gaps or overlaps"
    assert len(df) == len(periods), "rows from every chunk are kept"


def test_bot_statistic_with_no_observations_stops_the_build(monkeypatch, tmp_path):
    monkeypatch.setenv(bot_api.STATISTICS_TOKEN, "test-token")
    monkeypatch.setattr(bot_api, "http_get", lambda url, params, headers: Reply({"result": {"series": []}}))
    with_fetches(monkeypatch, reserves=lambda st, e: bot_api.statistic("X", st, e))
    out = tmp_path / "dashboard.json"
    with pytest.raises(SystemExit, match="no data for reserves"):
        build_data.main(["--out", str(out)])
    assert not out.exists()


def test_policy_rate_carries_the_last_meeting(monkeypatch, tmp_path):
    with_fetches(monkeypatch, meeting=lambda: bot_api.Meeting(date(2026, 10, 28), "คงอัตราไว้ที่ร้อยละ 1.00", "Held at 1.00 percent"))
    out = tmp_path / "dashboard.json"
    build_data.main(["--out", str(out)])
    by_id = {s["id"]: s for s in json.loads(out.read_text(encoding="utf-8"))["series"]}
    assert by_id["policy_rate"]["meeting"] == {
        "date": "2026-10-28", "decision": {"th": "คงอัตราไว้ที่ร้อยละ 1.00", "en": "Held at 1.00 percent"}}
    assert "meeting" not in by_id["usd_thb"]


def test_failing_meeting_source_writes_nothing(monkeypatch, tmp_path):
    def down():
        raise SourceError("HTTP 403")
    with_fetches(monkeypatch, meeting=down)
    out = tmp_path / "dashboard.json"
    with pytest.raises(SystemExit, match="Could not get the last meeting for policy_rate: HTTP 403"):
        build_data.main(["--out", str(out)])
    assert not out.exists()


def test_bot_meeting_is_read_from_the_announcement(monkeypatch):
    def answer(day, th=" คงอัตรา ", en="Held"):
        reply = Reply({"result": {"data": "1.00", "announcement_date": day, "news_text_th": th, "news_text_en": en}})
        monkeypatch.setattr(bot_api, "http_get", lambda url, params, headers: reply)
    monkeypatch.setenv(bot_api.POLICY_TOKEN, "test-token")
    answer("2026/10/28")
    assert bot_api.last_policy_meeting() == bot_api.Meeting(date(2026, 10, 28), "คงอัตรา", "Held")
    answer("28 Oct 2026")
    with pytest.raises(SourceError, match="expected YYYY/MM/DD"):
        bot_api.last_policy_meeting()
    answer("2026/10/28", th="")
    with pytest.raises(SourceError, match="no decision text"):
        bot_api.last_policy_meeting()


def test_bis_policy_rate_starts_two_years_early_even_from_a_leap_day(monkeypatch):
    import sources
    asked = {}

    class Csv:
        text = "TIME_PERIOD,OBS_VALUE\n2026-01-02,1.0\n"

    def fake(url, params, headers=None):
        asked.update(params)
        return Csv()
    monkeypatch.setattr(sources, "http_get", fake)
    sources.bis_policy_rate(date(2028, 2, 29), date(2031, 2, 28))
    assert asked["startPeriod"] <= "2026-02-28"
