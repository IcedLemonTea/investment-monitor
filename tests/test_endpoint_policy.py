from __future__ import annotations

import pytest

from ibkr_monitor.ibkr.endpoint_policy import ALLOWED_ENDPOINTS, assert_endpoint_allowed
from ibkr_monitor.ibkr.errors import EndpointNotAllowedError


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/tickle"),
        ("GET", "/iserver/auth/status"),
        ("GET", "/portfolio/accounts"),
        ("GET", "/portfolio/U1234567/summary"),
        ("GET", "/portfolio/U1234567/ledger"),
        ("GET", "/portfolio/U1234567/allocation"),
        ("GET", "/portfolio2/U1234567/positions"),
        ("GET", "/iserver/account/pnl/partitioned"),
        ("GET", "/iserver/marketdata/snapshot"),
    ],
)
def test_allowlisted_endpoints_are_allowed(method: str, path: str) -> None:
    assert_endpoint_allowed(method, path)


def test_allowlist_ignores_query_string() -> None:
    assert_endpoint_allowed("GET", "/iserver/marketdata/snapshot?conids=123&fields=31")


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/iserver/account/orders"),
        ("POST", "/iserver/account/U1234567/order"),
        ("POST", "/iserver/account/U1234567/orders"),
        ("POST", "/iserver/account/U1234567/order/whatif"),
        ("POST", "/iserver/reply/abc123"),
        ("DELETE", "/iserver/account/U1234567/order/abc123"),
        ("GET", "/iserver/account/trades"),
        ("GET", "/iserver/scanner/params"),
        ("GET", "/hmds/history"),
        ("GET", "/md/snapshot"),
    ],
)
def test_forbidden_trading_and_source_endpoints_are_blocked(method: str, path: str) -> None:
    with pytest.raises(EndpointNotAllowedError):
        assert_endpoint_allowed(method, path)


@pytest.mark.parametrize("forbidden", ["order", "orders", "whatif", "reply", "trades"])
def test_allowlist_contains_no_trading_patterns(forbidden: str) -> None:
    assert all(forbidden not in rule.pattern.pattern.lower() for rule in ALLOWED_ENDPOINTS)
