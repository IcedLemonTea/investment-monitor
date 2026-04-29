from __future__ import annotations

import argparse
import json
from pathlib import Path

from ibkr_monitor.common.env import load_dotenv, require_env
from ibkr_monitor.dashboard.build import write_mock_poll_once
from ibkr_monitor.dashboard.server import serve_dashboard
from ibkr_monitor.ibkr.flex import fetch_flex_report, parse_flex_xml, save_flex_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ibkr-monitor")
    subparsers = parser.add_subparsers(dest="command")

    poll = subparsers.add_parser("poll", help="Poll one snapshot. Mock only in v0.")
    poll.add_argument("--source", choices=["mock", "flex", "gateway"], default="mock")
    poll.add_argument("--data-dir", type=Path, default=Path("public/data"))

    flex = subparsers.add_parser("flex", help="Flex Web Service commands.")
    flex_sub = flex.add_subparsers(dest="flex_command")
    flex_test = flex_sub.add_parser("test-fetch", help="Fetch and parse one Flex report.")
    flex_test.add_argument("--output-dir", type=Path, default=Path("runtime/data/private/flex"))

    loop = subparsers.add_parser("poll-loop", help="Poll repeatedly. Not implemented in v0.")
    loop.add_argument("--source", choices=["mock", "gateway"], default="mock")
    loop.add_argument("--interval", type=int, default=3600)

    dashboard = subparsers.add_parser("dashboard", help="Dashboard commands.")
    dashboard_sub = dashboard.add_subparsers(dest="dashboard_command")
    serve = dashboard_sub.add_parser("serve", help="Serve dashboard locally. Placeholder in v0.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)

    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    if args.command == "poll" and args.source != "mock":
        raise SystemExit("Live IBKR polling is not implemented in v0.")
    if args.command == "poll":
        print(write_mock_poll_once(args.data_dir))
        return
    if args.command == "dashboard" and args.dashboard_command == "serve":
        serve_dashboard(host=args.host, port=args.port)
        return
    if args.command == "flex" and args.flex_command == "test-fetch":
        token = require_env("IBKR_FLEX_TOKEN")
        query_id = require_env("IBKR_FLEX_ACTIVITY_QUERY_ID")
        result = fetch_flex_report(token=token, query_id=query_id)
        report_path = save_flex_report(
            result.report_xml,
            args.output_dir,
            stem=f"activity_{result.reference_code}",
        )
        statement = parse_flex_xml(result.report_xml)
        print(
            json.dumps(
                {
                    "status": "ok",
                    "report_path": str(report_path),
                    "dividends": len(statement.dividends),
                    "fees": len(statement.fees),
                    "realized_pnl": len(statement.realized_pnl),
                    "trades": len(statement.trades),
                    "account_values": len(statement.account_values),
                },
                sort_keys=True,
            )
        )
        return
    print(f"{args.command} is scaffolded; implementation begins in a later phase.")


if __name__ == "__main__":
    main()
