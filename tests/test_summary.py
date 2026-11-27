import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import summary  # noqa: E402


def entry(id: str, group: str, points: list[list], **over) -> dict:
    return {"id": id, "group": group, "name": {"th": "ชื่อ", "en": "Name"}, "sub": {"th": "ย่อย", "en": "sub"},
            "unit": "", "decimals": 2, "frequency": "monthly", "change": "pct",
            "source": {"th": "ที่มา", "en": "Source"}, "points": points, **over}


def line(group: str, *entries: dict) -> dict:
    return summary.lines([group], list(entries))[0]


def usd(points: list[list]) -> dict:
    return entry("usd_thb", "fx", points, frequency="daily")


def rate(points: list[list], meeting_day: str) -> dict:
    return entry("policy_rate", "rate", points, unit="%", change="diff", frequency="event",
                 meeting={"date": meeting_day, "decision": {"th": "มติ", "en": "Decision"}})


def test_a_falling_dollar_rate_reads_as_the_baht_strengthening():
    got = line("fx", usd([["2026-11-18", 34.0], ["2026-11-25", 33.66]]))
    assert got["th"] == "ค่าเงินบาทแข็งค่า 1.00% เทียบดอลลาร์ใน 7 วัน อยู่ที่ 33.66 บาท"
    assert got["en"] == "The baht strengthened 1.00% against the dollar over 7 days, to 33.66."


def test_a_rising_dollar_rate_reads_as_the_baht_weakening():
    got = line("fx", usd([["2026-11-18", 34.0], ["2026-11-25", 34.34]]))
    assert got["th"].startswith("ค่าเงินบาทอ่อนค่า 1.00%")
    assert got["en"] == "The baht weakened 1.00% against the dollar over 7 days, to 34.34."


def test_the_seven_day_comparison_uses_the_last_point_from_a_week_or_more_back():
    got = line("fx", usd([["2026-11-16", 30.0], ["2026-11-18", 34.0], ["2026-11-20", 99.0], ["2026-11-25", 33.66]]))
    assert "1.00%" in got["th"], "the point exactly seven days back, not the nearer or the older one"


def test_a_baht_line_without_the_dollar_stops_the_build():
    with pytest.raises(summary.SummaryError, match="no usd_thb series"):
        line("fx", entry("eur_thb", "fx", [["2026-11-18", 37.0], ["2026-11-25", 37.2]], frequency="daily"))


def test_a_meeting_that_left_the_rate_alone_reads_as_held():
    got = line("rate", rate([["2026-01-01", 1.0], ["2026-10-28", 1.0], ["2026-11-25", 1.0]], "2026-10-28"))
    assert got["th"] == "กนง. คงดอกเบี้ยนโยบายไว้ที่ 1.00% เมื่อ 28 ต.ค. 2569"
    assert got["en"] == "The MPC held the policy rate at 1.00% on 28 Oct 2026."


def test_a_meeting_that_lowered_the_rate_reads_as_a_cut():
    got = line("rate", rate([["2026-01-01", 1.25], ["2026-10-28", 1.0], ["2026-11-25", 1.0]], "2026-10-28"))
    assert got["th"] == "กนง. ลดดอกเบี้ยนโยบายเป็น 1.00% เมื่อ 28 ต.ค. 2569"
    assert got["en"] == "The MPC cut the policy rate to 1.00% on 28 Oct 2026."


def test_a_meeting_that_lifted_the_rate_reads_as_a_rise():
    got = line("rate", rate([["2026-01-01", 1.0], ["2026-10-28", 1.25], ["2026-11-25", 1.25]], "2026-10-28"))
    assert got["th"] == "กนง. ขึ้นดอกเบี้ยนโยบายเป็น 1.25% เมื่อ 28 ต.ค. 2569"
    assert got["en"] == "The MPC raised the policy rate to 1.25% on 28 Oct 2026."


def test_a_rate_line_without_a_meeting_stops_the_build():
    with pytest.raises(summary.SummaryError, match="no series with a meeting"):
        line("rate", entry("thor", "rate", [["2026-11-24", 0.98], ["2026-11-25", 0.99]], unit="%", change="diff"))


def test_a_rate_line_with_no_rate_in_force_before_the_meeting_stops_the_build():
    with pytest.raises(summary.SummaryError, match="no rate in force before its 2026-10-28 meeting"):
        line("rate", rate([["2026-10-28", 1.0], ["2026-11-25", 1.0]], "2026-10-28"))


