"""Offline SAMPLE data so the dashboard renders without an API token.

These numbers are SYNTHETIC and only shaped to look plausible. They are NOT
official Bank of Thailand statistics. The PDF is stamped "SAMPLE DATA" when
they are used.
"""
from datetime import date

import numpy as np
import pandas as pd


def make(start: date, end: date):
    rng = np.random.default_rng(42)
    days = pd.bdate_range(start, end)
    walk = np.cumsum(rng.normal(0, 0.12, len(days)))
    fx = pd.DataFrame({"date": days, "usd_thb": 34.5 + walk - walk.mean()})

    months = pd.date_range(start, end, freq="MS")
    cpi = 0.8 + np.cumsum(rng.normal(0, 0.25, len(months)))
    infl = pd.DataFrame({"date": months, "cpi_yoy": np.clip(cpi, -1.5, 4.0)})

    pr = pd.DataFrame({
        "date": pd.to_datetime([start, start + (end - start) / 3, start + 2 * (end - start) / 3]),
        "policy_rate": [2.50, 2.25, 2.00],
    })
    return fx, infl, pr
