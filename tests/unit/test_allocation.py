from __future__ import annotations

from pathlib import Path

from ibkr_monitor.portfolio.allocation import PositionInput, calculate_allocation
from ibkr_monitor.portfolio.targets import load_targets


def test_targets_total_100_percent() -> None:
    targets = load_targets(Path("config/targets.example.yaml"))

    assert sum(target.target_percent for target in targets) == 100


def test_allocation_calculates_current_weight_drift_and_rebalance() -> None:
    targets = load_targets(Path("config/targets.example.yaml"))
    positions = [
        PositionInput(ticker="QLD", market_value=45_000),
        PositionInput(ticker="TQQQ", market_value=10_000),
        PositionInput(ticker="AVUV", market_value=25_000),
        PositionInput(ticker="AVDV", market_value=10_000),
        PositionInput(ticker="QMOM", market_value=10_000),
    ]

    rows = {row.ticker: row for row in calculate_allocation(positions, targets)}

    assert rows["QLD"].current_percent == 0.45
    assert rows["QLD"].target_percent == 0.50
    assert round(rows["QLD"].drift_percent, 6) == -0.05
    assert rows["QLD"].rebalance_value == 5_000
    assert rows["CASH_OTHERS"].target_percent == 0
