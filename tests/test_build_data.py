import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import build_data  # noqa: E402
import series  # noqa: E402
from sources import SourceError  # noqa: E402


def frame(days_ago: list[int], value: float = 1.0) -> pd.DataFrame:
    today = date.today()
    return pd.DataFrame({"date": pd.to_datetime([today - timedelta(days=d) for d in days_ago]), "value": value})


def with_fetches(monkeypatch, **by_id):
    """Point every series at a local fetch so no test touches the network."""
    regs = [series.Series(**{**vars(s), "fetch": by_id.get(s.id, lambda st, e: frame([400, 30, 1]))}) for s in series.SERIES]
    monkeypatch.setattr(build_data, "SERIES", regs)


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
