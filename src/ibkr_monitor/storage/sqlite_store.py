from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibkr_monitor.ibkr.flex import FlexStatement, NormalizedRow


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


def insert_flex_statement(path: Path, statement: FlexStatement) -> dict[str, int]:
    initialize_database(path)
    with sqlite3.connect(path) as connection:
        counts = {
            "account_values": _insert_flex_account_values(connection, statement.account_values),
            "dividends": _insert_flex_cash_rows(connection, "flex_dividends", statement.dividends),
            "fees": _insert_flex_cash_rows(connection, "flex_fees", statement.fees),
            "realized_pnl": _insert_flex_realized_pnl(connection, statement.realized_pnl),
            "trades": _insert_flex_trades(connection, statement.trades),
        }
    return counts


def load_flex_account_values(path: Path) -> list[dict[str, object]]:
    initialize_database(path)
    with sqlite3.connect(path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT date, account_id, name, currency, section, value
            FROM flex_account_values
            ORDER BY date, section, name
            """
        ).fetchall()
    return [dict(row) for row in rows]


def table_counts(path: Path) -> dict[str, int]:
    initialize_database(path)
    tables = [
        "snapshots",
        "positions",
        "flex_account_values",
        "flex_dividends",
        "flex_fees",
        "flex_realized_pnl",
        "flex_trades",
    ]
    with sqlite3.connect(path) as connection:
        return {
            table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in tables
        }


def _insert_flex_account_values(
    connection: sqlite3.Connection, rows: list[NormalizedRow]
) -> int:
    connection.executemany(
        """
        INSERT INTO flex_account_values (
          date, account_id, name, currency, section, value
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["date"],
                row["account_id"],
                row["name"],
                row.get("currency"),
                row.get("section"),
                row["value"],
            )
            for row in rows
        ],
    )
    return len(rows)


def _insert_flex_cash_rows(
    connection: sqlite3.Connection, table: str, rows: list[NormalizedRow]
) -> int:
    if table not in {"flex_dividends", "flex_fees"}:
        raise ValueError(f"Unsupported Flex cash table: {table}")
    connection.executemany(
        f"""
        INSERT INTO {table} (
          date, account_id, symbol, description, type, currency, amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["date"],
                row["account_id"],
                row.get("symbol"),
                row.get("description"),
                row.get("type"),
                row.get("currency"),
                row["amount"],
            )
            for row in rows
        ],
    )
    return len(rows)


def _insert_flex_realized_pnl(
    connection: sqlite3.Connection, rows: list[NormalizedRow]
) -> int:
    connection.executemany(
        """
        INSERT INTO flex_realized_pnl (
          date, account_id, symbol, description, currency, realized_pnl
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["date"],
                row["account_id"],
                row.get("symbol"),
                row.get("description"),
                row.get("currency"),
                row["realized_pnl"],
            )
            for row in rows
        ],
    )
    return len(rows)


def _insert_flex_trades(connection: sqlite3.Connection, rows: list[NormalizedRow]) -> int:
    connection.executemany(
        """
        INSERT INTO flex_trades (
          date, account_id, symbol, description, asset_class, currency, quantity,
          price, proceeds, commission, realized_pnl
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["date"],
                row["account_id"],
                row.get("symbol"),
                row.get("description"),
                row.get("asset_class"),
                row.get("currency"),
                row["quantity"],
                row["price"],
                row["proceeds"],
                row["commission"],
                row["realized_pnl"],
            )
            for row in rows
        ],
    )
    return len(rows)
