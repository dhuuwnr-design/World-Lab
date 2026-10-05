# WORLD LAB CAUSAL LINK CHECKPOINT

Date: 2026-10-05
Branch: feature/v0.8-presentation-architecture
Latest implementation commit: 86d58a939dd70837439f118c6443d7f9aafb9f55

## Verified progress

- Structured EventMetadata is now the explicit semantic boundary for scheduled events.
- Legacy schedule(day, callback, name) behavior remains supported.
- Event presentation records expose only declared actors, mechanisms, and effects.
- causal_links(world) now projects declared event metadata into CausalLink records.
- Each link carries declared evidence references and uncertainty.
- No causal relationship is inferred from callback behavior, event names, or observed outcomes.
- Tests cover multi-actor/multi-mechanism projection and legacy events producing no causal links.

## CI

Commit d77b50c8f3789a07de62a9d82ef9ca097a38c6c7 completed GitHub Actions successfully.

Commit 86d58a939dd70837439f118c6443d7f9aafb9f55 has GitHub Actions check `test` currently queued. It must be rechecked before declaring this checkpoint green.

## Next

Build deterministic scenario branching/replay from an explicit world-state checkpoint rather than copying runtime callbacks. The replay identity must cover model version, scenario, seed, input snapshot and evidence snapshot, and branches must produce independently reproducible trajectories.
