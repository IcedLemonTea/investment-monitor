from __future__ import annotations

import json
from pathlib import Path


def load_example(name: str) -> dict[str, object]:
    return json.loads(Path("public/data", name).read_text(encoding="utf-8"))


def test_latest_example_uses_snapshot_contract() -> None:
    latest = load_example("latest.example.json")

    assert latest["schema_version"] == "1.0"
    assert latest["base_currency"] == "USD"
    assert "account" in latest
    assert "positions" in latest
    assert "summary" not in latest
    assert "cash" not in json.dumps(latest["account"])


def test_latest_example_target_weights_match_plan() -> None:
    latest = load_example("latest.example.json")
    positions = latest["positions"]
    assert isinstance(positions, list)

    targets = {position["ticker"]: position["target_percent"] for position in positions}

    assert targets == {
        "QLD": 0.5,
        "TQQQ": 0.1,
        "AVUV": 0.2,
        "AVDV": 0.1,
        "QMOM": 0.1,
    }


def test_history_and_health_examples_are_present() -> None:
    history = load_example("history.example.json")
    health = load_example("health.example.json")

    assert history["portfolio_value"]
    assert history["daily_pnl"]
    assert health["status"] == "example"
    assert health["source"] == "mock"
