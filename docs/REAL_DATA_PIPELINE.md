# Real-data pipeline

WORLD LAB will separate four different uses of real-world evidence:

1. **Initialization** — construct starting populations and environments from observed
   distributions.
2. **Calibration** — estimate parameters so simulated patterns reproduce selected
   historical observations.
3. **Validation** — compare model outputs against observations that were not used to
   fit the same parameters whenever possible.
4. **Scenario evidence** — encode real incidents as dated, geographically scoped
   interventions or shocks without pretending the model can replay every causal detail.

Labour is the first economic subsystem being prepared for this workflow. ILOSTAT
publishes detailed annual/quarterly/monthly labour tables, including unemployment
duration, age, sex, education, occupation and sector. The World Bank also provides
harmonized labour indicators and the Global Jobs Indicators Database contains more
than 100 labour-market indicators across many countries and surveys.

The pipeline must preserve source metadata and known comparability limitations.
For example, labour definitions can differ across countries, so a global average
must not silently become a universal individual-level rule.

## No fabricated precision

If evidence is missing, WORLD LAB should widen uncertainty or keep a mechanism
experimental. It should not manufacture a precise coefficient simply to make the
simulation look realistic.

## Planned ingestion layers

- demographic evidence;
- labour and earnings evidence;
- household expenditure/wealth evidence;
- education transitions;
- health and mortality;
- migration;
- technology adoption;
- energy/industry;
- environmental observations;
- historical incident records.

Each imported dataset should be traceable to a source, version/date, geography,
time range, variable definition and transformation.
