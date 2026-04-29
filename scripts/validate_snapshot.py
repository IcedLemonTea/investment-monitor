from __future__ import annotations

import argparse
import json
from pathlib import Path

from ibkr_monitor.dashboard.validate import validate_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="public/data/latest.example.json")
    args = parser.parse_args()

    snapshot = json.loads(Path(args.path).read_text(encoding="utf-8"))
    validate_snapshot(snapshot)
    print(f"valid snapshot: {args.path}")


if __name__ == "__main__":
    main()
