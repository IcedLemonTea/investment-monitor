from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify rendered localhost dashboard DOM.")
    parser.add_argument("--url", default="http://127.0.0.1:8765/")
    parser.add_argument("--expect-source", default="flex / statement")
    parser.add_argument(
        "--reject",
        action="append",
        default=[
            "MOCK",
            "$100,000.00",
            "Latest snapshot is based on Flex statement data",
            "Example holdings",
        ],
    )
    args = parser.parse_args()

    browser = find_browser()
    with tempfile.TemporaryDirectory() as profile:
        completed = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                f"--user-data-dir={profile}",
                "--virtual-time-budget=5000",
                "--dump-dom",
                args.url,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

    dom = completed.stdout
    if args.expect_source not in dom:
        raise SystemExit(f"Rendered DOM did not contain expected source: {args.expect_source}")
    if "GMT" not in dom and "UTC" not in dom:
        raise SystemExit("Rendered DOM did not include an explicit timezone label.")
    rejected = [text for text in args.reject if text in dom]
    if rejected:
        raise SystemExit(f"Rendered DOM contained rejected text: {rejected}")
    print(f"render ok: {args.expect_source}")


def find_browser() -> Path:
    candidates = [
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit("No supported Chromium browser found for render verification.")


if __name__ == "__main__":
    main()
