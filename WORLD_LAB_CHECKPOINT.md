# WORLD LAB - Checkpoint

## Current branch
- feature/v0.9-social-network-foundation

## Latest implementation milestone
- Main tip before this milestone: 589cb89968bc3ef4465040a6a54af7941a8cfd3d.
- GitHub Actions run #154 on main: SUCCESS.
- The v0.8 prototype, deterministic branching/replay, yearly trajectories, individual cognitive agents, intervention exposure/adoption, event provenance and causal-link projections are implemented.
- This milestone adds the first explicit social-network substrate to generated populations: deterministic household relationship edges and a location-level social context.

## What is actually implemented
- Selectable simulated population sizes in the prototype.
- Persistent individual agents with goals, beliefs, memory, risk tolerance, social sensitivity and decision context.
- Deterministic world checkpoints, branching and replay identities.
- Counterfactual baseline/intervention comparison with yearly divergence trajectory.
- Explicit intervention exposure/access/adoption records.
- Explicit event metadata, evidence references and uncertainty.
- Generated people now have household relationship edges with closeness, trust, support, conflict and contact frequency.
- A default social context is attached to the generated location.

## Scientific boundary
Relationship parameters in this milestone are synthetic priors, not country-specific empirical estimates. They are a structural substrate for later calibration and must not be presented as measured real-world relationships.

## Next major build
1. Make social relationships dynamically influence individual perception and intervention diffusion.
2. Add non-household ties (workplace, education, community) using explicit institution structures.
3. Add country/region calibration records and geography rather than assigning personality stereotypes by country.
4. Add time-series People View with decisions, relationships and social-state changes.
5. Expand intervention diffusion from one-time exposure to repeated, relationship-mediated exposure.
6. Validate the prototype end-to-end and keep CI green after every milestone.

## Progress estimate
- Current engineering direction: approximately 40% of the eventual WORLD LAB vision.
- This is an engineering estimate, not a scientific accuracy score.
