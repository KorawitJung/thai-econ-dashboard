"""One sentence per group for the dashboard's summary card.

Every line reads the series dicts `build_data.build()` writes, so a sample build and a live build
take the same path. A group whose line cannot be written stops the build instead of going missing.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Callable

Entry = dict  # one series as build_data.build() writes it
Line = Callable[[list[Entry]], tuple[str, str]]


class SummaryError(Exception):
    """A group's line cannot be written from the series the build has."""


THAI_MONTHS = ("ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.")
EN_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
# Thai writes years in the Buddhist era. Spelling the months out keeps the build off a Thai locale,
# which a CI runner does not have.
BE_OFFSET = 543
WEEK = timedelta(days=7)
MONEY_TH = re.compile(r"\S*ล้าน\S*")
MONEY_EN = re.compile(r"USD bn|million \S+")


def thai_month(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{THAI_MONTHS[d.month - 1]} {d.year + BE_OFFSET}"


def thai_day(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{d.day} {THAI_MONTHS[d.month - 1]} {d.year + BE_OFFSET}"


def en_month(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{EN_MONTHS[d.month - 1]} {d.year}"


def en_day(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{d.day} {EN_MONTHS[d.month - 1]} {d.year}"


def value_of(entry: Entry, v: float) -> str:
    return f"{v:.{entry['decimals']}f}"


def latest_change(entry: Entry) -> tuple[float, str]:
    before, now = entry["points"][-2][1], entry["points"][-1][1]
    if entry["change"] == "diff":
        return now - before, "diff"
    return (now / before - 1) * 100, "pct"


def unit_of(entry: Entry, lang: str) -> str:
    if entry["unit"] == "%":
        return "%"
    found = (MONEY_TH if lang == "th" else MONEY_EN).search(entry["sub"][lang])
    return f" {found.group()}" if found else entry["unit"]


def baht(entries: list[Entry]) -> tuple[str, str]:
    usd = next((e for e in entries if e["id"] == "usd_thb"), None)
    if usd is None:
        raise SummaryError("the fx group has no usd_thb series, so the baht has nothing to move against")
    day, now = usd["points"][-1]
    week_ago = (date.fromisoformat(day) - WEEK).isoformat()
    earlier = [p for p in usd["points"] if p[0] <= week_ago]
    if not earlier:
        raise SummaryError(f"usd_thb has no point on or before {week_ago}, so a seven day change means nothing")
    pct = (now / earlier[-1][1] - 1) * 100
    strong = pct < 0
    level, amount = value_of(usd, now), f"{abs(pct):.2f}"
    if amount == "0.00":
        return (f"ค่าเงินบาททรงตัวเทียบดอลลาร์ใน 7 วัน อยู่ที่ {level} บาท",
                f"The baht held steady against the dollar over 7 days, at {level}.")
    return (f"ค่าเงินบาท{'แข็งค่า' if strong else 'อ่อนค่า'} {amount}% เทียบดอลลาร์ใน 7 วัน อยู่ที่ {level} บาท",
            f"The baht {'strengthened' if strong else 'weakened'} {amount}% against the dollar over 7 days, "
            f"to {level}.")


def policy(entries: list[Entry]) -> tuple[str, str]:
    rate = next((e for e in entries if "meeting" in e), None)
    if rate is None:
        raise SummaryError("the rate group has no series with a meeting, so there is no decision to report")
    day = rate["meeting"]["date"]
    before = [p for p in rate["points"] if p[0] < day]
    if not before:
        raise SummaryError(f"{rate['id']} has no rate in force before its {day} meeting")
    now = rate["points"][-1][1]
    moved = now - before[-1][1]
    verb_th = "คงดอกเบี้ยนโยบายไว้ที่" if moved == 0 else "ลดดอกเบี้ยนโยบายเป็น" if moved < 0 else "ขึ้นดอกเบี้ยนโยบายเป็น"
    verb_en = ("held the policy rate at" if moved == 0 else
               "cut the policy rate to" if moved < 0 else "raised the policy rate to")
    level = value_of(rate, now) + rate["unit"]
    return (f"กนง. {verb_th} {level} เมื่อ {thai_day(day)}",
            f"The MPC {verb_en} {level} on {en_day(day)}.")


def biggest_mover(entries: list[Entry]) -> tuple[str, str]:
    newest = max(e["points"][-1][0] for e in entries)
    pick = max((e for e in entries if e["points"][-1][0] == newest), key=lambda e: abs(latest_change(e)[0]))
    moved, kind = latest_change(pick)
    day, now = pick["points"][-1]
    level, amount = value_of(pick, now), f"{abs(moved):.2f}" + ("%" if kind == "pct" else "")
    up = moved > 0
    if amount.rstrip("%") == "0.00":
        return (f"{pick['name']['th']} {thai_month(day)} อยู่ที่ {level}{unit_of(pick, 'th')} ไม่เปลี่ยนจากเดือนก่อน",
                f"{pick['name']['en']} for {en_month(day)} was {level}{unit_of(pick, 'en')}, "
                "unchanged from the month before.")
    return (f"{pick['name']['th']} {thai_month(day)} อยู่ที่ {level}{unit_of(pick, 'th')} "
            f"{'เพิ่มขึ้น' if up else 'ลดลง'} {amount} จากเดือนก่อน",
            f"{pick['name']['en']} for {en_month(day)} was {level}{unit_of(pick, 'en')}, "
            f"{'up' if up else 'down'} {amount} from the month before.")


LINES: dict[str, Line] = {
    "fx": baht,
    "rate": policy,
    "infl": biggest_mover,
    "econ": biggest_mover,
    "ext": biggest_mover,
}


def lines(group_ids: list[str], series: list[Entry]) -> list[dict]:
    """One line per group that has series, in the order the groups are given."""
    out = []
    for group in group_ids:
        entries = [e for e in series if e["group"] == group]
        if not entries:
            continue
        write = LINES.get(group)
        if write is None:
            raise SummaryError(f"group {group} has no line in src/summary.py")
        th, en = write(entries)
        out.append({"group": group, "th": th, "en": en})
    return out
