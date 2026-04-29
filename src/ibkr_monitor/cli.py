from __future__ import annotations

import argparse

from ibkr_monitor.dashboard.server import serve_dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ibkr-monitor")
    subparsers = parser.add_subparsers(dest="command")

    poll = subparsers.add_parser("poll", help="Poll one snapshot. Mock only in v0.")
    poll.add_argument("--source", choices=["mock", "flex", "gateway"], default="mock")

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
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    if args.command == "poll" and args.source != "mock":
        raise SystemExit("Live IBKR polling is not implemented in v0.")
    if args.command == "dashboard" and args.dashboard_command == "serve":
        serve_dashboard(host=args.host, port=args.port)
        return
    print(f"{args.command} is scaffolded; implementation begins in a later phase.")


if __name__ == "__main__":
    main()
