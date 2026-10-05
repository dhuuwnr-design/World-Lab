# WORLD LAB - Checkpoint

## Current branch
- feature/v0.8-presentation-architecture

## Latest verified milestone
- Commit: 83f9b65656d578d1da26cad6c7c1ecb248841b04
- GitHub Actions run #148: SUCCESS.
- 67 tests passed in the preceding failed run before the final replay-fixture correction; the final run #148 is the authoritative CI gate and completed successfully.
- Replay intervention checkpoints now restore persisted intervention handlers correctly, and the replay regression fixture uses an individual cognitive agent.

## October 13 showable prototype
- Prototype commit: 7618fca25f278230196632a4e18c2af1eef52970, followed by verified replay/scenario fixes through 83f9b65656d578d1da26cad6c7c1ecb248841b04.
- prototype/index.html: civilization-observatory style interface.
- scripts/serve_prototype.py: zero-dependency local HTTP server.
- The UI can select simulated population size, intervention, population access fraction, and simulation horizon.
- The server runs the actual WORLD LAB engine, not a fake front-end animation.
- The demo shows civilization-scale metrics, divergence, individual-agent samples, exposure/adoption counts, declared mechanisms, evidence references, and uncertainty.
- Prototype README documents local launch.

## Current implementation milestone
- Individual intelligence architecture is active: generated people receive persistent individual cognitive agents with goals, beliefs, memory, risk tolerance, social sensitivity, perception and decision context.
- Deterministic replay/checkpointing and branching are active.
- Intervention definitions, population scopes, exposure/access, agent adoption, effects, beliefs, evidence and uncertainty are persisted.
- ScenarioSpec binds ScenarioDefinition, intervention, population scope, evidence, uncertainty and deterministic scenario fingerprint.
- run_scenario creates a baseline branch and intervention branch, advances both to the same horizon, and computes model-output divergence.
- Presentation contracts and event/causal projections remain available for future UI expansion.

## Scientific boundary
- Intervention outcomes are model outputs, not predictions of the real world.
- Evidence references and uncertainty remain explicit.
- Country/class/culture context must influence distributions and institutions, not hard-code personality stereotypes.
- The individual agent is an artificial decision model, not a claim of consciousness.
- The October 13 demo must visibly distinguish simulation output from observed evidence.

## Next major build for the October 13 demo
1. Validate the prototype end-to-end against the actual repository checkout.
2. Add time-series trajectories instead of only endpoint metrics.
3. Add branching-futures visualization with baseline vs multiple intervention branches.
4. Add a stronger People View showing an individual agent's trajectory, decisions and relationships.
5. Add intervention diffusion through relationships/organizations and repeated time-varying exposure.
6. Package/deploy a reliable demo URL if the chosen hosting path is stable and free/available.
7. Re-run CI after every implementation milestone and never mark an unverified state as complete.

## Post-demo scientific build
1. Calibration against real historical trajectories.
2. Geography, migration, labor, health, education, institutions, media and environmental feedback loops.
3. Scale/performance architecture for much larger populations.
4. Held-out validation, sensitivity analysis and reproducible experiment bundles.
5. Civilization-scale presentation: planet -> country -> city -> household -> person -> relationship -> causal chain -> branching future.

## Progress estimate
- Current engineering direction: approximately 38% of the eventual WORLD LAB vision.
- October 13 target: a genuinely showable, interactive prototype proving individual-agent simulation, counterfactual experimentation, deterministic branching, measurable divergence and scientific provenance.
- Full target: calibrated civilization-scale world model, broad coupled systems, large-scale performance, historical validation, mature branching/replay, and the civilization-observatory presentation layer.

## Continue rule
On Continue, inspect this checkpoint and the repository tip, verify the latest CI result, then continue the next major build. For the October 13 milestone, prioritize actual demo quality and end-to-end reliability over adding disconnected research features. Do not stop at trivial corrections or invent unverified project state.
