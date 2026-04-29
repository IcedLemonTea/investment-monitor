from __future__ import annotations


def convert_usd_to_myr(value: float, rate: float | None) -> float | None:
    if rate is None:
        return None
    return value * rate
