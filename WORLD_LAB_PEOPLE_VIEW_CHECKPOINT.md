# WORLD LAB PEOPLE VIEW CHECKPOINT

Date: 2026-10-05
Base: main at 589cb89968bc3ef4465040a6a54af7941a8cfd3d

## Build

Added a read-only People View projection tied to the real individual-agent state.

Verified design intent:
- Individual decisions are now recorded as deterministic DecisionRecord entries with reason, chosen action, bounded perception, and simulation day.
- Intervention adoption passes the actual simulation day into the decision record.
- Presentation exposes one person's goals, beliefs, bounded traits, recent event memory, decision history, and current perception through a typed IndividualAgentSnapshot.
- Export can optionally include a person projection.
- No LLM call is introduced into the simulation loop.
- The projection does not claim consciousness; it exposes model state only.

## Next

Build the UI around three synchronized levels:
1. civilization trajectory and branch comparison,
2. selected person trajectory/decisions,
3. causal/evidence panel explaining only declared mechanisms and provenance.

Then add relationship/organization diffusion so a person's exposure can change through the social network rather than only direct intervention scope.
