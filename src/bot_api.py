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

from sources import SourceError, http_get

GATEWAY = "https://gateway.api.bot.or.th"
STATISTICS_TOKEN = "BOT_TOKEN_STATISTICS"  # Statistics product
EXCHANGE_TOKEN = "BOT_TOKEN_EXCHANGE"  # Exchange Rates product
POLICY_TOKEN = "BOT_TOKEN_POLICY"  # Policy Rate product
MAX_DAYS = 31  # the Exchange Rates API refuses longer periods
# Statistics cuts a long daily request short without saying so (3 years came back as 6 months), so ask a quarter at a time.
DAILY_CHUNK_DAYS = 90


@dataclass(frozen=True)
class Meeting:
    day: date
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
    """One series from the Statistics product. Monthly periods ("2026-09") are dated the first of the month."""
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
    return Meeting(day, th, en)
