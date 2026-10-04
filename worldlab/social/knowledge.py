from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

@dataclass
class AgentKnowledge:
    beliefs: Dict[str, float] = field(default_factory=dict)
    confidence: Dict[str, float] = field(default_factory=dict)
    observations_seen: int = 0

    def observe(self, observations: Mapping[str, Any]) -> None:
        self.observations_seen += len(observations)
        for key, value in observations.items():
            if isinstance(value, (int, float)):
                previous = self.beliefs.get(key)
                if previous is None:
                    self.beliefs[key] = float(value)
                    self.confidence[key] = 0.25
                else:
                    self.beliefs[key] = previous + 0.25 * (float(value) - previous)
                    self.confidence[key] = min(1.0, self.confidence.get(key, 0.25) + 0.1)

    def knows(self, key: str) -> bool:
        return key in self.beliefs

    def estimate(self, key: str, default: float = 0.0) -> float:
        return self.beliefs.get(key, default)

def create_agent_knowledge() -> AgentKnowledge:
    return AgentKnowledge()
