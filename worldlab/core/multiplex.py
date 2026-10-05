"""Multiplex relationship graph for WORLD LAB.

A person can simultaneously relate to another person through multiple contexts.
Each context is stored independently instead of being collapsed into one edge.
"""

from typing import Iterable
from .social import Relationship


def add(graph: dict[tuple[int, int, str], Relationship], relationship: Relationship) -> None:
    relationship.validate()
    graph[(relationship.source_id, relationship.target_id, relationship.relationship_type)] = relationship


def remove_person_layer(graph: dict[tuple[int, int, str], Relationship], person_id: int, layers: Iterable[str]) -> None:
    layer_set = set(layers)
    for key in list(graph):
        source, target, layer = key
        if layer in layer_set and (source == person_id or target == person_id):
            del graph[key]


def neighbors(graph: dict[tuple[int, int, str], Relationship], person_id: int, *, layer: str | None = None) -> list[Relationship]:
    return [
        relationship
        for (source, target, relationship_layer), relationship in sorted(graph.items())
        if source == person_id and (layer is None or relationship_layer == layer)
    ]
