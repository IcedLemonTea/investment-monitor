from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentContract:
    ticker: str
    display_ticker: str
    asset_class: str
    currency: str
