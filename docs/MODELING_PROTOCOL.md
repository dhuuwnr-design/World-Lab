# WORLD LAB modeling protocol

WORLD LAB is an **experiment laboratory**, not a future-prediction machine.

## The rule we will enforce

Every model component follows:

**Evidence → mechanism → calibration → simulation → validation → uncertainty**

A result is not called "realistic" merely because it looks plausible. Model adequacy
is relative to the question being asked, and uncertainty must be carried into the
interpretation.

## How a user uses WORLD LAB

1. Choose a population size (small, medium, large, or custom).
2. Choose a starting year and simulation duration.
3. Choose the geographic scope and available reference data.
4. Run a baseline world.
5. Add an explicit intervention at a specified year.
6. Let time pass; people age, reproduce, work, migrate and die as mechanisms mature.
7. Compare baseline and intervention worlds.
8. Repeat with multiple seeds and inspect ranges, not only a single trajectory.
9. Export the experiment definition, seed, model version, calibration sources and
   outputs so another person can reproduce it.

## Design questions the engine must answer

Before adding a subsystem we ask:

- What real-world mechanism are we representing?
- What observations can constrain it?
- At what temporal/spatial resolution is it valid?
- What happens when the data is missing?
- Which parameters are uncertain?
- What outputs should be validated?
- Which interactions can create feedback loops?
- What alternative plausible mechanisms should be tested?
- How expensive will it be at 1k, 100k and 1M people?
- Can the same experiment be replayed exactly?

## Reality boundaries

WORLD LAB will distinguish:

- **calibrated**: parameterized and checked against a documented reference;
- **partially calibrated**: some mechanisms/parameters have evidence, others are provisional;
- **experimental**: mechanism exists for exploration but has not earned empirical confidence;
- **unsupported**: the requested claim cannot currently be justified.

The UI/API should expose this status rather than hiding it.

## Why this matters

Modern ABM validation guidance stresses that validation is not a final checkbox:
model construction, parameter inference, uncertainty analysis and interpretation all
need to be consistent with the intended research question. Testing, calibration and
sensitivity analysis should be documented as part of the model itself.

This protocol is therefore a product requirement, not just documentation.
