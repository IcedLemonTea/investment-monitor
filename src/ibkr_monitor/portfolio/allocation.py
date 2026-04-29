from __future__ import annotations

from dataclasses import dataclass

from ibkr_monitor.portfolio.targets import Target


@dataclass(frozen=True)
class PositionInput:
    ticker: str
    market_value: float


@dataclass(frozen=True)
class AllocationRow:
    ticker: str
    current_percent: float
    target_percent: float
    drift_percent: float
    rebalance_value: float


def calculate_allocation(
    positions: list[PositionInput],
    targets: list[Target],
) -> list[AllocationRow]:
    total_market_value = sum(position.market_value for position in positions)
    target_by_ticker = {target.ticker: target for target in targets}
    value_by_ticker = {position.ticker: position.market_value for position in positions}

    rows: list[AllocationRow] = []
    for ticker in target_by_ticker:
        current_value = value_by_ticker.get(ticker, 0.0)
        current_percent = current_value / total_market_value if total_market_value else 0.0
        target_percent = target_by_ticker[ticker].target_weight
        rows.append(
            AllocationRow(
                ticker=ticker,
                current_percent=current_percent,
                target_percent=target_percent,
                drift_percent=current_percent - target_percent,
                rebalance_value=(target_percent * total_market_value) - current_value,
            )
        )
    return rows
