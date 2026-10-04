from dataclasses import dataclass, field
from typing import Dict, Mapping


@dataclass
class LearningState:
    experience_count: int = 0
    prediction_errors: Dict[str, float] = field(default_factory=dict)

    def learn_from_outcome(
        self,
        predictions: Mapping[str, float],
        outcomes: Mapping[str, float],
        rate: float = 0.2,
    ) -> Dict[str, float]:
        if not 0.0 <= rate <= 1.0:
            raise ValueError("rate must be between 0 and 1")
        errors: Dict[str, float] = {}
        for key, predicted in predictions.items():
            if key not in outcomes:
                continue
            error = float(outcomes[key]) - float(predicted)
            previous = self.prediction_errors.get(key, 0.0)
            self.prediction_errors[key] = previous + rate * (error - previous)
            errors[key] = error
        self.experience_count += 1
        return errors


def update_estimate(
    estimate: float,
    outcome: float,
    learning_rate: float = 0.2,
) -> float:
    if not 0.0 <= learning_rate <= 1.0:
        raise ValueError("learning_rate must be between 0 and 1")
    return estimate + learning_rate * (outcome - estimate)
