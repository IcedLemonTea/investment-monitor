from __future__ import annotations

import functools
import json
from collections.abc import Callable
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ibkr_monitor.dashboard.build import write_mock_poll_once


def create_dashboard_handler(public_dir: Path) -> Callable[..., SimpleHTTPRequestHandler]:
    root = public_dir

    class DashboardRequestHandler(SimpleHTTPRequestHandler):
        def do_POST(self) -> None:
            if self.path != "/api/refresh-now":
                self.send_error(404, "Not found")
                return

            result = write_mock_poll_once(root / "data")
            body = json.dumps(result, sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return functools.partial(DashboardRequestHandler, directory=str(root))


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
