"""Read-only projections from the live WORLD LAB simulation kernel.

This module is an adapter, not a second simulation. Every value exposed here
comes from the supplied World instance or deterministic metadata derived from
that state.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import hashlib
import json
from typing import Any

from worldlab.core.world import World

from .contracts import EntitySnapshot, ReplayIdentity, WorldSnapshot, to_dict


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _entity_attributes(entity: Any) -> dict[str, Any]:
    if not is_dataclass(entity):
        raise TypeError("presentation entities must be dataclass instances")
    data = asdict(entity)
    for key in ("person_id", "household_id", "organization_id", "location_id"):
        data.pop(key, None)
    return data


class WorldPresenter:
    """Build deterministic, read-only presentation projections of a World."""

    def __init__(self, world: World, model_version: str = "0.8-dev") -> None:
        self._world = world
        self.model_version = model_version

    @property
    def world(self) -> World:
        return self._world

    def world_snapshot(self) -> WorldSnapshot:
        raw = self._world.snapshot()
        return WorldSnapshot(
            simulation_time=self._world.day,
            year=self._world.year,
            geography={
                "location_count": len(self._world.locations),
                "urban_location_count": sum(
                    1 for location in self._world.locations.values() if location.urban
                ),
            },
            population={
                "people": self._world.population,
                "weighted_people": self._world.weighted_population,
                "households": len(self._world.households),
                "organizations": len(self._world.organizations),
                "engine_snapshot": raw,
            },
            systems={
                "demography": {
                    "births_last_year": self._world.last_year_births,
                    "deaths_last_year": self._world.last_year_deaths,
                    "total_births": self._world.total_births,
                    "total_deaths": self._world.total_deaths,
                },
                "social": {
                    key: value for key, value in raw.items() if key.startswith("social_")
                },
                "labor": {
                    "working_age_employment_rate": raw["working_age_employment_rate"],
                },
            },
        )

    def entity_snapshots(self) -> tuple[EntitySnapshot, ...]:
        entities: list[EntitySnapshot] = []

        for person in sorted(self._world.people.values(), key=lambda item: item.person_id):
            entities.append(EntitySnapshot(
                entity_id=f"person:{person.person_id}",
                entity_type="person",
                attributes=_entity_attributes(person),
                parent_id=f"household:{person.household_id}",
                location_id=f"location:{person.location_id}",
            ))

        for household in sorted(
            self._world.households.values(), key=lambda item: item.household_id
        ):
            entities.append(EntitySnapshot(
                entity_id=f"household:{household.household_id}",
                entity_type="household",
                attributes=_entity_attributes(household),
                location_id=f"location:{household.location_id}",
            ))

        for organization in sorted(
            self._world.organizations.values(), key=lambda item: item.organization_id
        ):
            entities.append(EntitySnapshot(
                entity_id=f"organization:{organization.organization_id}",
                entity_type="organization",
                attributes=_entity_attributes(organization),
                location_id=f"location:{organization.location_id}",
            ))

        for location in sorted(
            self._world.locations.values(), key=lambda item: item.location_id
        ):
            entities.append(EntitySnapshot(
                entity_id=f"location:{location.location_id}",
                entity_type="location",
                attributes=_entity_attributes(location),
                location_id=f"location:{location.location_id}",
            ))

        return tuple(entities)

    def replay_identity(
        self,
        scenario_id: str = "live-world",
        parent_branch: str | None = None,
        evidence_snapshot: str | None = None,
    ) -> ReplayIdentity:
        input_snapshot = hashlib.sha256(
            _stable_json({
                "world": to_dict(self.world_snapshot()),
                "entities": [to_dict(entity) for entity in self.entity_snapshots()],
            }).encode("utf-8")
        ).hexdigest()
        return ReplayIdentity(
            model_version=self.model_version,
            scenario_id=scenario_id,
            parent_branch=parent_branch,
            random_seed=self._world.seed,
            input_snapshot=input_snapshot,
            evidence_snapshot=evidence_snapshot,
        )

    def export(self, scenario_id: str = "live-world") -> dict[str, Any]:
        """Return a JSON-compatible, read-only presentation payload."""
        return {
            "world": to_dict(self.world_snapshot()),
            "entities": [to_dict(entity) for entity in self.entity_snapshots()],
            "replay": to_dict(self.replay_identity(scenario_id=scenario_id)),
        }
