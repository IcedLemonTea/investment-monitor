from __future__ import annotations


class IbkrMonitorError(Exception):
    """Base project exception."""


class EndpointNotAllowedError(IbkrMonitorError):
    """Raised when code attempts to use a non-allowlisted IBKR endpoint."""
