# WORLD LAB — Durable Project Checkpoint

Last checkpoint: 2026-10-04

## Identity
WORLD LAB is a research-oriented virtual civilization laboratory.
Core principle: build a world, change conditions, let time pass, and observe what emerges.
It is not a one-click future predictor and must not claim exact real-world prediction.

## Canonical development repository
- GitHub: dhuuwnr-design/World-Lab
- Active development branch: feature/v0.3-calibration-engine
- GitHub + Composio are the canonical workflow for World Lab.
- Before continuing, inspect the actual branch, recent commits, open PRs, and CI status.

## Product vision
WORLD LAB should feel like a living civilization laboratory, not a spreadsheet or a simple AI demo.

Primary experience:
1. Create a world.
2. Choose population, geography, starting year and duration.
3. Let generations live through the world.
4. Introduce interventions.
5. Watch causal consequences unfold over realistic timescales.
6. Branch timelines and compare alternative worlds.
7. Inspect people, families, cities, technologies, institutions and systems.
8. Ask why an outcome happened and trace causal chains.
9. Discover model-derived unexpected consequences.
10. Repeat experiments with multiple seeds and inspect uncertainty.

Suggested product framing:
"WORLD LAB — An open laboratory for simulating how societies and civilizations evolve."
"Build a world. Change its conditions. Let time pass. Observe what emerges."

## Audience / uses
WORLD LAB should have multiple entry points into the same underlying simulation:
- Explorer: curious people exploring alternate worlds and counterfactuals.
- Student: learn history, economics, technology, demography and systems thinking through experiments.
- Teacher: create shared experiments and compare student worlds.
- Researcher: calibrated experiments, parameter sweeps, uncertainty, validation and reproducibility.
- Policy/planning user: investigate trade-offs and alternative scenarios, never as an unquestionable prediction.
- Developer/model builder: Python APIs, mechanisms, calibration and reproducible runs.
- AI-assisted researcher: AI helps formulate, execute and explain experiments; the simulation remains the source of outcomes.

## Experience principles
### Living world
The user should feel they were given a living world rather than a form asking for parameters.

### Time machine
Users should be able to move through a timeline, pause, inspect, intervene and branch from historical points.

### Micro <-> macro
Users should be able to zoom from civilization to region/city/community/family/person and back out, while observing the same underlying world state.

### Why did this happen?
Important outcomes should expose causal explanations grounded in model mechanisms:
technology -> affordability -> adoption -> demand -> production -> jobs -> migration -> housing, etc.

### Discovery
After runs, WORLD LAB should surface model-derived notable changes, unexpected consequences and divergent trajectories, with evidence from the simulation rather than invented narratives.

### Progressive complexity
Simple mode must be approachable. Research mode must expose deep parameters, calibration, uncertainty, sensitivity and batch experiments.

### No fake realism
Never create visual polish that pretends an uncalibrated mechanism is empirically exact.
Show calibration status, evidence, assumptions and uncertainty.

## Proposed future experience layer
The product layer should sit above the simulation engine:

Experience Layer
- Explore
- Follow a person/family/city/technology/industry/generation/idea
- Time Machine
- Intervene
- Branch
- Discover
- Explain

Research Layer
- Parameters
- Calibration
- Batch runs
- Sensitivity
- Validation
- Reproducibility

Both use the same Experiment Engine and shared World state.

## Existing modeling foundation at this checkpoint
The repository already contains:
- reference-driven synthetic population foundation
- population-size configuration
- life-course engine
- culture/social/affective state foundation
- sparse social network foundation
- local social influence / perceived respect mechanism
- experiment configuration and deterministic runner
- interventions and timeline snapshots
- multi-run uncertainty summaries
- modeling protocol and architecture documentation
- GitHub Actions tests

Latest major implementation checkpoint before this product checkpoint:
- Commit: 5f985bd2faeff24056f8e8d0760cb2feb830d213
- Message: Add sparse social networks and emergent local respect

## Current known model gaps
These are not claims of completion:
- individual decision-making is not yet sufficiently modeled
- socioeconomic state/economic household dynamics need implementation
- relationship formation/dissolution beyond household ties needs implementation
- friendship/work/school/community/online networks need implementation
- institutions and social norms need deeper mechanisms
- technology diffusion needs deeper integration with economy/social networks
- calibration profiles need source/year/geography/population-scope metadata and empirical validation
- historical validation needs to expand
- subsystem scheduling/mechanism registry should eventually replace ad-hoc annual integration
- experience/UI layer is conceptual and needs implementation
- causal explanation/provenance layer needs implementation
- branching timelines need a durable state/version model
- large-scale performance needs measured benchmarks before claims

## Human realism principles
People must not be represented as stereotypes.
Country/region/culture is context, not a single personality coefficient.
Individual behavior should emerge from heterogeneous:
- life history
- household/family relationships
- socioeconomic circumstances
- education
- occupation/status
- values and personality
- emotions and wellbeing
- risk tolerance
- ambitions
- social expectations
- reference groups
- information/media exposure
- reputation
- institutions
- major life events
- memory/learning
- migration and community context
where evidence and calibration justify them.

Example principle:
"middle-class Indian social respect" must not become one fixed national coefficient. It should emerge from evidence-backed norms, class/economic context, reference groups, relationships and individual variation.

## Research/modeling rule
Every mature mechanism should follow:
Evidence -> Mechanism -> Calibration -> Simulation -> Validation -> Uncertainty

A result is not called "realistic" merely because it looks plausible.

## Autonomous continuation rule
When the user says "Continue World Lab", "continue", or "work on World Lab":
1. Read this checkpoint.
2. Inspect actual GitHub state; do not trust the checkpoint blindly.
3. Verify latest commit, branch, PR and CI.
4. Identify the highest-value modeling/product weakness.
5. Research relevant evidence/tools where useful.
6. Implement directly through GitHub + Composio.
7. Add tests and documentation.
8. Run/dispatch CI and inspect results.
9. Update this checkpoint with the new verified checkpoint.
10. Report concrete work done, not generic promises.

## Product north star
WORLD LAB should make a user think:
"I am not asking AI what happens. I am conducting an experiment on a living simulated civilization."

The ambition is to make the project genuinely useful, visually compelling and intellectually surprising while keeping the simulation honest, reproducible and evidence-aware.
