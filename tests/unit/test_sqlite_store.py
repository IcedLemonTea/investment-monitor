from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ibkr_monitor.storage.sqlite_store import insert_snapshot


def test_insert_snapshot_writes_snapshot_and_positions(tmp_path: Path) -> None:
    snapshot = json.loads(Path("public/data/latest.example.json").read_text(encoding="utf-8"))
    db_path = tmp_path / "monitor.sqlite3"

    snapshot_id = insert_snapshot(db_path, snapshot)

    with sqlite3.connect(db_path) as connection:
        snapshot_count = connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        position_count = connection.execute("SELECT COUNT(*) FROM positions").fetchone()[0]

    assert snapshot_id == 1
    assert snapshot_count == 1
    assert position_count == 5
