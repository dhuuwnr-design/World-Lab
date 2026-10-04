"""Sparse social network and reputation dynamics."""
from dataclasses import dataclass
from typing import Dict, Tuple
from worldlab.core.world import World

@dataclass
class SocialTie:
    source: int
    target: int
    strength: float = 0.1
    trust: float = 0.5
    frequency: float = 0.1
    family: bool = False

class SocialNetwork:
    def __init__(self):
        self.ties: Dict[Tuple[int, int], SocialTie] = {}

    def get(self, source: int, target: int):
        return self.ties.get((source, target))

    def connect(self, source: int, target: int, strength: float = 0.2,
                trust: float = 0.5, family: bool = False):
        if source == target:
            return
        self.ties[(source, target)] = SocialTie(
            source, target, max(0, min(1, strength)),
            max(0, min(1, trust)), max(0, min(1, strength)), family
        )

    def neighbors(self, person_id: int):
        return [t for (source, _), t in self.ties.items() if source == person_id]

    def initialize_household_ties(self, world: World):
        """Compatibility entry point: create initial reciprocal household ties."""
        self.ties.clear()
        for household in world.households.values():
            members = list(household.member_ids)
            for i, source in enumerate(members):
                for target in members[i + 1:]:
                    self.connect(source, target, 0.75, 0.70, True)
                    self.connect(target, source, 0.75, 0.70, True)

    def annual_update(self, world: World):
        # Existing household ties are maintained; newly created households are added.
        known = set(self.ties)
        for household in world.households.values():
            members = list(household.member_ids)
            for i, source in enumerate(members):
                for target in members[i + 1:]:
                    if (source, target) not in known:
                        self.connect(source, target, 0.75, 0.70, True)
                        self.connect(target, source, 0.75, 0.70, True)

        for tie in list(self.ties.values()):
            if tie.source not in world.people or tie.target not in world.people:
                continue
            a = world.people[tie.source]
            b = world.people[tie.target]
            same = a.location_id == b.location_id
            tie.strength = min(1.0, 0.94 * tie.strength + (0.08 if same else -0.015))
            tie.frequency = 0.90 * tie.frequency + 0.10 * (1 if same else 0)
            tie.trust = max(0.0, min(1.0, 0.97 * tie.trust + 0.03 * tie.frequency))
        self._update_local_respect(world)

    def _update_local_respect(self, world: World):
        for person in world.people.values():
            state = getattr(person, "social", None)
            if state is None:
                continue
            weighted = []
            total = 0.0
            for tie in self.neighbors(person.person_id):
                other = world.people.get(tie.target)
                other_state = getattr(other, "social", None) if other else None
                if other_state is None:
                    continue
                achievement = 0.5 * other_state.status_security + 0.5 * other_state.perceived_respect
                weighted.append(tie.strength * (0.5 * tie.trust + 0.5 * achievement))
                total += tie.strength
            if total:
                peer_signal = sum(weighted) / total
                state.perceived_respect = max(
                    0.0, min(1.0, 0.88 * state.perceived_respect + 0.12 * peer_signal)
                )
                state.wellbeing = max(
                    0.0, min(1.0, 0.93 * state.wellbeing + 0.07 * state.perceived_respect)
                )
