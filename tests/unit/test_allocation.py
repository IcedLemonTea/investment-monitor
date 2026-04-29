from __future__ import annotations

from pathlib import Path

import pytest

from ibkr_monitor.portfolio.allocation import (
    PositionInput,
    allocation_by_ticker,
    calculate_allocation,
)
from ibkr_monitor.portfolio.targets import Target, load_targets, validate_targets


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

    rows = allocation_by_ticker(positions, targets)

    assert rows["QLD"].current_percent == 0.45
    assert rows["QLD"].target_percent == 0.50
    assert round(rows["QLD"].drift_percent, 6) == -0.05
    assert rows["QLD"].rebalance_value == 5_000
    assert rows["QLD"].current_value == 45_000
    assert rows["QLD"].target_value == 50_000
    assert rows["CASH_OTHERS"].target_percent == 0


def test_allocation_includes_missing_target_positions() -> None:
    targets = [
        Target(ticker="QLD", display_ticker="NYSEARCA:QLD", target_percent=50),
        Target(ticker="AVUV", display_ticker="NYSEARCA:AVUV", target_percent=50),
    ]

    rows = allocation_by_ticker([PositionInput(ticker="QLD", market_value=10_000)], targets)

    assert rows["AVUV"].current_percent == 0
    assert rows["AVUV"].target_percent == 0.5
    assert rows["AVUV"].rebalance_value == 5_000


def test_allocation_handles_zero_market_value() -> None:
    targets = [Target(ticker="QLD", display_ticker="NYSEARCA:QLD", target_percent=100)]

    rows = calculate_allocation([PositionInput(ticker="QLD", market_value=0)], targets)

    assert rows[0].current_percent == 0
    assert rows[0].target_value == 0
    assert rows[0].rebalance_value == 0


def test_targets_must_total_100_percent() -> None:
    targets = [
        Target(ticker="QLD", display_ticker="NYSEARCA:QLD", target_percent=50),
        Target(ticker="TQQQ", display_ticker="NASDAQ:TQQQ", target_percent=20),
    ]

    with pytest.raises(ValueError, match="Target percentages must total 100"):
        validate_targets(targets)
