# WORLD LAB - Checkpoint

## Current branch
- feature/v0.9-social-network-foundation

## Latest implementation milestone
- Previous verified social-network milestone: 5e2fa3e68abb9f846a918c276958414f0706c669.
- Current implementation tip: 84802c8be6180c162689c2fb3cb8f8018bc77975.
- GitHub Actions run #154 on main: SUCCESS.
- The v0.8 prototype, deterministic branching/replay, yearly trajectories, individual cognitive agents, intervention exposure/adoption, event provenance and causal-link projections are implemented.
- The social-network layer now extends from households into education, workplace and community institutions.

## What is actually implemented
- Selectable simulated population sizes in the prototype.
- Persistent individual agents with goals, beliefs, memory, risk tolerance, social sensitivity and decision context.
- Deterministic world checkpoints, branching and replay identities.
- Counterfactual baseline/intervention comparison with yearly divergence trajectory.
- Explicit intervention exposure/access/adoption records.
- Explicit event metadata, evidence references and uncertainty.
- Generated people now have household relationship edges with closeness, trust, support, conflict and contact frequency.
- Generated populations now receive deterministic school, workplace and community organizations with bounded group sizes.
- Non-household ties use the same explicit relationship mechanics, so institutional peers already affect perception and intervention diffusion.
- Employment and education assignments are synthetic structural priors used to construct those networks; they are not empirical estimates.
- A default social context is attached to the generated location.
- CI validation for commit 84802c8 is currently in progress; local 73-test validation preceded this milestone.

## Scientific boundary
Relationship parameters in this milestone are synthetic priors, not country-specific empirical estimates. They are a structural substrate for later calibration and must not be presented as measured real-world relationships.

## Next major build
1. Add repeated, time-dependent relationship-mediated exposure and belief diffusion.\n2. Add explicit multi-affiliation memberships so school, workplace and community networks can change as life stages change.
3. Add country/region calibration records and geography rather than assigning personality stereotypes by country.
4. Complete life-course network transitions: education -> work -> income -> household -> network changes.
5. Add time-series People View with decisions, relationships and social-state changes.
6. Validate the showable prototype end-to-end and keep the automated test suite green after every milestone.

## Progress estimate
- Current engineering direction: approximately 45% of the eventual WORLD LAB vision.
- This is an engineering estimate, not a scientific accuracy score.
