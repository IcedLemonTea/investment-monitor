from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Target:
    ticker: str
    display_ticker: str
    target_percent: float

    @property
    def target_weight(self) -> float:
        return self.target_percent / 100


def load_targets(path: Path) -> list[Target]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    targets = [
        Target(
            ticker=item["ticker"],
            display_ticker=item["display_ticker"],
            target_percent=float(item["target_percent"]),
        )
        for item in raw["targets"]
    ]
    validate_targets(targets)
    return targets


def validate_targets(targets: list[Target]) -> None:
    total = sum(target.target_percent for target in targets)
    if round(total, 6) != 100:
        raise ValueError(f"Target percentages must total 100, got {total}")
