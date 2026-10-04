# Labour-market model

WORLD LAB treats work as a life-course process, not a permanent agent label.

The labour layer currently tracks:
- labour-force participation;
- employment and unemployment;
- unemployment duration;
- employment duration;
- occupation;
- annual income.

The mechanism is deliberately provisional. The default coefficients are not claims
about any particular country. They are replaceable by evidence-backed parameters.

## Real-world calibration targets

Relevant empirical data include labour-force participation, employment-to-population
ratio, unemployment, unemployment duration, occupation, sector, earnings, education,
age, sex, rural/urban status and employment transitions. ILOSTAT provides these
statistics at multiple temporal and demographic resolutions; World Bank labour
datasets expose comparable indicators across countries.

Calibration should be performed by geography and time period rather than applying
one global labour market to every simulated society.

## Transition structure

A person can move among:
- outside the labour force;
- participating and employed;
- participating and unemployed.

Transitions depend on age/life stage, education, health and social/economic context.
Later versions should add job vacancies, firms, occupation-specific demand, migration,
informality, self-employment, seasonal work, caregiving, discrimination, labour
institutions, benefits, commuting and macroeconomic shocks.

## Important limitation

The current implementation is a mechanism scaffold. It is **not calibrated** to
a country and must not be presented as a realistic forecast. Real-data calibration
and out-of-sample validation are required before stronger claims are made.
