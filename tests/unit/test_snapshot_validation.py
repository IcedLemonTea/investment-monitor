from __future__ import annotations

import json
from pathlib import Path

import pytest

from ibkr_monitor.dashboard.validate import validate_snapshot


def test_latest_example_snapshot_is_valid() -> None:
    snapshot = json.loads(Path("public/data/latest.example.json").read_text(encoding="utf-8"))

    validate_snapshot(snapshot)


def test_snapshot_validation_rejects_missing_account_field() -> None:
    snapshot = json.loads(Path("public/data/latest.example.json").read_text(encoding="utf-8"))
    del snapshot["account"]["net_liquidation"]

    with pytest.raises(ValueError, match="account missing fields"):
        validate_snapshot(snapshot)
