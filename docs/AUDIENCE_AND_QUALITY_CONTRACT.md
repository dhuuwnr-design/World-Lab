# WORLD LAB audience and quality contract

WORLD LAB must be judged from the outside in, not only from the engine author's perspective.

The recurring question is:

> If I were this person discovering WORLD LAB for the first time, what would I expect it to do, what would make me trust it, what would make me leave, and what would make me tell someone else about it?

This is a product requirement, not just UX research.

## 1. Explorer / curious person

### First thought
"I have a world in front of me. What can I change, and what happens if I let it run?"

### Expects
- Immediate understanding without reading a manual.
- A visually alive world rather than a spreadsheet.
- Simple starting scenarios.
- A strong time-travel feeling: years and generations actually pass.
- The ability to zoom from civilization-scale outcomes into real individual lives.
- Surprising consequences that come from the simulation.
- A clear explanation of why an outcome happened.

### Trust requirement
The product must not pretend that an uncertain simulation result is a fact.

### Failure
If the first experience is hundreds of parameters, unexplained charts, or an instant "future prediction", the Explorer should reject the product.

### Quality bar
Within minutes, the person should be able to create or open a world, change one condition, run time forward, and understand at least one causal consequence.

## 2. Student

### First thought
"Can I learn something by experimenting instead of only reading about it?"

### Expects
- Guided experiments.
- Historical starting points.
- Clear explanations of mechanisms.
- Ability to compare what actually happened historically with a counterfactual.
- Individual stories connected to aggregate statistics.
- Safe experimentation without needing advanced mathematics.

### Quality bar
A student should be able to answer "why did this happen?" using the model's causal chain, not an AI-generated explanation detached from the simulation.

## 3. Teacher / educator

### First thought
"Can I use this to make a difficult concept understandable to a whole class?"

### Expects
- Reproducible scenarios.
- Shareable experiment configurations.
- Baseline vs intervention comparison.
- Teacher-controlled starting conditions.
- Guided questions and checkpoints.
- Evidence and source visibility.
- A way to prevent students from confusing simulation with historical fact.

### Business/product implication
A teacher is not buying graphics. They are buying a reliable learning environment and reusable experiments.

## 4. Researcher

### First thought
"Can I inspect the assumptions, reproduce a run, calibrate the model, and determine whether the result is defensible?"

### Expects
- Explicit mechanisms.
- Parameter provenance.
- Source metadata.
- Geography, population and observation period for evidence.
- Calibration and validation targets.
- Uncertainty distributions.
- Random seeds and reproducibility.
- Batch experiments and sensitivity analysis.
- Raw and derived outputs.
- Versioned model definitions.
- Clear separation of observed data, calibrated parameters and simulated outcomes.

### Trust requirement
Every important empirical claim must be traceable to evidence. A beautiful visualization cannot compensate for weak calibration.

### Failure
A researcher should reject WORLD LAB if it hides assumptions behind a single "realism" score or presents arbitrary coefficients as scientific truth.

## 5. Business / entrepreneur

### First thought
"Can I test a decision in a plausible market before spending real money?"

### Expects
- A way to introduce a product, service or technology.
- Customers with different needs, incomes and constraints.
- Competitors and substitutes.
- Awareness and marketing.
- Pricing and purchasing power.
- Distribution and supply constraints.
- Production capacity.
- Hiring and wages.
- Taxes/regulation where relevant.
- Reviews and social influence.
- Repeat purchase and churn.
- Market share and long-term survival.
- Multiple scenarios rather than one answer.

### Critical requirement
A product must not succeed merely because the user selected "successful product." It must survive causal interactions among people, firms, prices, supply, competition, institutions and time.

### Business value
The useful output is not "your product will make $X." It is a range of possible trajectories, the mechanisms driving them, the assumptions that matter most, and the conditions under which the result changes.

## 6. Policy / public-sector user

### First thought
"What are the trade-offs, who benefits, who loses, and how long do effects take?"

### Expects
- Policy interventions.
- Distributional effects, not only averages.
- Regional differences.
- Time-to-effect.
- Unintended consequences.
- Multiple stochastic runs.
- Alternative scenarios.
- Evidence provenance.
- Explicit uncertainty.
- Ability to inspect affected populations.

### Safety/quality requirement
WORLD LAB must support policy exploration without presenting itself as an oracle or replacing real-world evaluation.

## 7. Social scientist / economist / demographer

### First thought
"Are the population and social mechanisms represented at the right level of detail, and can I test hypotheses?"

### Expects
- Heterogeneous individuals and households.
- Age, education, work, income, family and migration processes.
- Networks and institutions.
- Country/region/time-specific evidence.
- Cohort effects.
- Distributional outputs.
- Historical calibration.
- Mechanism-level inspection.

### Failure
Averages that erase heterogeneity should not be accepted as a substitute for individual-level structure when the research question depends on it.

## 8. Developer / model builder

### First thought
"Can I extend the world without breaking reproducibility or the existing model?"

### Expects
- Clear module boundaries.
- Stable data contracts.
- Deterministic seeds where possible.
- Tests.
- Versioned experiments.
- Documentation.
- APIs.
- Pluggable mechanisms.
- Efficient scaling paths.

### Quality bar
The visual product and the simulation engine must be separable. A new representation should not require rewriting the underlying world.

## 9. AI researcher

### First thought
"Can AI help conduct experiments while the simulation remains the source of outcomes?"

### Expects
- Natural-language experiment construction.
- Automatic scenario setup.
- Experiment execution.
- Model inspection.
- Causal explanations grounded in actual run data.
- Hypothesis generation.
- Comparison of repeated runs.
- Evidence retrieval and provenance.

