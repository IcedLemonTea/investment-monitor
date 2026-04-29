from __future__ import annotations

import functools
import json
from collections.abc import Callable
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ibkr_monitor.dashboard.build import write_latest_from_flex_report, write_mock_poll_once


def create_dashboard_handler(public_dir: Path) -> Callable[..., SimpleHTTPRequestHandler]:
    root = public_dir

    class DashboardRequestHandler(SimpleHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != "/api/refresh-now":
                self.send_error(404, "Not found")
                return

            result = refresh_dashboard_data(root)
            body = json.dumps(result, sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return functools.partial(DashboardRequestHandler, directory=str(root))


def refresh_dashboard_data(public_dir: Path) -> dict[str, object]:
    project_root = public_dir.parent
    flex_report = latest_flex_report(project_root / "runtime" / "data" / "private" / "flex")
    if flex_report is not None:
        return write_latest_from_flex_report(flex_report, public_dir / "data")
    return write_mock_poll_once(public_dir / "data")


def latest_flex_report(flex_dir: Path) -> Path | None:
    if not flex_dir.exists():
        return None
    reports = list(flex_dir.glob("activity_*.xml"))
    if not reports:
        return None
    return max(reports, key=lambda path: path.stat().st_mtime)


def serve_dashboard(
    host: str = "127.0.0.1",
    port: int = 8765,
    public_dir: Path | None = None,
) -> None:
    root = public_dir or Path(__file__).resolve().parents[3] / "public"
    handler = create_dashboard_handler(root)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Serving dashboard at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping dashboard server.")
    finally:
        server.server_close()
