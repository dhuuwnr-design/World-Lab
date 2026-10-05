# WORLD LAB CHECKPOINT

## 2026-10-05 — v0.8 engine-to-presentation integration

### Verified repository state
- Repository: `dhuuwnr-design/World-Lab`
- Branch: `feature/v0.8-presentation-architecture`
- Latest implementation commit: `20da21bb6b81070dd94b655d2cab515feb6cf6a2`
- GitHub access through the connected Composio account is active.
- The earlier v0.8 architecture commit remains in history; this checkpoint advances it with executable engine integration.

### Implemented in this checkpoint
- Added `worldlab/presentation/presenter.py` with a read-only `WorldPresenter`.
- `WorldPresenter.world_snapshot()` projects the real `World.snapshot()` into the typed `WorldSnapshot` contract.
- Existing engine snapshot fields are preserved verbatim under `population.engine_snapshot`; the presenter does not replace or reinterpret them.
- Added deterministic entity projections for people, households, organizations and locations, preserving real IDs, parent household relationships and locations.
- Added deterministic replay identity hashing from the actual projected world/entity state plus the model version and simulation seed.
- Added a JSON-compatible `export()` payload containing world, entity and replay projections.
- Added regression tests proving:
  - real engine snapshot fields are preserved;
  - entity IDs and relationships map to actual simulation state;
  - presentation export is read-only;
  - identical world state + seed produce identical replay identities.
- Updated presentation package exports to expose `WorldPresenter`.

### Scientific / architectural boundary
- The presenter is an adapter, not a second simulation.
- It does not invent events, causes, evidence or future outcomes.
- No event provenance was fabricated because the current event queue does not yet retain immutable event records after dispatch.
- Event capture/provenance is therefore still a separate engine task.

### Verification status
- Implementation commit was successfully created through Composio/GitHub.
- GitHub Actions result for this new commit has not yet been verified as completed; do not treat CI as passed until a completed run is observed.

### Next target
Add immutable event capture to the actual event engine without changing simulation behavior, then project those real events into `EventRecord` with provenance only where provenance exists. After that, build a presenter-level scenario/replay service over actual runs.
