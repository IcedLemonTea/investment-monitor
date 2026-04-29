from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ibkr_monitor.ibkr.flex import parse_flex_file
from ibkr_monitor.storage.sqlite_store import insert_flex_statement, insert_snapshot


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


def test_insert_flex_statement_writes_all_normalized_rows(tmp_path: Path) -> None:
    statement = parse_flex_file("tests/fixtures/flex/sample_statement.xml")
    db_path = tmp_path / "monitor.sqlite3"

    counts = insert_flex_statement(db_path, statement)

    with sqlite3.connect(db_path) as connection:
        account_value_count = connection.execute(
            "SELECT COUNT(*) FROM flex_account_values"
        ).fetchone()[0]
        dividend_count = connection.execute("SELECT COUNT(*) FROM flex_dividends").fetchone()[0]
        fee_count = connection.execute("SELECT COUNT(*) FROM flex_fees").fetchone()[0]
        realized_count = connection.execute("SELECT COUNT(*) FROM flex_realized_pnl").fetchone()[0]
        trade_count = connection.execute("SELECT COUNT(*) FROM flex_trades").fetchone()[0]
        tsla_trade = connection.execute(
            """
            SELECT account_id, symbol, quantity, proceeds, realized_pnl
            FROM flex_trades
            WHERE symbol = 'TSLA'
            """
        ).fetchone()

    assert counts == {
        "account_values": 2,
        "dividends": 1,
        "fees": 2,
        "realized_pnl": 1,
        "trades": 2,
    }
    assert account_value_count == 2
    assert dividend_count == 1
    assert fee_count == 2
    assert realized_count == 1
    assert trade_count == 2
    assert tsla_trade == ("U0000001", "TSLA", -5.0, 900.0, 125.75)
