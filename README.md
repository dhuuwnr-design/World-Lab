# WORLD LAB

A research-oriented virtual civilization laboratory.

## Goal

WORLD LAB is designed as a persistent, multi-sector world simulation in which
people, households, organizations, locations, resources, products, policies,
and events share one world state.

The first hard milestone is:

> Introduce a product, service, technology, or policy into a calibrated
> population and measure how its effects propagate through connected sectors.

This is a simulation/research system, not a claim that the real world can be
reproduced exactly.

## Current milestone: v0.3 calibration layer

The v0.3 foundation now separates three concerns:

1. **Reference data** — explicit age/sex, household, employment, and spatial
   targets supplied by documented datasets.
2. **Synthetic population generation** — reproducible generation constrained by
   those targets.
3. **Validation** — measurable error reports rather than subjective claims of
   realism.

The reference layer deliberately contains no invented country statistics.
Regional adapters will supply official or documented data later.

### v0.3 acceptance criteria

- reproducible generation from a seed
- exact requested population count
- exact spatial population totals after integer allocation
- household membership consistency
- explicit reference-distribution validation
- NRMSE and relative absolute error
- failures when calibration error exceeds tolerance
- no sector-specific mini-worlds

## Architecture

- **World state** — people, households, organizations, locations and shared state.
- **Time engine** — deterministic event scheduling and annual progression.
- **Population layer** — synthetic population generation and calibration.
- **Sector layer** — education, health, finance, industry, retail, transport,
  housing, agriculture, energy, government, media and future modules.
- **Experiment layer** — interventions and branching timelines.
- **Calibration layer** — documented reference data and validation metrics.
- **AI/ML layer** — optional higher-level decisions, forecasting and analysis;
  routine simulation should not require an LLM call for every person/tick.

## Repository layout

```
worldlab/
  core/          # world state and time engine
  population/    # synthetic population generation
  sectors/       # connected civilization sectors
  experiments/   # interventions and timeline branching
  calibration/   # reference data and validation
  tests/         # deterministic regression tests
scripts/         # Colab/local entry points
config/          # explicit simulation configuration
```

## Development

The project is Python-first and can be developed from Google Colab/mobile.
GitHub is the active development mirror/workflow, with Composio providing the
repository automation layer.

## Status

Early research implementation. Results must be calibrated against external
reference data before being treated as realistic.
