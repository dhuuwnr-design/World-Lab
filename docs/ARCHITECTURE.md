# WORLD LAB architecture

WORLD LAB is designed as a **simulation laboratory**, not a single predictive model.

## Runtime layers

**World state** → people, households, organizations and places.

**Mechanisms** → demographic, social, economic, technological and environmental processes.

**Experiment layer** → scenarios, interventions, seeds, snapshots and comparisons.

**Evidence layer** → datasets, calibration parameters, validation targets and uncertainty.

**Presentation layer** → maps, dashboards, timelines and experiment reports.

The key rule is that presentation never changes model state. A saved experiment must contain
enough metadata to reproduce the run: model version, configuration, random seed, interventions,
calibration profile and output schema.

## Simulation clock

The engine has a continuous day counter with annual process boundaries. Daily events may be
scheduled, while demographic and other slow processes run at the annual boundary. This lets us
represent events on different timescales without pretending every human process happens once per
year.

## Causality before convenience

An intervention must enter a real mechanism. For example, a technology intervention should not
directly set adoption to 80%. It should change a causal input such as knowledge, production
capacity, infrastructure, price or availability. Adoption then emerges over time.

Likewise, a policy intervention should modify an institution, budget, incentive or constraint,
not directly write the final population/GDP outcome.

## Scale strategy

The engine should support progressively larger worlds:

- **micro**: 100–10,000 agents for inspection and teaching;
- **meso**: 10,000–1,000,000 for serious scenario exploration;
- **macro**: beyond 1,000,000 using aggregation, spatial indexing, vectorized state and/or distributed execution where necessary.

Individual-level resolution is a design choice, not a promise that every run will use one Python
object per real-world person.

Large ABM platforms demonstrate that spatial/data-driven simulation can reach millions of agents,
but WORLD LAB must benchmark its own architecture before making performance claims. citeturn0search0

## Model documentation contract

Every mature mechanism should have an ODD-style description: purpose, state variables/scales,
process scheduling, design concepts, initialization, inputs and submodels. ODD is widely used to
make ABMs understandable and reproducible. citeturn0search9turn0search11

Validation is contextual rather than a single final test. The validation protocol must track
model construction, parameter inference, uncertainty, simulation and interpretation together.
citeturn0search5
