# WORLD LAB architecture

WORLD LAB is a simulation laboratory, not a single predictive model.

## Runtime layers

World state -> people, households, organizations and places.

Mechanisms -> demographic, social, economic, technological and environmental processes.

Experiment layer -> scenarios, interventions, seeds, snapshots and comparisons.

Evidence layer -> datasets, calibration parameters, validation targets and uncertainty.

Presentation layer -> maps, dashboards, timelines and experiment reports.

The presentation layer never changes model state. A saved experiment must contain enough metadata to reproduce the run: model version, configuration, random seed, interventions, calibration profile and output schema.

## Human heterogeneity

People carry individual life histories plus contextual cultural and social state. CultureProfile describes evidence-backed distributions and salience for a country, region or community; it does not define a single personality for that population. Individual draws, family relationships, peer networks, institutions and experience must create variation within every context.

Social and affective state is intentionally latent: wellbeing, stress, belonging, perceived respect, family pressure, status security, loneliness, values, emotions and norm sensitivity can influence decisions later. Current coefficients are provisional until calibrated against evidence.

## Simulation clock

The engine has a continuous day counter with annual process boundaries. Daily events may be scheduled, while demographic and other slow processes run at the annual boundary. This lets us represent events on different timescales without pretending every human process happens once per year.

## Causality before convenience

An intervention must enter a real mechanism. A technology intervention should change causal inputs such as knowledge, production capacity, infrastructure, price or availability; adoption then emerges over time. A policy intervention should modify an institution, budget, incentive or constraint rather than directly writing a final outcome.

## Scale strategy

The engine should support progressively larger worlds: micro 100-10,000 agents; meso 10,000-1,000,000; macro beyond 1,000,000 using aggregation, spatial indexing, vectorized state and/or distributed execution where necessary. WORLD LAB must benchmark its own architecture before making performance claims.

## Model documentation contract

Every mature mechanism should have an ODD-style description covering purpose, state variables/scales, scheduling, design concepts, initialization, inputs and submodels. Validation is contextual and must track model construction, parameter inference, uncertainty, simulation and interpretation together.
