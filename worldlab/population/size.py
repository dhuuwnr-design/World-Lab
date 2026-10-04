"""Population-size controls for WORLD LAB.

A simulation may represent a fixed number of people or the full size of a
reference population. Keeping this choice explicit prevents "all people" from
being an accidental default.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PopulationSize:
    """Describe how many synthetic people to instantiate."""

    mode: str = "fixed"
    people: Optional[int] = None
    fraction: Optional[float] = None
    reference_people: Optional[int] = None

    def resolve(self) -> int:
        if self.mode == "fixed":
            if self.people is None or self.people <= 0:
                raise ValueError("fixed population requires people > 0")
            return self.people
        if self.mode == "full":
            if self.reference_people is None or self.reference_people <= 0:
                raise ValueError("full population requires reference_people > 0")
            return self.reference_people
        if self.mode == "fraction":
            if self.reference_people is None or self.reference_people <= 0:
                raise ValueError("fraction population requires reference_people > 0")
            if self.fraction is None or not 0.0 < self.fraction <= 1.0:
                raise ValueError("fraction must be in (0, 1]")
            return max(1, round(self.reference_people * self.fraction))
        raise ValueError("mode must be 'fixed', 'fraction', or 'full'")
