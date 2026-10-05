# WORLD LAB CHECKPOINT

## 2026-10-05 — v0.8 presentation architecture

### Verified repository state
- v0.5 cumulative demographic + representative-population engine is merged into main.
- v0.6 human/social state exists on feature/v0.6-human-social-state.
- v0.7 evidence-calibration foundation exists on feature/v0.7-evidence-calibration at commit 86586532196d2966e451045fa33120fe3b0a1ea7.
- GitHub read access and repository admin/push permission for the connected account were verified on 2026-10-05.
- The v0.8 branch starts from feature/v0.7-evidence-calibration.

### Implemented in this checkpoint
- Defined three presentation modes: WORLD, LAB, SCIENCE.
- Defined scale-aware world navigation from planet to person.
- Defined Time Machine, Why Layer, People View, Meet the World, Branching Futures, and Reproducible Replay concepts.
- Defined serializable contracts for world snapshots, entities, events, scenarios, branches, causal links, validation, and provenance.
- Defined scientific-integrity rules for presentation and generated narrative.

### Critical architecture rule
Presentation is a view of simulation truth. It must not invent simulation facts or turn uncertain scenario outcomes into deterministic predictions.

### Next implementation target
Implement the presentation data contracts as typed Python models, add serialization/regression tests, then build a minimal read-only presenter API/view over real simulation snapshots. After that, add branching/replay metadata and evidence-linked WHY explanations.
