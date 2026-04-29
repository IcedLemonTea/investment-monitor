from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountSummary:
    account_id: str
    net_liquidation: float
    daily_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    margin_value: float
