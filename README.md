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
- **Population layer** — statistically grounded synthetic populations with explicit representation weights.
- **Demography** — parameter-driven fertility and mortality mechanics; real rates remain external calibration inputs.
- **Social layer** — heterogeneous individual affective/social states, relationships and context variables; no country stereotype is hard-coded.
- **Sector layer** — education, health, finance, industry, retail, transport, housing, agriculture, energy, government and media can mutate the same world.
- **Experiment layer** — interventions and branching timelines.
- **Calibration layer** — compare simulated aggregates with reference data.
- **Validation layer** — regression tests and measurable acceptance criteria.

AI/LLM components are optional higher-level analysis tools. Routine simulation must remain deterministic and reproducible without an LLM call for every person or tick.

## Current milestone

**v0.6 — Human/social state foundation**

The kernel now has demographic lifecycle mechanics, representative-population weights, deterministic event-boundary ordering, and heterogeneous social/affective state. Real-world calibration data is still external and must be sourced and documented before results are described as realistic.

See WORLD_LAB_CHECKPOINT.md for the durable project state and next research target.

## Development environment

The first development workflow is Google Colab/mobile-friendly Python, with GitHub as the current mirrored source of truth.
