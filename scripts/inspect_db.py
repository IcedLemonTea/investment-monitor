from __future__ import annotations

import argparse
import json
from pathlib import Path

from ibkr_monitor.storage.sqlite_store import table_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("runtime/data/private/monitor.sqlite3"))
    args = parser.parse_args()
    print(json.dumps(table_counts(args.db), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
