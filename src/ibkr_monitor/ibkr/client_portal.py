from __future__ import annotations

from dataclasses import dataclass

from ibkr_monitor.ibkr.endpoint_policy import assert_endpoint_allowed


@dataclass(frozen=True)
class ClientPortalRequest:
    method: str
    path: str

    def validate(self) -> None:
        assert_endpoint_allowed(self.method, self.path)
