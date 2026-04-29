from __future__ import annotations

import argparse
import json
from pathlib import Path

from ibkr_monitor.dashboard.build import write_mock_poll_once


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write one local dashboard snapshot.")
    parser.add_argument("--source", choices=["mock", "flex", "gateway"], default="mock")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("public/data"),
        help="Directory where latest.json and health.json are written.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.source != "mock":
        raise SystemExit("Live IBKR polling is not implemented. Use --source mock.")

    result = write_mock_poll_once(args.data_dir)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
