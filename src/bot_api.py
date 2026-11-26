"""Bank of Thailand API Portal (https://portal.api.bot.or.th).

Each portal app gets its own token and subscribes to one product, so every
product reads its token from its own environment variable.
"""
from __future__ import annotations

import os
from datetime import date, timedelta

import pandas as pd

from sources import SourceError, http_get

GATEWAY = "https://gateway.api.bot.or.th"
EXCHANGE_TOKEN = "BOT_TOKEN_EXCHANGE"  # Exchange Rates product
MAX_DAYS = 31  # the Exchange Rates API refuses longer periods


def _token(env: str) -> str:
    token = os.getenv(env, "").strip()
    if not token:
        raise SourceError(f"{env} is not set. It holds the BOT API token for this product.")
    return token


def usd_thb(start: date, end: date) -> pd.DataFrame:
    """Daily average USD mid rate, in baht per dollar."""
    headers = {"Authorization": _token(EXCHANGE_TOKEN), "accept": "application/json"}
    rows = []
    while start <= end:
        stop = min(start + timedelta(days=MAX_DAYS - 1), end)
        js = http_get(f"{GATEWAY}/Stat-ExchangeRate/v2/DAILY_AVG_EXG_RATE/",
                      {"start_period": start.isoformat(), "end_period": stop.isoformat(), "currency": "USD"},
                      headers).json()
        rows += js["result"]["data"]["data_detail"]
        start = stop + timedelta(days=1)
    df = pd.DataFrame(rows, columns=["period", "mid_rate"])
    return pd.DataFrame({
        "date": pd.to_datetime(df["period"]),
        "value": pd.to_numeric(df["mid_rate"], errors="coerce"),
    }).dropna().sort_values("date")
