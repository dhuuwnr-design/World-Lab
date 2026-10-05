# WORLD LAB CAUSAL TRACE CHECKPOINT

Date: 2026-10-05

## Completed
- Added a causal trace store for declared simulation mechanisms.
- Social diffusion can emit causal traces for successful transmission.
- Each trace contains source, target, mechanism, simulation day, probability/strength, evidence references and uncertainty.
- Lineage traversal can answer why a selected person received a downstream effect, including multi-hop social paths.
- The diffusion layer now preserves the mechanism/evidence metadata instead of collapsing it into a generic intervention ID.

## Scientific guardrail
The engine records declared causal mechanisms; it does not infer causality merely because two variables correlate.

## Next
Expose causal lineage in the presentation contract, then build the first interactive observatory prototype around civilization → person → causal explanation.
