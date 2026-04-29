from __future__ import annotations

from typing import Any

REQUIRED_ACCOUNT_FIELDS = {
    "account_id",
    "net_liquidation",
    "daily_pnl",
    "unrealized_pnl",
    "realized_pnl",
    "margin_value",
    "total_market_value",
}

REQUIRED_POSITION_FIELDS = {
    "ticker",
    "name",
    "currency",
    "units",
    "unit_price",
    "market_value",
    "current_percent",
    "target_percent",
    "drift_percent",
}


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    require(snapshot.get("schema_version") == "1.0", "schema_version must be 1.0")
    require(snapshot.get("base_currency") == "USD", "base_currency must be USD")
    require(isinstance(snapshot.get("account"), dict), "account must be an object")
    require(isinstance(snapshot.get("positions"), list), "positions must be a list")
    require(isinstance(snapshot.get("warnings"), list), "warnings must be a list")

    account = snapshot["account"]
    missing_account = REQUIRED_ACCOUNT_FIELDS - account.keys()
    require(not missing_account, f"account missing fields: {sorted(missing_account)}")

    positions = snapshot["positions"]
    require(len(positions) > 0, "positions must not be empty")
    for index, position in enumerate(positions):
        require(isinstance(position, dict), f"positions[{index}] must be an object")
        missing_position = REQUIRED_POSITION_FIELDS - position.keys()
        require(
            not missing_position,
            f"positions[{index}] missing fields: {sorted(missing_position)}",
        )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)
