"""Refuse to publish a data file that is not live data.

Usage:
    python src/check_live.py web/dist/data/dashboard.json

The 2026-11-16 and 2026-11-23 runs published sample numbers as if they were real. The deploy
job runs this on the file it is about to upload, so sample data cannot reach the site again.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str]) -> None:
    path = Path(argv[0])
    source = json.loads(path.read_text(encoding="utf-8")).get("source")
    if source != "live":
        sys.exit(f"{path} holds {source!r} data. Only live data is published. "
                 "Build it with `python src/build_data.py`, without --sample.")
    print(f"{path} holds live data")


if __name__ == "__main__":
    main(sys.argv[1:])
