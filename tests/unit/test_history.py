from __future__ import annotations

from ibkr_monitor.portfolio.history import build_history_payload


def test_build_history_payload_prefers_equity_summary_net_liquidation() -> None:
    payload = build_history_payload(
        [
            {
                "date": "20260428",
                "account_id": "U0000001",
                "section": "ChangeInNAV",
                "name": "ending_value",
                "currency": "USD",
                "value": 99999.0,
            },
            {
                "date": "20260428",
                "account_id": "U0000001",
                "section": "EquitySummaryByReportDateInBase",
                "name": "net_liquidation",
                "currency": "USD",
                "value": 100000.0,
            },
            {
                "date": "20260429",
                "account_id": "U0000001",
                "section": "EquitySummaryByReportDateInBase",
                "name": "net_liquidation",
                "currency": "USD",
                "value": 100250.0,
            },
        ]
    )

    assert payload["schema_version"] == "1.0"
    assert payload["base_currency"] == "USD"
    assert payload["portfolio_value"] == [
        {"date": "2026-04-28", "net_liquidation": 100000.0},
        {"date": "2026-04-29", "net_liquidation": 100250.0},
    ]
    assert payload["daily_pnl"] == [
        {"date": "2026-04-28", "value": 0.0},
        {"date": "2026-04-29", "value": 250.0},
    ]


def test_build_history_payload_falls_back_to_change_in_nav_ending_value() -> None:
    payload = build_history_payload(
        [
            {
                "date": "20260427",
                "account_id": "U0000001",
                "section": "ChangeInNAV",
                "name": "ending_value",
                "currency": "USD",
                "value": 99500.0,
            },
            {
                "date": "20260428",
                "account_id": "U0000001",
                "section": "ChangeInNAV",
                "name": "ending_value",
                "currency": "USD",
                "value": 100000.0,
            },
        ]
    )

    assert payload["portfolio_value"] == [
        {"date": "2026-04-27", "net_liquidation": 99500.0},
        {"date": "2026-04-28", "net_liquidation": 100000.0},
    ]
    assert payload["daily_pnl"] == [
        {"date": "2026-04-27", "value": 0.0},
        {"date": "2026-04-28", "value": 500.0},
    ]


def test_build_history_payload_ignores_non_history_account_values() -> None:
    payload = build_history_payload(
        [
            {
                "date": "20260429",
                "account_id": "U0000001",
                "name": "NetLiquidation",
                "currency": "USD",
                "value": 125000.5,
            },
            {
                "date": "20260429",
                "account_id": "U0000001",
                "section": "OpenPosition",
                "name": "position_value:QLD",
                "currency": "USD",
                "value": 50000.0,
            },
        ]
    )

    assert payload["portfolio_value"] == []
    assert payload["daily_pnl"] == []
