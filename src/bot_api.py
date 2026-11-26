"""Bank of Thailand API Portal (https://portal.api.bot.or.th).

Each portal app gets its own token and subscribes to one product, so every
product reads its token from its own environment variable.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import cache

import pandas as pd

from sources import SourceError, bis_policy_rate, http_get

GATEWAY = "https://gateway.api.bot.or.th"
STATISTICS_TOKEN = "BOT_TOKEN_STATISTICS"  # Statistics product
EXCHANGE_TOKEN = "BOT_TOKEN_EXCHANGE"  # Exchange Rates product
POLICY_TOKEN = "BOT_TOKEN_POLICY"  # Policy Rate product
MAX_DAYS = 31  # the Exchange Rates API refuses longer periods
# Statistics returns only about six months of a longer daily request and reports no error, so ask for 90 days at a time.
DAILY_CHUNK_DAYS = 90


@dataclass(frozen=True)
class Meeting:
    day: date
    rate: float
    decision_th: str
    decision_en: str


def _headers(env: str) -> dict[str, str]:
    token = os.getenv(env, "").strip()
    if not token:
        raise SourceError(f"{env} is not set. It holds the BOT API token for this product.")
    return {"Authorization": token, "accept": "application/json"}


@cache
def _mid_rates(start: date, end: date) -> pd.DataFrame:
    """Daily average mid rates of every currency BOT publishes, one request per 31 days."""
    headers = _headers(EXCHANGE_TOKEN)
    rows = []
    while start <= end:
        stop = min(start + timedelta(days=MAX_DAYS - 1), end)
        js = http_get(f"{GATEWAY}/Stat-ExchangeRate/v2/DAILY_AVG_EXG_RATE/",
                      {"start_period": start.isoformat(), "end_period": stop.isoformat()}, headers).json()
        rows += js["result"]["data"]["data_detail"]
        start = stop + timedelta(days=1)
    df = pd.DataFrame(rows, columns=["period", "currency_id", "mid_rate"])
    return pd.DataFrame({
        "date": pd.to_datetime(df["period"]),
        "currency": df["currency_id"].str.strip(),
        "value": pd.to_numeric(df["mid_rate"], errors="coerce"),
    }).dropna().sort_values("date")


def mid_rate(currency: str, start: date, end: date) -> pd.DataFrame:
    """Baht per unit of `currency` (per 100 yen for JPY), daily average mid rate."""
    df = _mid_rates(start, end)
    return df.loc[df["currency"] == currency, ["date", "value"]].reset_index(drop=True)


def statistic(code: str, start: date, end: date, scale: float = 1.0, chunk_days: int | None = None) -> pd.DataFrame:
    """One series from the Statistics product. A monthly period such as "2026-09" gets the first day of the month as its date."""
    headers = _headers(STATISTICS_TOKEN)
    rows = []
    while start <= end:
        stop = min(start + timedelta(days=chunk_days - 1), end) if chunk_days else end
        js = http_get(f"{GATEWAY}/observations/",
                      {"series_code": code, "start_period": start.isoformat(), "end_period": stop.isoformat()}, headers).json()
        found = js.get("result", {}).get("series") or [{}]
        rows += found[0].get("observations") or []
        start = stop + timedelta(days=1)
    obs = pd.DataFrame(rows, columns=["period_start", "value"])
    return pd.DataFrame({
        "date": pd.to_datetime(obs["period_start"], format="mixed"),
        "value": pd.to_numeric(obs["value"], errors="coerce") * scale,
    }).dropna().sort_values("date").reset_index(drop=True)


@cache
def last_policy_meeting() -> Meeting:
    """The latest MPC decision, whether the rate changed or not."""
    js = http_get(f"{GATEWAY}/PolicyRate/v3/policy_rate", {}, _headers(POLICY_TOKEN)).json()
    result = js.get("result", {})
    raw = result.get("announcement_date")
    try:
        day = datetime.strptime(raw, "%Y/%m/%d").date()
    except (TypeError, ValueError):
        raise SourceError(f"Policy Rate announcement_date is {raw!r}, expected YYYY/MM/DD") from None
    th, en = (result.get(k, "").strip() for k in ("news_text_th", "news_text_en"))
    if not th or not en:
        raise SourceError("Policy Rate has no decision text in news_text_th and news_text_en")
    try:
        rate = float(result.get("data"))
    except (TypeError, ValueError):
        raise SourceError(f"Policy Rate data is {result.get('data')!r}, expected a number") from None
    return Meeting(day, rate, th, en)


def policy_rate(start: date, end: date) -> pd.DataFrame:
    """BIS history of the policy rate, ending with the rate BOT set at its latest meeting.

    BIS publishes a change days after the MPC announces it. Without BOT's rate, the chart
    could show the old rate beside a decision that changed it.
    """
    m = last_policy_meeting()
    df = bis_policy_rate(start, end)
    df = df[df["date"] < pd.Timestamp(m.day)]
    return pd.concat([df, pd.DataFrame({"date": [pd.Timestamp(m.day)], "value": [m.rate]})], ignore_index=True)
