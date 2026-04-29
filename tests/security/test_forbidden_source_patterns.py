from __future__ import annotations

from pathlib import Path

FORBIDDEN_PATTERNS = [
    "placeOrder",
    "cancelOrder",
    "modifyOrder",
    "/iserver/account/orders",
    "/iserver/reply",
    "whatif",
]


def test_no_trading_patterns_in_source() -> None:
    roots = [Path("src"), Path("public"), Path("scripts")]
    files = [
        path
        for root in roots
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ]

    matches: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                matches.append(f"{path}: {pattern}")

    assert matches == []
