from __future__ import annotations

import pytest

from ibkr_monitor.ibkr.client_portal import ClientPortalClient, JsonValue
from ibkr_monitor.ibkr.errors import EndpointNotAllowedError


class MockTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, str] | None]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> JsonValue:
        self.calls.append((method, path, params))
        return {"ok": True, "path": path}


def test_client_uses_injected_transport_for_allowlisted_request() -> None:
    transport = MockTransport()
    client = ClientPortalClient(transport=transport)

    response = client.auth_status()

    assert response == {"ok": True, "path": "/iserver/auth/status"}
    assert transport.calls == [("GET", "/iserver/auth/status", None)]


def test_client_blocks_non_allowlisted_request_before_transport() -> None:
    transport = MockTransport()
    client = ClientPortalClient(transport=transport)

    with pytest.raises(EndpointNotAllowedError):
        client.request("GET", "/not/allowed")

    assert transport.calls == []


def test_marketdata_snapshot_passes_query_params_to_transport() -> None:
    transport = MockTransport()
    client = ClientPortalClient(transport=transport)

    client.marketdata_snapshot(conids="123", fields="31,84")

    assert transport.calls == [
        ("GET", "/iserver/marketdata/snapshot", {"conids": "123", "fields": "31,84"})
    ]
