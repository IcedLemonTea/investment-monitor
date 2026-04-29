from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


def sqlite_store_available() -> bool:
    return True


def initialize_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(path) as connection:
        connection.executescript(schema)


def insert_snapshot(path: Path, snapshot: dict[str, Any]) -> int:
    initialize_database(path)
    account = snapshot["account"]
    positions = snapshot["positions"]
    with sqlite3.connect(path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO snapshots (
              source, generated_at, market_session, base_currency, net_liquidation,
              daily_pnl, unrealized_pnl, realized_pnl, margin_value, raw_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot["source"],
                snapshot["generated_at"],
                snapshot.get("mode"),
                snapshot["base_currency"],
                account["net_liquidation"],
                account["daily_pnl"],
                account["unrealized_pnl"],
                account["realized_pnl"],
                account["margin_value"],
                json.dumps(snapshot, sort_keys=True),
            ),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("SQLite did not return a snapshot id")
        snapshot_id = cursor.lastrowid
        connection.executemany(
            """
            INSERT INTO positions (
              snapshot_id, ticker, conid, asset_class, currency, units, unit_price,
              market_value, daily_pnl, unrealized_pnl
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    snapshot_id,
                    position["ticker"],
                    position.get("conid"),
                    position.get("asset_class"),
                    position["currency"],
                    position["units"],
                    position["unit_price"],
                    position["market_value"],
                    position["daily_pnl"],
                    position["unrealized_pnl"],
                )
                for position in positions
            ],
        )
        return snapshot_id
