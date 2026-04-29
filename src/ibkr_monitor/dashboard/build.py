from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ibkr_monitor.dashboard.schema import SNAPSHOT_SCHEMA_VERSION
from ibkr_monitor.ibkr.flex import FlexStatement, NormalizedRow
from ibkr_monitor.portfolio.history import build_history_payload
from ibkr_monitor.portfolio.targets import Target, load_targets
from ibkr_monitor.storage.atomic_json import write_json_atomic
from ibkr_monitor.storage.sqlite_store import load_flex_account_values


def dashboard_builder_available() -> bool:
    """Return true when dashboard mock output generation is available."""
    return True


def build_mock_snapshot(generated_at: str | None = None) -> dict[str, object]:
    timestamp = generated_at or datetime.now(tz=UTC).isoformat()
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "source": "mock",
        "mode": "poll_once",
        "generated_at": timestamp,
        "base_currency": "USD",
        "display_currency": "MYR",
        "fx": {
            "USD_MYR": 4.75,
            "source": "manual_config",
        },
        "account": {
            "account_id": "MOCK",
            "account_type": "individual",
            "net_liquidation": 100000.0,
            "daily_pnl": 250.0,
            "unrealized_pnl": 5000.0,
            "realized_pnl": 100.0,
            "margin_value": 0.0,
            "excess_liquidity": 100000.0,
            "total_market_value": 100000.0,
        },
        "positions": [
            {
                "ticker": "QLD",
                "display_ticker": "NYSEARCA:QLD",
                "name": "ProShares Ultra QQQ",
                "asset_class": "ETF",
                "currency": "USD",
                "units": 632.91,
                "unit_price": 79.00,
                "market_value": 50000.0,
                "daily_pnl": 150.0,
                "unrealized_pnl": 2500.0,
                "current_percent": 0.5,
                "target_percent": 0.5,
                "drift_percent": 0.0,
            },
            {
                "ticker": "TQQQ",
                "display_ticker": "NASDAQ:TQQQ",
                "name": "ProShares UltraPro QQQ",
                "asset_class": "ETF",
                "currency": "USD",
                "units": 166.67,
                "unit_price": 60.00,
                "market_value": 10000.0,
                "daily_pnl": 40.0,
                "unrealized_pnl": 800.0,
                "current_percent": 0.1,
                "target_percent": 0.1,
                "drift_percent": 0.0,
            },
            {
                "ticker": "AVUV",
                "display_ticker": "NYSEARCA:AVUV",
                "name": "Avantis U.S. Small Cap Value ETF",
                "asset_class": "ETF",
                "currency": "USD",
                "units": 250.0,
                "unit_price": 80.00,
                "market_value": 20000.0,
                "daily_pnl": 25.0,
                "unrealized_pnl": 900.0,
                "current_percent": 0.2,
                "target_percent": 0.2,
                "drift_percent": 0.0,
            },
            {
                "ticker": "AVDV",
                "display_ticker": "NYSEARCA:AVDV",
                "name": "Avantis International Small Cap Value ETF",
                "asset_class": "ETF",
                "currency": "USD",
                "units": 200.0,
                "unit_price": 50.00,
                "market_value": 10000.0,
                "daily_pnl": 20.0,
                "unrealized_pnl": 400.0,
                "current_percent": 0.1,
                "target_percent": 0.1,
                "drift_percent": 0.0,
            },
            {
                "ticker": "QMOM",
                "display_ticker": "NASDAQ:QMOM",
                "name": "Alpha Architect U.S. Quantitative Momentum ETF",
                "asset_class": "ETF",
                "currency": "USD",
                "units": 100.0,
                "unit_price": 100.00,
                "market_value": 10000.0,
                "daily_pnl": 15.0,
                "unrealized_pnl": 400.0,
                "current_percent": 0.1,
                "target_percent": 0.1,
                "drift_percent": 0.0,
            },
        ],
        "warnings": [
            {
                "code": "MOCK_DATA",
                "message": "Mock snapshot only. No live IBKR calls were made.",
            }
        ],
    }


