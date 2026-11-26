"""Fetch every series in the registry and write the dashboard's data file.

Usage:
    python src/build_data.py                 # live data from the sources in src/series.py
    python src/build_data.py --sample        # synthetic data, labelled as sample
    python src/build_data.py --out path.json # default: web/public/data/dashboard.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import sample_data  # noqa: E402
from series import GROUPS, MONTHLY_MAX_AGE, SERIES, Series  # noqa: E402
from bot_api import Meeting  # noqa: E402
from sources import SourceError  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "web" / "public" / "data" / "dashboard.json"
YEARS = 3
BANGKOK = timezone(timedelta(hours=7))
# The widest gap between two points that real data has. Thai holidays leave up to a week without
# exchange rates. A wider gap means a request came back short, as BOT Statistics did once.
MAX_GAP_DAYS = {"daily": 14, "monthly": 62}


def fetch_real(series: Series, start: date, end: date) -> pd.DataFrame:
    try:
        df = series.fetch(start, end)
    except SourceError as e:
        sys.exit(f"Could not get {series.id}: {e}\n"
                 "Nothing was written. Use --sample to build from synthetic data.")
    if df.empty:
        sys.exit(f"The source returned no data for {series.id}. Nothing was written.")
    latest = df["date"].max().date()
    if series.max_age_days is not None and (end - latest).days > series.max_age_days:
        sys.exit(f"The newest {series.id} value is from {latest}, more than {series.max_age_days} days ago. "
                 "Nothing was written.")
    if series.frequency in MAX_GAP_DAYS:
        dates = df.loc[df["date"] >= pd.Timestamp(start), "date"].sort_values()
        gaps = dates.diff()
        if len(gaps) > 1 and gaps.max().days > MAX_GAP_DAYS[series.frequency]:
            after = dates[gaps.idxmax()].date()
            sys.exit(f"{series.id} has no data for {gaps.max().days} days before {after}, more than the "
                     f"{MAX_GAP_DAYS[series.frequency]} a {series.frequency} series allows. A request may have come back "
                     "short. Fetch BOT ranges through bot_api.periods(). Nothing was written.")
    if series.change == "pct" and (df["value"] <= 0).any():
        sys.exit(f"{series.id} has values at or below zero, so a percent change means nothing. "
                 "Set change=\"diff\" in src/series.py. Nothing was written.")
    return df


def fetch_meeting(series: Series) -> Meeting:
    try:
        return series.meeting()
    except SourceError as e:
        sys.exit(f"Could not get the last meeting for {series.id}: {e}\n"
                 "Nothing was written. Use --sample to build from synthetic data.")


def points(series: Series, df: pd.DataFrame, start: date, end: date) -> list[list]:
    df = df.sort_values("date").drop_duplicates("date", keep="last")
    if series.frequency == "event":
        # Keep only the days the rate changed. A decision stays in force until the next one,
        # so carry the value in force at `start` and extend it to `end`.
        df = df[df["value"].ne(df["value"].shift())]
        before = df[df["date"] <= pd.Timestamp(start)]
        df = df[df["date"] > pd.Timestamp(start)]
        if not before.empty:
            df = pd.concat([pd.DataFrame({"date": [pd.Timestamp(start)], "value": [before["value"].iloc[-1]]}), df])
        if df["date"].iloc[-1] < pd.Timestamp(end):
            df = pd.concat([df, pd.DataFrame({"date": [pd.Timestamp(end)], "value": [df["value"].iloc[-1]]})])
    else:
        df = df[df["date"] >= pd.Timestamp(start)]
    return [[d.date().isoformat(), round(float(v), series.decimals + 2)] for d, v in zip(df["date"], df["value"])]


def build(sample: bool, today: date) -> dict:
    # The page's widest range is 3Y back from each series' newest point, and a monthly point may be
    # MONTHLY_MAX_AGE days old, so keep that much more history.
    start = today - timedelta(days=365 * YEARS + MONTHLY_MAX_AGE)
    out = []
    for s in SERIES:
        df = sample_data.make(s, start, today) if sample else fetch_real(s, start, today)
        entry = {
            "id": s.id, "group": s.group, "name": vars(s.name), "sub": vars(s.sub),
            "unit": s.unit, "decimals": s.decimals, "frequency": s.frequency, "change": s.change,
            "source": vars(s.source),
            "points": points(s, df, start, today),
        }
        if s.meeting:
            m = sample_data.meeting(df) if sample else fetch_meeting(s)
            entry["meeting"] = {"date": m.day.isoformat(), "decision": {"th": m.decision_th, "en": m.decision_en}}
        out.append(entry)
    return {
        "generated": datetime.now(BANGKOK).isoformat(timespec="seconds"),
        "source": "sample" if sample else "live",
        "groups": [{"id": g.id, "name": vars(g.name)} for g in GROUPS],
        "series": out,
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="use synthetic sample data")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    payload = build(args.sample, date.today())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(payload['series'])} series to {args.out} [{payload['source']}]")


if __name__ == "__main__":
    main()
