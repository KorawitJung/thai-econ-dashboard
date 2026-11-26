"""Free data sources that need no API key, and the HTTP helper every source uses.

The BIS Data Portal republishes the Bank of Thailand's policy rate and Thailand's CPI.
"""
from __future__ import annotations

import io
from datetime import date, timedelta

import pandas as pd
import requests

BIS = "https://stats.bis.org/api/v2/data/dataflow/BIS"


class SourceError(RuntimeError):
    pass


def http_get(url: str, params: dict, headers: dict | None = None) -> requests.Response:
    try:
        r = requests.get(url, params=params, headers=headers, timeout=60)
    except requests.RequestException as e:
        raise SourceError(f"{url} -> {e}") from e
    if r.status_code != 200:
        raise SourceError(f"{url} -> HTTP {r.status_code}: {r.text[:200]}")
    return r


def _bis(flow: str, key: str, start: str) -> pd.DataFrame:
    r = http_get(f"{BIS}/{flow}/1.0/{key}", {"startPeriod": start, "format": "csv"}, {"Accept": "text/csv"})
    df = pd.read_csv(io.StringIO(r.text), usecols=["TIME_PERIOD", "OBS_VALUE"])
    return pd.DataFrame({
        "date": pd.to_datetime(df["TIME_PERIOD"]),
        "value": pd.to_numeric(df["OBS_VALUE"], errors="coerce"),
    }).dropna().sort_values("date")


def bis_policy_rate(start: date, end: date) -> pd.DataFrame:
    # Start two years early so the decision in force at `start` is in the data.
    # Subtract days, not years: date.replace(year=...) fails when start is 29 February.
    return _bis("WS_CBPOL", "D.TH", (start - timedelta(days=731)).isoformat())


def bis_cpi_yoy(start: date, end: date) -> pd.DataFrame:
    # Unit 771: percentage change on the same month a year earlier.
    return _bis("WS_LONG_CPI", "M.TH.771", start.strftime("%Y-%m"))
