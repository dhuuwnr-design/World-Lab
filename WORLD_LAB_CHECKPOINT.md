# WORLD LAB - Checkpoint

## Current branch
- feature/v0.8-presentation-architecture

## Latest verified milestone
- Commit: ada2e161ec4d32b90177c502d9f8d50371e1b986
- Message: Add deterministic world branching from checkpoints
- CI: GitHub Actions run #136 - SUCCESS
- Verified: 2026-10-05

## What is implemented
- Persistent individual cognitive agents attached to simulated people.
- Individual perception and decision contexts.
- Annual lived-world learning.
- Deterministic world state serialization and restoration.
- Stable event-handler replay restoration.
- Typed presentation/science contracts.
- Event metadata and provenance/causal-link projection.
- Deterministic branching from exact replay checkpoints.
- Branch isolation and checkpoint round-trip regression tests.

## Current architectural meaning
WORLD LAB can now create an exact world state, preserve its identity, and fork independent histories from that state. This is the foundation for counterfactual civilization experiments.

## Next major build
Implement the Intervention and Exposure Engine:
1. Define interventions, technologies, and policies as explicit mechanisms.
2. Define configurable population scopes: selected people, households, geography, fractions, and deterministic sampling.
3. Define exposure, access, and adoption rules over time.
4. Apply interventions deterministically to a branch without mutating its parent.
5. Record provenance, evidence, uncertainty, and causal mechanism IDs.
6. Compare baseline versus intervention branches through measurable divergence.
7. Test deterministic replay, scope correctness, branch isolation, and long-horizon divergence.

## Progress estimate
This is an engineering roadmap estimate, not a measured scientific completeness score.
- Current engine foundation: approximately 25-30% of the eventual WORLD LAB vision.
- 50% milestone target: a usable civilization experiment core where a user can create a baseline, select a population scope, introduce an intervention, run years or generations, branch alternatives, and inspect explainable measurable divergence with uncertainty and provenance.
- Full target: the above plus broad calibrated real-world systems, large-scale performance, geography, culture, economics, health, education, institutions, environment, migration feedbacks, validation against historical data, mature branching and replay, and the civilization-scale presentation layer.
- Percentages must be revised as capabilities become concrete; they must never be presented as proof that the model is a replica of reality.

## Continue rule
When the user says Continue or Work on World Lab, inspect this checkpoint and the actual repository state first, verify the latest CI, then continue implementation from the next major build. Do not stop at a trivial code correction.
