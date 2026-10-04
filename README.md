# WORLD LAB

A research-oriented virtual civilization laboratory.

## Goal

WORLD LAB is designed as a persistent, multi-sector world simulation in which people, households, organizations, locations, resources, products, policies and events share one world state.

The first hard milestone is:

> Introduce a product, service, technology or policy into a calibrated population and measure how its effects propagate through connected sectors.

This is a simulation/research system, not a claim that the real world can be reproduced exactly.

## Architecture

- **World state** — people, households, organizations, locations and shared economic/social state.
- **Time engine** — deterministic event scheduling and autonomous daily/monthly/yearly progression.
- **Population layer** — statistically grounded synthetic population generation.
- **Sector layer** — education, health, finance, industry, retail, transport, housing, agriculture, energy, government and media.
- **Experiment layer** — interventions and branching timelines.
- **Calibration layer** — compare simulated aggregates with reference data.
- **Validation layer** — regression tests and measurable acceptance criteria.

AI/LLM components are optional higher-level decision and analysis layers. Routine simulation must not depend on an LLM call for every person or every tick.

## Current milestone

### v0.3 — Calibration-ready kernel

The immediate objective is to build a small but scientifically testable regional world rather than pretending a tiny random population represents Earth.

Acceptance criteria will include:

1. reproducible population generation from explicit distributions;
2. correlated household/person attributes rather than independent random fields;
3. geographic assignment;
4. connected sector flows;
5. intervention propagation;
6. deterministic replay from a seed;
7. calibration error metrics;
8. tests that fail when core invariants are violated.

## Repository layout

```
worldlab/
  core/          # world state and time engine
  population/    # synthetic population generation
  sectors/       # connected civilization sectors
  experiments/   # interventions and timeline branching
  calibration/   # reference data and validation metrics
  tests/         # deterministic regression tests
scripts/         # Colab/local entry points
config/          # explicit simulation configuration
```

## Status

Early research implementation. Results are experimental and must be calibrated against external reference data before being treated as realistic.

## Development environment

The first development workflow is Google Colab/mobile-friendly Python, with GitLab as the source of truth.
