"""Thin client for the Bank of Thailand (BOT) API Portal.

Get a free token at https://portal.api.bot.or.th and set it as the
BOT_API_TOKEN environment variable. Endpoint paths can be overridden with
environment variables in case BOT changes versions.
"""
from __future__ import annotations

import os
from datetime import date

import pandas as pd
import requests

from sources import SourceError

GATEWAY = os.getenv("BOT_GATEWAY", "https://gateway.api.bot.or.th")
EXG_PATH = os.getenv("BOT_EXG_PATH", "/Stat-ExchangeRate/v2/DAILY_AVG_EXG_RATE/")
OBS_PATH = os.getenv("BOT_OBS_PATH", "/observations/")
CPI_SERIES = os.getenv("BOT_CPI_SERIES", "EIMEPIM00001")  # headline CPI YoY (override if needed)


class BotApiError(SourceError):
    pass


def _get(path: str, params: dict) -> dict:
    token = os.getenv("BOT_API_TOKEN")
    if not token:
        raise BotApiError("BOT_API_TOKEN is not set")
    r = requests.get(
        GATEWAY + path,
        params=params,
        headers={"Authorization": token, "accept": "application/json"},
        timeout=30,
    )
    if r.status_code != 200:
        raise BotApiError(f"{path} -> HTTP {r.status_code}: {r.text[:200]}")
    return r.json()


def exchange_rate(start: date, end: date, currency: str = "USD") -> pd.DataFrame:
    js = _get(EXG_PATH, {"start_period": start.isoformat(), "end_period": end.isoformat(), "currency": currency})
    rows = js["result"]["data"]["data_detail"]
    df = pd.DataFrame(rows)
    df = df[df["mid_rate"].astype(str).str.strip() != ""]
    return pd.DataFrame({
        "date": pd.to_datetime(df["period"]),
        "value": pd.to_numeric(df["mid_rate"], errors="coerce"),
    }).dropna().sort_values("date")


def inflation(start: date, end: date) -> pd.DataFrame:
    js = _get(OBS_PATH, {"series_code": CPI_SERIES, "start_period": start.isoformat(), "end_period": end.isoformat()})
    obs = js["result"]["series"][0]["observations"]
    df = pd.DataFrame(obs)
    return pd.DataFrame({
        "date": pd.to_datetime(df["period_start"]),
        "value": pd.to_numeric(df["value"], errors="coerce"),
    }).dropna().sort_values("date")
