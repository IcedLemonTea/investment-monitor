from __future__ import annotations

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def serve_dashboard(
    host: str = "127.0.0.1",
    port: int = 8765,
    public_dir: Path | None = None,
) -> None:
    root = public_dir or Path(__file__).resolve().parents[3] / "public"
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(root))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Serving dashboard at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping dashboard server.")
    finally:
        server.server_close()