### Non-negotiable rule
AI may propose, explain and investigate. It must not invent simulation outcomes, evidence or causal mechanisms.

## 10. Investor / business decision-maker evaluating WORLD LAB itself

### First thought
"Is this a serious platform with defensible technology and a credible path to users?"

### Expects
- A clear product category.
- Demonstrable wow moments.
- Real evidence infrastructure.
- Reproducible experiments.
- A growing model ecosystem.
- Strong differentiation from dashboards, games and generic AI chat.
- A credible route from a focused initial use case to a broader world platform.
- Measurable quality improvements over time.

### Important product distinction
The moat is not merely "more parameters." It is the combination of:
1. individual/world simulation,
2. evidence and calibration provenance,
3. experiment/branching infrastructure,
4. human-readable causal inspection,
5. multiple representations of the same world,
6. reproducibility.

# Cross-audience expectations

Different users want different depth, but they must share one underlying world.

| Dimension | Explorer | Student | Teacher | Researcher | Business | Policy | Developer |
|---|---|---|---|---|---|---|---|
| Ease of entry | very high | high | high | medium | high | medium | lower |
| Visual exploration | essential | essential | essential | useful | essential | useful | optional |
| Individual inspection | essential | high | high | high | useful | high | useful |
| Evidence provenance | visible | visible | essential | essential | essential | essential | essential |
| Uncertainty | simple | explained | explained | detailed | decision-focused | detailed | technical |
| Batch experiments | hidden | optional | useful | essential | essential | essential | essential |
| Model internals | hidden | guided | guided | essential | selective | selective | essential |
| Reproducibility | automatic | automatic | essential | essential | essential | essential | essential |

The interface should adapt to the user's goal without creating separate incompatible products.

# Product-level questions WORLD LAB must keep asking

Before adding a major feature, ask:

1. Who would use this?
2. What real-world question are they trying to answer?
3. What would they expect to see?
4. What evidence would make them trust it?
5. What would make them distrust it?
6. What is the smallest useful experiment?
7. What happens at 1 year, 10 years and several generations?
8. Which individuals or groups experience the change?
9. Which regions or institutions diverge?
10. What could go unexpectedly wrong?
11. Can the result be reproduced?
12. Can the user understand why the result occurred?
13. Which assumptions drive the result?
14. Is this mechanism supported by real evidence?
15. Are we showing an observed fact, a calibrated model behaviour, or a speculative simulation?
16. Does the representation make the simulation easier to understand without exaggerating certainty?
17. Does this feature create genuine value or merely make the product look impressive?

# The stranger test

A feature is not considered successful merely because it works internally.

A person who did not build WORLD LAB should be able to encounter it and answer:
- What is this?
- Why should I care?
- What can I do here?
- What happened?
- Why did it happen?
- Can I trust what I am seeing?
- Can I change one thing and test it?
- Can I inspect who was affected?
- Can I reproduce or share the experiment?

If the product cannot answer these naturally, the representation is incomplete even if the engine is technically correct.

# The real-world consequence test

For interventions involving products, technologies, policies, disasters, migration, education, energy, health or economic change, do not jump directly from intervention to outcome.

Look for the real causal chain.

Example:

new product
-> awareness
-> perceived usefulness
-> affordability
-> access/distribution
-> individual decision
-> household constraints
-> social exposure/recommendation
-> purchase
-> repeat use
-> demand
-> production
-> supply chain
-> jobs/income
-> competitor response
-> prices
-> regulation/taxation
-> regional diffusion
-> longer-term structural effects

The exact chain will differ by intervention. The principle is that outcomes should emerge through interacting mechanisms rather than a single success coefficient.

# The beyond-imagination test

WORLD LAB should create moments that are difficult to get from ordinary charts:

- Follow one person from childhood to old age while the civilization changes around them.
- Watch a technology move from invention to scarce prototype to infrastructure-dependent adoption to widespread use.
- Branch a world at a historical moment and watch two generations diverge.
- Zoom from a global change to the households experiencing it.
- Discover an unexpected consequence and trace it back to the mechanism that produced it.
- Compare not just averages, but distributions, regions, generations and social groups.
- Re-run the same experiment and see the range of plausible outcomes.
- Ask "what would have to be different for the result to change?" and inspect sensitivity.

The wow moment must come from the depth of the living system, not fabricated cinematic effects.

# Product quality ladder

WORLD LAB should progress through these gates:

1. **Understandable** — a stranger knows what it is.
2. **Interactive** — a stranger can run a meaningful experiment.
3. **Alive** — time and people create visible evolution.
4. **Causal** — outcomes emerge through inspectable mechanisms.
5. **Evidence-grounded** — important mechanisms have provenance and calibration status.
6. **Uncertainty-aware** — repeated runs reveal ranges rather than fake certainty.
7. **Research-useful** — experiments are reproducible and inspectable.
8. **Decision-useful** — users can explore trade-offs and conditions, not receive magic answers.
9. **Extensible** — developers can add mechanisms without destroying the contract.
10. **World-scale** — interconnected systems produce emergent civilization-level behaviour.

We should never claim a higher gate while a lower gate is broken.

# Operating principle

WORLD LAB development should alternate between:

**build -> observe -> question -> research -> calibrate -> test -> represent -> challenge -> repeat**

The assistant should continuously role-play the major user perspectives above and actively look for missing capabilities, misleading representations, weak assumptions and better ways to make the world useful.

The goal is not to make a bigger simulation.

The goal is to make a world that people can enter, experiment on, understand, question and trust to the degree justified by evidence.
