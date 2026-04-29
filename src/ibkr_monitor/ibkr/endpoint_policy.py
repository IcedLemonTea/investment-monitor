from __future__ import annotations

import re
from dataclasses import dataclass

from ibkr_monitor.ibkr.errors import EndpointNotAllowedError


@dataclass(frozen=True)
class EndpointRule:
    method: str
    pattern: re.Pattern[str]

    def matches(self, method: str, path: str) -> bool:
        return self.method == method.upper() and self.pattern.fullmatch(path) is not None


ALLOWED_ENDPOINTS: tuple[EndpointRule, ...] = (
    EndpointRule("POST", re.compile(r"/tickle")),
    EndpointRule("GET", re.compile(r"/iserver/auth/status")),
    EndpointRule("GET", re.compile(r"/portfolio/accounts")),
    EndpointRule("GET", re.compile(r"/portfolio/[^/]+/summary")),
    EndpointRule("GET", re.compile(r"/portfolio/[^/]+/ledger")),
    EndpointRule("GET", re.compile(r"/portfolio/[^/]+/allocation")),
    EndpointRule("GET", re.compile(r"/portfolio2/[^/]+/positions")),
    EndpointRule("GET", re.compile(r"/iserver/account/pnl/partitioned")),
    EndpointRule("GET", re.compile(r"/iserver/marketdata/snapshot")),
)


def assert_endpoint_allowed(method: str, path: str) -> None:
    normalized_path = path.split("?", maxsplit=1)[0]
    if any(rule.matches(method, normalized_path) for rule in ALLOWED_ENDPOINTS):
        return
    raise EndpointNotAllowedError(f"IBKR endpoint is not allowlisted: {method.upper()} {path}")
