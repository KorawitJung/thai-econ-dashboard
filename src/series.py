"""The indicators the dashboard shows. Add an indicator by adding one Series here."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Literal

import pandas as pd

import sources

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
    source: Text
    fetch: Fetch


GROUPS = [
    Group("fx", Text("ค่าเงินบาท", "Baht")),
    Group("rate", Text("อัตราดอกเบี้ย", "Interest rates")),
    Group("infl", Text("เงินเฟ้อ", "Inflation")),
]

SERIES = [
    Series("usd_thb", "fx", Text("ดอลลาร์สหรัฐ", "US dollar"), Text("USD/THB · รายวัน", "USD/THB · daily"),
           unit="", decimals=2, frequency="daily", max_age_days=7,
           source=Text("อัตราอ้างอิงของธนาคารกลางยุโรป (ECB) ผ่าน Frankfurter", "European Central Bank reference rate via Frankfurter"),
           fetch=sources.frankfurter_usd_thb),
    Series("policy_rate", "rate", Text("ดอกเบี้ยนโยบาย", "Policy rate"), Text("กนง.", "MPC"),
           unit="%", decimals=2, frequency="event", max_age_days=None,
           source=Text("BIS จากข้อมูลของธนาคารแห่งประเทศไทย", "BIS, from Bank of Thailand data"),
           fetch=sources.bis_policy_rate),
    # BIS adds a month's CPI about two months after the month starts, so allow four months.
    Series("cpi_yoy", "infl", Text("เงินเฟ้อทั่วไป", "Headline CPI"), Text("YoY · รายเดือน", "YoY · monthly"),
           unit="%", decimals=2, frequency="monthly", max_age_days=120,
           source=Text("BIS (Consumer prices)", "BIS (Consumer prices)"),
           fetch=sources.bis_cpi_yoy),
]

assert {s.group for s in SERIES} <= {g.id for g in GROUPS}, "every series needs a known group"
assert len({s.id for s in SERIES}) == len(SERIES), "series ids must be unique"
