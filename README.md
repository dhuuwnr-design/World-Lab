# WORLD LAB

A research-oriented virtual civilization laboratory.

WORLD LAB is a persistent multi-sector world simulation in which people, households, organizations, locations, resources, products, policies and events share one world state.

## Current milestone

**v0.7 — Evidence calibration foundation**

The engine now separates simulation mechanics from externally sourced calibration inputs. Calibration records preserve source/year/unit provenance; adapters use explicit mappings; validation produces measurable comparison reports.

The project does **not** claim that these mechanics reproduce real human societies. Country-specific distributions and causal relationships must be calibrated and validated from evidence.

## Data foundations

- UN World Population Prospects 2024 for demographic trajectories. The UN methodology uses age/sex-specific fertility, mortality and net international migration in its cohort-component framework. citeturn0search24turn0search25
- World Bank Indicators API for programmatic time-series indicators. The API supports date ranges, multiple indicators and JSON output without API keys. citeturn0search0turn0search1

## Architecture

- World state
- Deterministic time/event engine
- Representative population
- Demography
- Human/social state
- Evidence calibration
- Validation
- Future sectors: education, health, labor, finance, industry, housing, transport, agriculture, energy, government and media

Routine simulation must remain deterministic and must not require an LLM call per person/tick.
