"""Hierarchical geographic structure for WORLD LAB."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class GeographyNode:
    geography_id: int
    name: str
    level: str
    parent_id: Optional[int] = None
    location_id: Optional[int] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("geography name must not be empty")
        if not self.level.strip():
            raise ValueError("geography level must not be empty")
        if self.latitude is not None and not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        if self.longitude is not None and not -180.0 <= self.longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180")


def ancestry(nodes: Dict[int, GeographyNode], geography_id: int) -> List[GeographyNode]:
    result: List[GeographyNode] = []
    seen = set()
    current = geography_id
    while current is not None:
        if current in seen:
            raise ValueError("geography hierarchy contains a cycle")
        seen.add(current)
        node = nodes.get(current)
        if node is None:
            raise KeyError(f"unknown geography id: {current}")
        result.append(node)
        current = node.parent_id
    return result
