"""The indicators the dashboard shows. Add an indicator by adding one Series here."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import partial
from typing import Callable, Literal

import pandas as pd

import bot_api
import sources

Frequency = Literal["daily", "monthly", "event"]
Change = Literal["pct", "diff"]  # pct: percent change of a level. diff: plain difference, for rates and balances.
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
    change: Change = "pct"
    meeting: Callable[[], bot_api.Meeting] | None = None  # event series: the latest decision meeting


GROUPS = [
    Group("fx", Text("ค่าเงินบาท", "Baht")),
    Group("rate", Text("อัตราดอกเบี้ย", "Interest rates")),
    Group("infl", Text("เงินเฟ้อ", "Inflation")),
    Group("econ", Text("เศรษฐกิจในประเทศ", "Domestic economy")),
    Group("ext", Text("ภาคต่างประเทศ", "External sector")),
]

FX_SOURCE = Text("ธนาคารแห่งประเทศไทย อัตราแลกเปลี่ยนเฉลี่ย (อัตรากลาง)", "Bank of Thailand, daily average mid rate")
# BOT publishes most monthly statistics one to three months after the month, dated the month's first day.
MONTHLY_MAX_AGE = 150


def fx(id: str, currency: str, th: str, en: str, sub_th: str, sub_en: str) -> Series:
    return Series(id, "fx", Text(th, en), Text(f"{sub_th} · รายวัน", f"{sub_en} · daily"), unit="", decimals=2,
                  frequency="daily", max_age_days=7, source=FX_SOURCE, fetch=partial(bot_api.mid_rate, currency))


def stat(id: str, group: str, code: str, name: Text, sub: Text, *, unit: str = "", decimals: int = 1,
         frequency: Frequency = "monthly", scale: float = 1.0, change: Change = "pct") -> Series:
    return Series(id, group, name, sub, unit=unit, decimals=decimals, frequency=frequency,
                  max_age_days=7 if frequency == "daily" else MONTHLY_MAX_AGE,
                  source=Text(f"ธนาคารแห่งประเทศไทย ชุดข้อมูล {code}", f"Bank of Thailand, series {code}"),
                  fetch=partial(bot_api.statistic, code, scale=scale,
                                chunk_days=bot_api.DAILY_CHUNK_DAYS if frequency == "daily" else None),
                  change=change)


SERIES = [
    fx("usd_thb", "USD", "ดอลลาร์สหรัฐ", "US dollar", "USD/THB", "USD/THB"),
    fx("eur_thb", "EUR", "ยูโร", "Euro", "EUR/THB", "EUR/THB"),
    fx("jpy_thb", "JPY", "เยน", "Japanese yen", "บาทต่อ 100 เยน", "THB per 100 JPY"),
    fx("cny_thb", "CNY", "หยวน", "Chinese yuan", "CNY/THB", "CNY/THB"),
    fx("gbp_thb", "GBP", "ปอนด์สเตอร์ลิง", "Pound sterling", "GBP/THB", "GBP/THB"),
    stat("neer", "fx", "EINEERM00071", Text("ดัชนีค่าเงินบาท", "Baht index (NEER)"),
         Text("เทียบคู่ค้า ยิ่งสูงบาทยิ่งแข็ง · รายเดือน", "vs trading partners, higher is stronger · monthly"), decimals=2),

    Series("policy_rate", "rate", Text("ดอกเบี้ยนโยบาย", "Policy rate"), Text("กนง.", "MPC"),
           unit="%", decimals=2, frequency="event", max_age_days=None, change="diff",
           source=Text("BIS จากข้อมูลของธนาคารแห่งประเทศไทย", "BIS, from Bank of Thailand data"),
           fetch=sources.bis_policy_rate, meeting=bot_api.last_policy_meeting),
    stat("thor", "rate", "FMRTTHORD00003", Text("ดอกเบี้ยข้ามคืน THOR", "THOR overnight rate"),
         Text("รายวัน", "daily"), unit="%", decimals=2, frequency="daily", change="diff"),
    stat("bond_10y", "rate", "FMRTINTM00296", Text("พันธบัตรรัฐบาล 10 ปี", "10-year government bond"),
         Text("อัตราผลตอบแทน · รายเดือน", "yield · monthly"), unit="%", decimals=2, change="diff"),

    # BIS adds a month's CPI about two months after the month starts, so allow four months.
    Series("cpi_yoy", "infl", Text("เงินเฟ้อทั่วไป", "Headline CPI"), Text("YoY · รายเดือน", "YoY · monthly"),
           unit="%", decimals=2, frequency="monthly", max_age_days=120, change="diff",
           source=Text("BIS (Consumer prices)", "BIS (Consumer prices)"),
           fetch=sources.bis_cpi_yoy),

    stat("consumption", "econ", "EIPCIM00063", Text("การบริโภคภาคเอกชน", "Private consumption"),
         Text("ดัชนี ปรับฤดูกาล · รายเดือน", "index, seasonally adjusted · monthly")),
    stat("investment", "econ", "EIPIIM00061", Text("การลงทุนภาคเอกชน", "Private investment"),
         Text("ดัชนี ปรับฤดูกาล · รายเดือน", "index, seasonally adjusted · monthly")),
    stat("manufacturing", "econ", "RGNRMPIM00002", Text("การผลิตอุตสาหกรรม", "Manufacturing output"),
         Text("ดัชนี ปรับฤดูกาล · รายเดือน", "index, seasonally adjusted · monthly")),
    stat("sentiment", "econ", "EIBSIM00057", Text("ความเชื่อมั่นภาคธุรกิจ", "Business sentiment"),
         Text("ดัชนี 50 คือทรงตัว · รายเดือน", "index, 50 is neutral · monthly")),
    stat("unemployment", "econ", "RLLFSWKM00079", Text("อัตราการว่างงาน", "Unemployment rate"),
         Text("รายเดือน", "monthly"), unit="%", decimals=2, change="diff"),
    stat("tourists", "econ", "EITOURISTM00267", Text("นักท่องเที่ยวต่างชาติ", "Foreign tourists"),
         Text("ล้านคน · รายเดือน", "million people · monthly"), decimals=2, scale=1e-3),

    stat("exports", "ext", "XTBOP0OVL0M15593", Text("มูลค่าส่งออก", "Exports"),
         Text("พันล้านดอลลาร์ · รายเดือน", "USD bn · monthly"), scale=1e-3),
    stat("trade_balance", "ext", "XTBOP0OVL0M15595", Text("ดุลการค้า", "Trade balance"),
         Text("พันล้านดอลลาร์ · รายเดือน", "USD bn · monthly"), decimals=2, scale=1e-3, change="diff"),
    stat("current_account", "ext", "XTBOP0OVL0M15597", Text("ดุลบัญชีเดินสะพัด", "Current account"),
         Text("พันล้านดอลลาร์ · รายเดือน", "USD bn · monthly"), decimals=2, scale=1e-3, change="diff"),
    stat("reserves", "ext", "XTRSV00000M00697", Text("ทุนสำรองระหว่างประเทศ", "International reserves"),
         Text("เงินตราต่างประเทศ พันล้านดอลลาร์ · รายเดือน", "foreign currency, USD bn · monthly"), scale=1e-3),
]

assert {s.group for s in SERIES} <= {g.id for g in GROUPS}, "every series needs a known group"
assert len({s.id for s in SERIES}) == len(SERIES), "series ids must be unique"
assert all(s.change == "diff" for s in SERIES if s.unit == "%"), "a percent change of a rate means nothing"
