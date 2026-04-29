from __future__ import annotations

from typing import Any

from ibkr_monitor.dashboard.schema import SNAPSHOT_SCHEMA_VERSION
from ibkr_monitor.ibkr.flex import NormalizedRow

HistoryPayload = dict[str, object]


def build_history_payload(account_values: list[NormalizedRow]) -> HistoryPayload:
    values_by_date = _portfolio_values_by_date(account_values)
    portfolio_value = [
        {"date": date, "net_liquidation": value}
        for date, value in sorted(values_by_date.items())
    ]
    daily_pnl = _daily_pnl(portfolio_value)

    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "base_currency": _base_currency(account_values),
        "portfolio_value": portfolio_value,
        "daily_pnl": daily_pnl,
        "benchmark": {
            "name": "Benchmark placeholder",
            "series": [],
        },
    }


def _portfolio_values_by_date(account_values: list[NormalizedRow]) -> dict[str, float]:
    equity_values: dict[str, float] = {}
    nav_values: dict[str, float] = {}

    for row in account_values:
        date = _dashboard_date(row.get("date"))
        if not date:
            continue

        section = row.get("section")
        name = row.get("name")
        value = row.get("value")

        if section == "EquitySummaryByReportDateInBase" and name == "net_liquidation":
            equity_values[date] = _float_value(value)
        elif section == "ChangeInNAV" and name == "ending_value":
            nav_values[date] = _float_value(value)

    values_by_date = dict(nav_values)
    values_by_date.update(equity_values)
    return values_by_date


def _daily_pnl(portfolio_value: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    previous_value: float | None = None
    for point in portfolio_value:
        current_value = _float_value(point["net_liquidation"])
        pnl = 0.0 if previous_value is None else current_value - previous_value
        rows.append({"date": point["date"], "value": pnl})
        previous_value = current_value
    return rows


def _base_currency(account_values: list[NormalizedRow]) -> str:
    for row in account_values:
        currency = row.get("currency")
        if isinstance(currency, str) and currency:
            return currency
    return "USD"


def _dashboard_date(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    text = value.strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    return text


def _float_value(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str) and value:
        return float(value.replace(",", ""))
    return 0.0
