from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ibkr_monitor.dashboard.schema import SNAPSHOT_SCHEMA_VERSION
from ibkr_monitor.storage.atomic_json import write_json_atomic


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
