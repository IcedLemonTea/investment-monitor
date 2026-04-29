from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from ibkr_monitor.dashboard.build import write_mock_poll_once
from ibkr_monitor.dashboard.server import create_dashboard_handler


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_mock_poll_once_writes_latest_and_health(tmp_path: Path) -> None:
    result = write_mock_poll_once(tmp_path, generated_at="2026-04-29T06:00:00+00:00")

    latest = read_json(tmp_path / "latest.json")
    health = read_json(tmp_path / "health.json")

    assert result["source"] == "mock"
    assert latest["schema_version"] == "1.0"
    assert latest["source"] == "mock"
    assert latest["mode"] == "poll_once"
    assert latest["generated_at"] == "2026-04-29T06:00:00+00:00"
    assert health["status"] == "ok"
    assert health["source"] == "mock"
    assert health["last_successful_refresh"] == latest["generated_at"]


def test_refresh_now_posts_mock_files(tmp_path: Path) -> None:
    public_dir = tmp_path / "public"
    handler = create_dashboard_handler(public_dir)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

    try:
        port = server.server_address[1]
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/refresh-now",
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    latest = read_json(public_dir / "data" / "latest.json")
    health = read_json(public_dir / "data" / "health.json")

    assert result["status"] == "ok"
    assert latest["source"] == "mock"
    assert health["message"] == (
        "Mock refresh completed locally. No live brokerage or market data calls were used."
    )
