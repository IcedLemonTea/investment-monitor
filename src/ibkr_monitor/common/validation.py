from __future__ import annotations


def require_non_empty(value: str, field_name: str) -> str:
    if not value:
        raise ValueError(f"{field_name} must not be empty")
    return value
