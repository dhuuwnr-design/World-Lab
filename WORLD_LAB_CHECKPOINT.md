# WORLD LAB CHECKPOINT

## 2026-10-05 — v0.8 individual intelligence: explicit perception context

### Verified repository state
- Repository: `dhuuwnr-design/World-Lab`
- Branch: `feature/v0.8-presentation-architecture`
- Latest implementation commit: `5dbab2fbd7abc443a58d52effe29aa49155be3c2`
- Previous implementation: `fc801911dbe7e6e7a6c5e7f6a481866e864ed4e9`
- CI for `fc801911...`: completed successfully.
- CI for `5dbab2f...`: in progress when this checkpoint was written; not yet verified green.

### Implemented
- `worldlab/core/agents.py`
  - Added explicit immutable `Perception` structure.
  - Added explicit `DecisionContext` structure joining perception, candidate actions and decision reason.
  - Added `IndividualAgent.perceive_context()` and `IndividualAgent.decide()` while preserving the existing `choose()` API.
- `worldlab/core/world.py`
  - Added `World.perception_for(person_id)`.
  - A person's perception now draws from currently simulated individual, household, relationship, organization, location and social-context state.
  - Signals are bounded to [0,1] before reaching the individual agent.
  - Added `World.decision_context_for()` for reproducible structured decisions.
  - Annual learning now records the richer current perception rather than wellbeing alone.
- `worldlab/tests/test_agent_perception.py`
  - Covers bounded perception.
  - Covers structured decision context.
  - Covers richer world-to-person perception.
  - Covers deterministic repeated context construction.

### Scientific boundary
The new transforms are interface mechanics, not calibrated claims about human psychology. Financial saturation constants and bounded mappings are provisional until evidence/calibration work assigns justified parameters. Country, class, culture, institutions, relationships and life history remain contextual mechanisms rather than deterministic personality stereotypes.

### Next implementation target
1. Verify CI for `5dbab2f...` and fix any regression before proceeding.
2. Represent action consequences as explicit serializable world events with declared metadata.
3. Add selective technology/policy exposure by population scope.
4. Build deterministic serializable world checkpoints and scenario branching/replay.
5. Compare baseline vs intervention trajectories with uncertainty/provenance.
6. Keep routine agents lightweight; reserve deeper reasoning for selected agents/experiments.

### Long-term WORLD LAB direction
Each simulated person remains an individual decision-maker with persistent memory, beliefs, goals, constraints and social context. The simulation should produce multi-year and multi-generation outcomes from interacting individuals and institutions, rather than directly assigning population-level outcomes.
