"""Offline SAMPLE data so the dashboard builds without an API token.

These numbers are SYNTHETIC and only shaped to look plausible. They are NOT
official Bank of Thailand statistics. The dashboard labels them as sample data.
"""
from __future__ import annotations

import zlib
from datetime import date

import numpy as np
import pandas as pd

from bot_api import Meeting
from series import Series

# Last value and the size of one random step, per series.
SHAPES = {
    "usd_thb": (32.74, 0.12), "eur_thb": (37.2, 0.15), "jpy_thb": (21.4, 0.1), "cny_thb": (5.1, 0.02),
    "gbp_thb": (44.5, 0.18), "neer": (128.0, 0.8), "thor": (0.99, 0.01), "bond_10y": (1.9, 0.08),
    "cpi_yoy": (0.77, 0.25), "consumption": (160.0, 1.0), "investment": (105.0, 1.5),
    "manufacturing": (98.0, 1.2), "sentiment": (48.0, 1.0), "unemployment": (0.9, 0.05), "tourists": (2.6, 0.2),
    "exports": (27.0, 1.2), "trade_balance": (1.2, 0.8), "current_account": (1.5, 1.0), "reserves": (245.0, 2.0),
}


def make(series: Series, start: date, end: date) -> pd.DataFrame:
    if series.frequency == "event":
        dates = pd.to_datetime([start, start + (end - start) / 3, start + 2 * (end - start) / 3])
        return pd.DataFrame({"date": dates, "value": [2.50, 2.25, 2.00]})
    rng = np.random.default_rng(zlib.crc32(series.id.encode()))
    last, step = SHAPES[series.id]
    dates = pd.bdate_range(start, end) if series.frequency == "daily" else pd.date_range(start, end, freq="MS")
    walk = np.cumsum(rng.normal(0, step, len(dates)))
    return pd.DataFrame({"date": dates, "value": walk - walk[-1] + last})


def meeting(df: pd.DataFrame) -> Meeting:
    return Meeting(df["date"].max().date(), "ข้อมูลตัวอย่าง ไม่ใช่มติจริงของ กนง.", "Sample data, not a real MPC decision.")
