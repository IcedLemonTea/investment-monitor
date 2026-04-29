from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from ibkr_monitor.ibkr.endpoint_policy import assert_endpoint_allowed

JsonValue = dict[str, Any] | list[Any] | str | int | float | bool | None


class ClientPortalTransport(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> JsonValue: ...


@dataclass(frozen=True)
class ClientPortalRequest:
    method: str
    path: str

    def validate(self) -> None:
        assert_endpoint_allowed(self.method, self.path)


@dataclass(frozen=True)
class ClientPortalClient:
    transport: ClientPortalTransport

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> JsonValue:
        ClientPortalRequest(method=method, path=path).validate()
        return self.transport.request(method.upper(), path, params=params)

    def tickle(self) -> JsonValue:
        return self.request("POST", "/tickle")

    def auth_status(self) -> JsonValue:
        return self.request("GET", "/iserver/auth/status")

    def portfolio_accounts(self) -> JsonValue:
        return self.request("GET", "/portfolio/accounts")

    def account_summary(self, account_id: str) -> JsonValue:
        return self.request("GET", f"/portfolio/{account_id}/summary")

    def account_ledger(self, account_id: str) -> JsonValue:
        return self.request("GET", f"/portfolio/{account_id}/ledger")

    def account_allocation(self, account_id: str) -> JsonValue:
        return self.request("GET", f"/portfolio/{account_id}/allocation")

    def account_positions(self, account_id: str) -> JsonValue:
        return self.request("GET", f"/portfolio2/{account_id}/positions")

    def pnl_partitioned(self) -> JsonValue:
        return self.request("GET", "/iserver/account/pnl/partitioned")

    def marketdata_snapshot(self, conids: str, fields: str) -> JsonValue:
        return self.request(
            "GET",
            "/iserver/marketdata/snapshot",
            params={"conids": conids, "fields": fields},
        )
