# WORLD LAB experience layer

WORLD LAB should be represented as a living world, not a dashboard that happens to contain simulation numbers.

## Core interaction
Build a world -> watch it live -> inspect it -> change one condition -> let time pass -> compare what emerged.

The product has three synchronized representations:
1. World — people, families, cities, organizations, technology, infrastructure and environment.
2. Experiment — scenarios, interventions, branches, elapsed time and comparisons.
3. Evidence — observations, calibration, validation and uncertainty.

Research-oriented simulation environments demonstrate the value of interactive displays, inspection and experiment modes. NetLogo emphasizes approachable exploration and learning, while GAMA supports multiple displays, agent inspection, GUI experiments and batch/headless execution. WORLD LAB should take those lessons without copying their interfaces.

## World Observatory
The first real product surface should be a World Observatory containing:
- spatial world/map canvas
- current year and generation
- play/pause and simulation speed
- persistent time bar
- population/economy/technology summary
- selectable map layers
- event markers
- inspect action
- intervention action
- Reality Check status
- baseline/branch comparison

Suggested map layers:
People | Families | Cities | Economy | Technology | Energy | Transport | Environment | Institutions

Do not show every layer simultaneously.

## Time Machine
Time is a primary interaction. Users can scrub through history, jump by year/decade/generation, pause, inspect a historical point, create a branch, return to a branch point and compare trajectories.

Event markers can include technology introductions, policy changes, migration shocks, wars, pandemics, financial crises, disasters and resource discoveries. The interface must distinguish observed historical events from simulated consequences.

## Micro to macro
The same world state should support:
Civilization -> region -> city -> neighbourhood -> household -> person

A person view can show life timeline, household, education, work, income/wealth, relationships, migration, health, social state and major life events. Internal variables such as stress or perceived respect must be presented as model estimates, never literal access to a person's thoughts.

## Intervention Studio
Interventions should enter causal mechanisms, not directly overwrite final outcomes.

Example:
technology introduced
-> awareness
-> materials
-> manufacturing
-> infrastructure
-> affordability
-> usefulness
-> individual decisions
-> adoption
-> demand
-> production
-> jobs
-> migration/wealth/etc.

Users should inspect active mechanisms before starting a run.

## Branching
A branch is visually obvious:
2026 -> 2035 -> 2050
              -> World A: baseline
              -> World B: intervention

Each branch retains world state, configuration, random seed, model version, evidence/calibration profile and intervention history.

## Discovery
After a run, answer:
- What changed?
- Why did it change?
- Who was affected?
- Where did it happen?
- When did trajectories diverge?
- What unexpected consequences emerged?
- How uncertain is the result?

Unexpected consequences must come from simulation evidence and repeated runs, not AI-generated storytelling.

## Reality Check
Every important result should expose evidence status. Example:
Population — calibrated
Labour participation — partially calibrated
Technology adoption — experimental
Social norms — evidence-backed profile, incomplete calibration
Long-term GDP — experimental

Then show source, geography, observation period, variables, calibration target, validation target, limitations and uncertainty.

Never collapse this into one fake realism score.

## Research mode
Advanced users can reveal parameters, mechanisms, distributions, calibration, validation, sensitivity, stochastic runs, batch experiments, reproducibility and raw outputs. Normal users should not need these controls.

## Follow mode
Users can pin and follow a person, family, city, technology, industry, generation, region or institution. The selected entity remains visible while the simulation advances, connecting individual experience to civilization-scale change.

## Representation principles
WORLD LAB should feel serious, cinematic but information-dense, spatial, alive, calm during normal evolution, visually dramatic only when genuine system changes occur, transparent about uncertainty and original.

Avoid giant KPI dashboards as the home screen, endless parameter forms, fake 3D merely for appearance, instant-result animations, "AI predicts humanity" framing, unexplained confidence scores and national stereotypes as fixed personality rules.

## Progressive complexity
Explorer — simple world view and meaningful controls.
Student — guided experiments and explanations.
Teacher — shared experiments and comparisons.
Researcher — calibration, uncertainty, batch experiments and validation.
Developer — APIs and model inspection.

## First representation milestone
Build the first World Observatory around the existing engine:
map/state canvas + timeline + world metrics + inspection + intervention + causal explanation + Reality Check + branch comparison.

The representation layer must remain independent from simulation state so multiple visual representations can inspect the same underlying world.

## Product principle
WORLD LAB should feel like a place you enter, not a report you read.

The simulation creates the world.
The experience layer lets humans see, question, alter and investigate it.
The evidence layer tells them how strongly what they see is grounded in reality.
