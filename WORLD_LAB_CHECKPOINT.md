# WORLD LAB - Checkpoint

## Current branch
- `feature/v0.8-presentation-architecture`

## Latest verified milestone
- Commit: `3b769c27ae5ef7a08b3e6508a4837ee18e6df882`
- Deterministic intervention/exposure engine repaired and baseline-vs-scenario divergence metrics added.
- CI for `eea8f10b7909bdb81d8d155b0babd1d6263b9fa3`: SUCCESS (run #139).
- CI for `3b769c27ae5ef7a08b3e6508a4837ee18e6df882`: SUCCESS (run #140).

## Current implementation milestone
- Intervention & Exposure Engine is active and tested.
- Supports declarative population scopes, deterministic exposure/access sampling, individual-agent adoption decisions, measurable person effects, belief learning, exposure history serialization, and branch-safe application.
- `worldlab/experiments/metrics.py` now measures weighted population, employment, income, money, health, education, and social-state aggregates and computes deterministic baseline-vs-scenario deltas plus a normalized distance.
- Metrics explicitly describe model-output divergence and do not claim real-world causal truth.

## Scientific boundary
- Intervention outcomes are model outputs, not predictions of the real world.
- Evidence references and uncertainty are explicit fields.
- Population sampling does not consume the core world's RNG, preserving reproducibility.
- Individual agents drive adoption when available; the engine does not encode country/class personality stereotypes.

## Next major build
1. Connect intervention lifecycle to persistent event/replay declarations.
2. Persist intervention definitions and intervention-engine state inside replay checkpoints.
3. Add time-varying exposure/adoption and diffusion through relationships/organizations.
4. Build scenario contracts that bind branch provenance, intervention, mechanism, evidence, uncertainty, and metrics.
5. Expand calibration/validation against real historical trajectories.

## Progress estimate
- Current: approximately 32% of the eventual WORLD LAB vision.
- 50% target: usable civilization experiment core with interventions, population selection, individual decisions, multi-year branching, measurable divergence, uncertainty/provenance, and validation gates.
- Full target: calibrated civilization-scale world model, broad coupled systems, large-scale performance, historical validation, mature branching/replay, and the civilization-observatory presentation layer.

## Continue rule
On `Continue`, inspect this checkpoint and the repository tip, verify the latest CI result, then continue the next major build. Do not stop at trivial corrections or invent unverified project state.
