from __future__ import annotations


def redact_secret(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return f"{value[:2]}****{value[-2:]}"
