"""The indicators the dashboard shows. Add an indicator by adding one Series here."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Literal

import pandas as pd

import bot_api

Frequency = Literal["daily", "monthly", "event"]
Fetch = Callable[[date, date], pd.DataFrame]  # returns columns: date, value


@dataclass(frozen=True)
class Text:
    th: str
    en: str


@dataclass(frozen=True)
class Group:
    id: str
    name: Text


@dataclass(frozen=True)
class Series:
    id: str
    group: str
    name: Text
    sub: Text
    unit: str
    decimals: int
    frequency: Frequency
    max_age_days: int | None  # None: changes only on decisions, so an old last value is normal
    fetch: Fetch


GROUPS = [
    Group("fx", Text("ค่าเงินบาท", "Baht")),
    Group("rate", Text("อัตราดอกเบี้ย", "Interest rates")),
    Group("infl", Text("เงินเฟ้อ", "Inflation")),
]

SERIES = [
    Series("usd_thb", "fx", Text("ดอลลาร์สหรัฐ", "US dollar"), Text("USD/THB · รายวัน", "USD/THB · daily"),
           unit="", decimals=2, frequency="daily", max_age_days=7, fetch=bot_api.exchange_rate),
    Series("policy_rate", "rate", Text("ดอกเบี้ยนโยบาย", "Policy rate"), Text("กนง.", "MPC"),
           unit="%", decimals=2, frequency="event", max_age_days=None, fetch=bot_api.policy_rate),
    # CPI for a month is published early the next month and dated to the month's first day.
    Series("cpi_yoy", "infl", Text("เงินเฟ้อทั่วไป", "Headline CPI"), Text("YoY · รายเดือน", "YoY · monthly"),
           unit="%", decimals=2, frequency="monthly", max_age_days=95, fetch=bot_api.inflation),
]

assert {s.group for s in SERIES} <= {g.id for g in GROUPS}, "every series needs a known group"
assert len({s.id for s in SERIES}) == len(SERIES), "series ids must be unique"
