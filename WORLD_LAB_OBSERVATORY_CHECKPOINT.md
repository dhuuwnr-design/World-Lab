# WORLD LAB OBSERVATORY CHECKPOINT

Date: 2026-10-05

## Completed
- Added a typed ObservatorySnapshot presentation contract.
- Added causal lineage to IndividualAgentSnapshot.
- WorldPresenter can expose civilization-level state, entity counts, selected entity, and causal-trace counts.
- People View can now include the causal lineage that led to a person.
- The observatory remains a read-only projection over the simulation; it does not create a second simulation.

## Current architecture
Civilization state -> entity hierarchy -> individual agent -> decisions/perception -> causal lineage.

## Next
Build scenario branching contracts/execution so the observatory can compare the same world under different interventions and follow divergent futures.