def test_a_group_line_picks_the_biggest_mover_among_the_series_with_the_newest_month():
    stale = entry("stale", "econ", [["2026-08-01", 100.0], ["2026-09-01", 150.0]],
                  name={"th": "เก่า", "en": "Stale"})
    small = entry("small", "econ", [["2026-09-01", 100.0], ["2026-10-01", 101.0]],
                  name={"th": "ขยับน้อย", "en": "Small"})
    big = entry("big", "econ", [["2026-09-01", 100.0], ["2026-10-01", 94.0]],
                name={"th": "ขยับมาก", "en": "Big"}, decimals=1)
    got = line("econ", stale, small, big)
    assert got["th"] == "ขยับมาก ต.ค. 2569 อยู่ที่ 94.0 ลดลง 6.00% จากเดือนก่อน"
    assert got["en"] == "Big for Oct 2026 was 94.0, down 6.00% from the month before."


def test_a_rate_series_in_a_group_line_shows_points_and_no_percent_sign_on_the_change():
    cpi = entry("cpi_yoy", "infl", [["2026-09-01", 2.82], ["2026-10-01", 3.9]],
                name={"th": "เงินเฟ้อทั่วไป", "en": "Headline CPI"}, unit="%", change="diff")
    got = line("infl", cpi)
    assert got["th"] == "เงินเฟ้อทั่วไป ต.ค. 2569 อยู่ที่ 3.90% เพิ่มขึ้น 1.08 จากเดือนก่อน"
    assert got["en"] == "Headline CPI for Oct 2026 was 3.90%, up 1.08 from the month before."


def test_a_group_line_takes_its_unit_from_the_sub_text():
    reserves = entry("reserves", "ext", [["2026-09-01", 237.9], ["2026-10-01", 236.7]],
                     name={"th": "ทุนสำรองระหว่างประเทศ", "en": "International reserves"}, decimals=1,
                     sub={"th": "เงินตราต่างประเทศ พันล้านดอลลาร์ · รายเดือน", "en": "foreign currency, USD bn · monthly"})
    got = line("ext", reserves)
    assert "อยู่ที่ 236.7 พันล้านดอลลาร์ ลดลง 0.50%" in got["th"]
    assert "was 236.7 USD bn, down 0.50%" in got["en"]


def test_a_group_line_leaves_the_unit_out_when_the_sub_text_names_none():
    sentiment = entry("sentiment", "econ", [["2026-09-01", 48.1], ["2026-10-01", 45.2]], decimals=1,
                      name={"th": "ความเชื่อมั่นภาคธุรกิจ", "en": "Business sentiment"},
                      sub={"th": "ดัชนี 50 คือทรงตัว · รายเดือน", "en": "index, 50 is neutral · monthly"})
    got = line("econ", sentiment)
    assert got["th"] == "ความเชื่อมั่นภาคธุรกิจ ต.ค. 2569 อยู่ที่ 45.2 ลดลง 6.03% จากเดือนก่อน"
    assert got["en"] == "Business sentiment for Oct 2026 was 45.2, down 6.03% from the month before."


def test_groups_come_back_in_the_order_they_are_given_and_an_empty_group_is_skipped():
    got = summary.lines(["fx", "infl", "rate"], [
        usd([["2026-11-18", 34.0], ["2026-11-25", 33.66]]),
        rate([["2026-01-01", 1.0], ["2026-10-28", 1.0], ["2026-11-25", 1.0]], "2026-10-28"),
    ])
    assert [g["group"] for g in got] == ["fx", "rate"]


def test_a_group_with_no_line_of_its_own_stops_the_build():
    with pytest.raises(summary.SummaryError, match="group crypto has no line in src/summary.py"):
        line("crypto", entry("btc", "crypto", [["2026-11-24", 1.0], ["2026-11-25", 2.0]]))


def test_a_group_line_with_no_change_says_unchanged_not_down():
    flat = entry("flat", "econ", [["2026-09-01", 45.2], ["2026-10-01", 45.2]], decimals=1,
                 name={"th": "ความเชื่อมั่นภาคธุรกิจ", "en": "Business sentiment"})
    got = line("econ", flat)
    assert got["th"] == "ความเชื่อมั่นภาคธุรกิจ ต.ค. 2569 อยู่ที่ 45.2 ไม่เปลี่ยนจากเดือนก่อน"
    assert got["en"] == "Business sentiment for Oct 2026 was 45.2, unchanged from the month before."


def test_a_dollar_rate_that_did_not_move_reads_as_the_baht_holding_steady():
    got = line("fx", usd([["2026-11-18", 34.0], ["2026-11-25", 34.0]]))
    assert got["th"] == "ค่าเงินบาททรงตัวเทียบดอลลาร์ใน 7 วัน อยู่ที่ 34.00 บาท"
    assert got["en"] == "The baht held steady against the dollar over 7 days, at 34.00."