def build_mock_health(generated_at: str) -> dict[str, object]:
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "status": "ok",
        "source": "mock",
        "last_successful_refresh": generated_at,
        "ibkr_session": {
            "gateway": "not_configured",
            "flex": "not_configured",
        },
        "message": (
            "Mock refresh completed locally. No live brokerage or market data calls were used."
        ),
    }


def write_mock_poll_once(data_dir: Path, generated_at: str | None = None) -> dict[str, object]:
    timestamp = generated_at or datetime.now(tz=UTC).isoformat()
    latest = build_mock_snapshot(timestamp)
    health = build_mock_health(timestamp)

    write_json_atomic(data_dir / "latest.json", latest)
    write_json_atomic(data_dir / "health.json", health)

    return {
        "status": "ok",
        "source": "mock",
        "latest_path": str(data_dir / "latest.json"),
        "health_path": str(data_dir / "health.json"),
        "generated_at": timestamp,
    }


def write_history_from_db(db_path: Path, data_dir: Path) -> dict[str, object]:
    account_values = load_flex_account_values(db_path)
    history = build_history_payload(account_values)
    history_path = data_dir / "history.json"
    write_json_atomic(history_path, history)
    portfolio_value = history["portfolio_value"]
    daily_pnl = history["daily_pnl"]
    if not isinstance(portfolio_value, list) or not isinstance(daily_pnl, list):
        raise TypeError("History payload is malformed")
    return {
        "status": "ok",
        "history_path": str(history_path),
        "portfolio_value_points": len(portfolio_value),
        "daily_pnl_points": len(daily_pnl),
    }


def build_latest_from_flex_statement(
    statement: FlexStatement,
    targets: list[Target],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    account_values = statement.account_values
    latest_date = _latest_report_date(account_values, statement.open_positions)
    equity = _latest_named_values(
        account_values,
        latest_date,
        section="EquitySummaryByReportDateInBase",
    )
    nav = _latest_named_values(account_values, latest_date, section="ChangeInNAV")
    positions = _latest_open_positions(statement.open_positions, latest_date)
    total_market_value = sum(float(position["market_value"]) for position in positions)
    target_by_ticker = {target.ticker: target for target in targets}

    rendered_positions: list[dict[str, Any]] = []
    for position in positions:
        ticker = str(position["ticker"])
        target = target_by_ticker.get(ticker)
        target_percent = target.target_weight if target else 0.0
        market_value = float(position["market_value"])
        current_percent = market_value / total_market_value if total_market_value else 0.0
        rendered_positions.append(
            {
                "ticker": ticker,
                "display_ticker": target.display_ticker if target else ticker,
                "name": position["name"] or ticker,
                "asset_class": position["asset_class"] or "UNKNOWN",
                "currency": position["currency"] or "USD",
                "units": position["units"],
                "unit_price": position["unit_price"],
                "market_value": market_value,
                "daily_pnl": 0.0,
                "unrealized_pnl": position["unrealized_pnl"],
                "current_percent": current_percent,
                "target_percent": target_percent,
                "drift_percent": current_percent - target_percent,
            }
        )

    net_liquidation = _value(equity, "net_liquidation", _value(nav, "ending_value"))
    realized_pnl = _value(nav, "realized_pnl")
    unrealized_pnl = sum(float(position["unrealized_pnl"]) for position in positions)

    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "source": "flex",
        "mode": "statement",
        "generated_at": generated_at or _generated_at_from_date(latest_date),
        "base_currency": _currency(account_values, positions),
        "display_currency": "MYR",
        "fx": {
            "USD_MYR": _manual_usd_myr_rate(),
            "source": "manual_config",
        },
        "account": {
            "account_id": _account_id(account_values, positions),
            "account_type": "individual",
            "net_liquidation": net_liquidation,
            "daily_pnl": _latest_daily_pnl(account_values, latest_date),
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": realized_pnl,
            "margin_value": 0.0,
            "excess_liquidity": net_liquidation,
            "total_market_value": total_market_value,
        },
        "positions": rendered_positions,
        "warnings": [
            {
                "code": "FLEX_STATEMENT_DATA",
                "message": (
                    "Latest snapshot is based on Flex statement data, not live Gateway data."
                ),
            }
        ],
    }


