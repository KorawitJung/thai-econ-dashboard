"""Offline SAMPLE data so the dashboard builds without an API token.

These numbers are SYNTHETIC and only shaped to look plausible. They are NOT
official Bank of Thailand statistics. The dashboard labels them as sample data.
"""
from __future__ import annotations

import zlib
from datetime import date

import numpy as np
import pandas as pd

from series import Series

SHAPES = {
    "daily": {"usd_thb": (32.74, 0.12)},
    "monthly": {"cpi_yoy": (0.77, 0.25)},
}


def make(series: Series, start: date, end: date) -> pd.DataFrame:
    if series.frequency == "event":
        dates = pd.to_datetime([start, start + (end - start) / 3, start + 2 * (end - start) / 3])
        return pd.DataFrame({"date": dates, "value": [2.50, 2.25, 2.00]})
    rng = np.random.default_rng(zlib.crc32(series.id.encode()))
    last, step = SHAPES[series.frequency][series.id]
    dates = pd.bdate_range(start, end) if series.frequency == "daily" else pd.date_range(start, end, freq="MS")
    walk = np.cumsum(rng.normal(0, step, len(dates)))
    return pd.DataFrame({"date": dates, "value": walk - walk[-1] + last})
