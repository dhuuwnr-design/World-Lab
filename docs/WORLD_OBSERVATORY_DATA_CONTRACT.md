# World Observatory data contract

The representation layer must consume a stable, read-only view of the simulation rather than reaching into model internals.

## Design rule

Simulation state -> presentation snapshot -> visual surfaces.

The Observatory can display the same snapshot through world overview, map layers, timeline, entity inspector, causal explanation, Reality Check and comparison. A visual component must not mutate simulation state directly.

## Observatory snapshot

### Time
- simulation year
- absolute day
- generation
- branch/world identifier

### Population
- population
- households
- births/deaths
- age structure
- migration

### Economy
- employment
- unemployment
- income
- wealth
- production
- prices

### Technology
- technologies available
- awareness
- adoption
- infrastructure readiness

### Society
- wellbeing
- stress
- social ties
- family/community structure

### Physical world
- settlements
- transport
- energy
- land
- water
- environment

### Evidence
For every displayed metric: status, source identifiers, geography, observation period, calibration target, validation target and uncertainty.

## Entity inspection

The Observatory should support a common read-only, time-aware inspection interface for person, household, organization, location, technology, institution and region. Modelled psychological or social states must never be presented as direct access to subjective thoughts.

## Causal explanation

An explanation is a chain of model mechanisms, not an AI-generated story. Example: technology introduction -> awareness increased -> affordability improved -> adoption increased -> demand increased -> production expanded -> employment changed -> household income changed -> migration pressure changed. Each link should eventually reference its mechanism and evidence status.

## Branch comparison

Compare worlds using aligned simulation time and display absolute values, meaningful differences, percentage changes, uncertainty intervals and divergence point. Make intervention effects distinguishable from stochastic variation.

## Current boundary

The existing World.snapshot() is the first seed of this contract. It currently exposes population, households, organizations, labour, income, household money and social metrics. Future work should extend the snapshot without coupling presentation code to subsystem implementation details.