def write_latest_from_flex_report(
    report_path: Path,
    data_dir: Path,
    targets_path: Path = Path("config/targets.example.yaml"),
) -> dict[str, object]:
    from ibkr_monitor.ibkr.flex import parse_flex_file

    statement = parse_flex_file(report_path)
    snapshot = build_latest_from_flex_statement(statement, load_targets(targets_path))
    latest_path = data_dir / "latest.json"
    health_path = data_dir / "health.json"
    write_json_atomic(latest_path, snapshot)
    write_json_atomic(health_path, build_flex_health(snapshot["generated_at"], report_path))
    return {
        "status": "ok",
        "latest_path": str(latest_path),
        "health_path": str(health_path),
        "source": "flex",
        "positions": len(snapshot["positions"]),
    }


def build_flex_health(generated_at: str, report_path: Path) -> dict[str, object]:
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "status": "ok",
        "source": "flex",
        "last_successful_refresh": generated_at,
        "ibkr_session": {
            "gateway": "not_configured",
            "flex": "ok",
        },
        "message": f"Flex statement snapshot loaded from {report_path.name}.",
    }


def _latest_report_date(
    account_values: list[NormalizedRow],
    positions: list[NormalizedRow],
) -> str:
    dates = [
        str(row.get("date", ""))
        for row in [*account_values, *positions]
        if str(row.get("date", "")).strip()
    ]
    if not dates:
        return datetime.now(tz=UTC).strftime("%Y%m%d")
    return max(dates)


def _latest_named_values(
    account_values: list[NormalizedRow],
    latest_date: str,
    *,
    section: str,
) -> dict[str, float]:
    return {
        str(row["name"]): float(row["value"])
        for row in account_values
        if row.get("date") == latest_date and row.get("section") == section
    }


def _latest_open_positions(
    positions: list[NormalizedRow],
    latest_date: str,
) -> list[NormalizedRow]:
    return [
        position
        for position in positions
        if position.get("date") == latest_date and float(position.get("market_value", 0.0)) != 0
    ]


def _latest_daily_pnl(account_values: list[NormalizedRow], latest_date: str) -> float:
    history = build_history_payload(account_values)
    daily_pnl = history["daily_pnl"]
    if not isinstance(daily_pnl, list):
        return 0.0
    dashboard_date = _dashboard_date(latest_date)
    for row in daily_pnl:
        if isinstance(row, dict) and row.get("date") == dashboard_date:
            return float(row.get("value", 0.0))
    return 0.0


def _value(values: dict[str, float], key: str, fallback: float = 0.0) -> float:
    return values.get(key, fallback)


def _generated_at_from_date(value: str) -> str:
    date = _dashboard_date(value)
    if not date:
        return datetime.now(tz=UTC).isoformat()
    return f"{date}T00:00:00+00:00"


def _dashboard_date(value: str) -> str:
    if len(value) == 8 and value.isdigit():
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
    return value


def _currency(account_values: list[NormalizedRow], positions: list[NormalizedRow]) -> str:
    for row in [*account_values, *positions]:
        currency = row.get("currency")
        if isinstance(currency, str) and currency:
            return currency
    return "USD"


def _account_id(account_values: list[NormalizedRow], positions: list[NormalizedRow]) -> str:
    for row in [*account_values, *positions]:
        account_id = row.get("account_id")
        if isinstance(account_id, str) and account_id:
            return account_id
    return "UNKNOWN"


def _manual_usd_myr_rate() -> float | None:
    import os

    value = os.environ.get("USD_MYR_MANUAL_RATE", "").strip()
    return float(value) if value else None
