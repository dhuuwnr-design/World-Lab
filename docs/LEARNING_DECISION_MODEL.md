# Learning-to-decision contract

WORLD LAB agents must not receive the simulator's ground truth as a hidden decision input.

The intended loop is:

1. perceive a bounded subset of world state;
2. store observations as knowledge with confidence;
3. form an expectation about an action;
4. act;
5. observe the consequence available to the agent;
6. update the expectation from prediction error;
7. make later choices using the updated internal estimate.

This is an implementation scaffold, not a claim that the current parameters reproduce human learning.

## Guardrails

- Decisions use acquired agent knowledge, not direct World object access.
- Learning is gradual and bounded.
- Exploration remains possible, so behavior is not perfectly deterministic.
- Randomness must be seedable for reproducible experiments.
- Parameters require empirical calibration before being interpreted as human behavior.

## Next integration target

Connect this loop to a real World Lab mechanism (employment, technology adoption, or household economic choices) so learning changes an observable world outcome rather than remaining an isolated cognitive test.
