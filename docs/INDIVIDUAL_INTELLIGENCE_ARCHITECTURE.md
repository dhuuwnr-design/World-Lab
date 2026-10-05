# Individual Intelligence Architecture

WORLD LAB should model each simulated person as an individual decision-making agent, rather than assigning a country/class rule that directly determines behavior.

## Principle

A person's action emerges from:
- persistent goals and priorities
- beliefs and learned information
- bounded memory
- current social/emotional state
- relationships and observed behavior
- resources and constraints
- perceived opportunities and risks
- institutions, culture, media and environment
- life history and previous decisions

Country, class and generation are contextual influences, not personality templates.

## Architecture

Person
-> Individual Cognitive State
-> Perception
-> Memory / Learning
-> Belief update
-> Goal appraisal
-> Candidate actions
-> Decision
-> World interaction
-> Consequence
-> Learning

The simulation engine remains deterministic when a seed is fixed.

## Scale strategy

Do not call a large language model for every person on every simulation tick. That would be computationally wasteful and would make long historical runs difficult to reproduce.

Instead:
1. Every person receives an individual cognitive agent.
2. Routine cognition uses a fast bounded model.
3. More expensive reasoning can be activated selectively for important agents, unusual situations, interviews, or high-resolution studies.
4. Population-scale experiments can use representative agents while preserving weighted distributions.
5. Agent state must be checkpointable and replayable.

## Scientific boundary

The agents are artificial decision models, not claims of human consciousness or exact human psychology. Their mechanisms must be calibrated and validated against observed behavior.

## Long-term target

This layer enables experiments such as:

"Introduce a new technology to 10,000 selected people in 2026 and follow how their decisions, relationships, employment, households, migration, beliefs, adoption and descendants change over 30 years."

The important result is not one hard-coded outcome. It is a distribution of possible trajectories with explicit assumptions, uncertainty, and reproducible branches.
