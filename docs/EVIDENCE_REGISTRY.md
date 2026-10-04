# Evidence Registry

WORLD LAB treats real-world evidence as an input to model construction, not as decoration.

Each mechanism should eventually have:
- source organization and dataset/study;
- geography and population scope;
- observation years;
- variable definitions;
- sample/design information;
- known measurement limitations;
- transformation or harmonization steps;
- uncertainty/range;
- calibration target;
- validation target that was not used for fitting when possible;
- license/access constraints;
- provenance identifier.

## Evidence hierarchy

Prefer, in order where appropriate:
1. official statistical agencies and administrative statistics;
2. documented longitudinal or household surveys;
3. harmonized research microdata;
4. peer-reviewed empirical studies;
5. well-documented historical datasets;
6. expert elicitation only when direct evidence is unavailable.

No source is automatically treated as universal. A statistic from one country, class,
period or population must not silently become a global behavioral coefficient.

## Important data families

IPUMS International provides harmonized census and survey microdata covering more
than 100 countries and over one billion person records, including individual and
household characteristics such as fertility, migration, labor force, occupation,
education and household composition. Its documentation explicitly preserves
comparability limitations and source metadata.

For WORLD LAB this suggests a data architecture in which observations remain tied
to geography, year, population scope and source rather than being collapsed into
one global average.

## Calibration and validation rule

A model may use empirical data to initialize agents, calibrate parameters and
validate emergent behavior, but those uses must be recorded separately when
possible. Published ABM validation research specifically warns that reproducing
an aggregate pattern alone does not establish that the underlying individual
mechanism is correct.

Therefore every important result should be traceable to:
Evidence -> mechanism -> parameterization -> simulation -> validation -> uncertainty.

## Real incidents

Real historical incidents should become reproducible scenario inputs where the
evidence supports them: wars, pandemics, financial crises, migrations, energy
shocks, disasters, policy changes, technological breakthroughs and demographic
transitions. The incident record should distinguish observed facts from uncertain
interpretation and should never be used to imply that the model can replay history
exactly.

## Current status

This registry is an architecture requirement. The current codebase has only a
small number of provisional mechanisms. It must not be described as empirically
calibrated at civilization scale yet.
