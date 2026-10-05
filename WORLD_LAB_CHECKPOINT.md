# WORLD LAB CHECKPOINT

## 2026-10-05 — v0.8 full deterministic world restore

### Verified repository state
- Repository: `dhuuwnr-design/World-Lab`
- Branch: `feature/v0.8-presentation-architecture`
- Replay foundation CI: **success** for `863bda6ad317dd6d6b7791cd700ef6a8b2a41a3d`.
- Latest implementation commit: `4f4264ad298b128e5b1da3367d0c14f43c2d7571`.
- CI for `4f4264ad...`: **in progress** when this checkpoint was written; not yet verified green.

### Implemented
- `World.state_dict()` serializes complete mutable core simulation state:
  - people
  - individual agents and bounded memories/beliefs
  - social states
  - households
  - organizations
  - locations
  - relationships
  - social contexts
  - demographic profile
  - simulation counters/time
  - deterministic RNG state
- `World.from_state_dict()` restores those structures and RNG state.
- `ReplayCheckpoint.capture(world, identity)` now captures the complete mutable world state rather than only the aggregate snapshot.
- `ReplayCheckpoint.restore_world()` restores a checkpoint when there are no pending runtime callbacks.
- Added exact state restoration tests and checkpoint restoration tests.
- Callback-free event declarations remain separate from runtime callbacks.

### Verification boundary
The new restore path is designed to make the core world reproducible, but **pending scheduled callbacks are intentionally not restored yet**. A checkpoint with pending callbacks raises a clear error instead of silently producing an incorrect branch. Full event-handler restoration is the next required step before arbitrary mid-event checkpoints can branch.

### Next implementation target
1. Verify CI for `4f4264ad...`.
2. Add deterministic event-handler registration keyed by stable event type/name so declared pending events can be restored without serializing Python callbacks.
3. Implement explicit branch creation with parent branch, divergence day, scenario ID, seed and model version.
4. Add selective technology/policy exposure to a population scope and connect exposure to individual decisions and declared consequence events.
5. Run baseline/intervention trajectories and compare outcomes with uncertainty/provenance.
6. Continue scaling the individual-agent model without requiring an LLM call per person/tick.
