# WORLD LAB - Checkpoint

## Current branch
- `feature/v0.8-presentation-architecture`

## Latest verified milestone
- Commit: `2660c41bd5bea94a01d9a85be46ed24748ed1bf4`
- Deterministic world branching and checkpoint round-trip implemented.
- CI for branching implementation: SUCCESS (run #136).

## Current implementation milestone
- Intervention & Exposure Engine implemented in commit after this checkpoint.
- Supports declarative population scopes, deterministic exposure/access sampling, individual-agent adoption decisions, measurable person effects, belief learning, exposure history serialization, and branch-safe application.

## Scientific boundary
- Intervention outcomes are model outputs, not predictions of the real world.
- Evidence references and uncertainty are explicit fields.
- Population sampling does not consume the core world's RNG, preserving reproducibility.
- Individual agents drive adoption when available; the engine does not encode country/class personality stereotypes.

## Next major build
1. Connect intervention lifecycle to persistent event/replay declarations.
2. Add baseline-vs-intervention metrics and divergence reports.
3. Add time-varying exposure/adoption and diffusion through relationships/organizations.
4. Add scenario contracts and intervention serialization into replay checkpoints.
5. Expand calibration/validation against real historical trajectories.

## Progress estimate
- Current: approximately 30% of the eventual WORLD LAB vision.
- 50% target: usable civilization experiment core with interventions, population selection, individual decisions, multi-year branching, measurable divergence, uncertainty/provenance, and validation gates.
- Full target: calibrated civilization-scale world model, broad coupled systems, large-scale performance, historical validation, mature branching/replay, and the civilization-observatory presentation layer.

## Continue rule
On `Continue`, inspect this checkpoint and the repository tip, verify the latest CI result, then continue the next major build. Do not stop at trivial corrections or invent unverified project state.
