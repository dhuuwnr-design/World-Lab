"""Explicit simulation population sizing."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PopulationConfig:
    people: int = 10_000
    seed: int = 42

    def validate(self) -> None:
        if self.people <= 0:
            raise ValueError("people must be positive")
        if self.people > 10_000_000:
            raise ValueError(
                "people exceeds the default safety limit; use an explicit "
                "large-scale execution profile"
            )
