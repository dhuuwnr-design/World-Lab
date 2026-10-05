# WORLD LAB CHECKPOINT

## 2026-10-05 — v0.7 Evidence calibration foundation

### Verified repository state
- v0.5 cumulative demographic + representative-population engine is merged into main.
- v0.6 human/social state exists on `feature/v0.6-human-social-state`.
- v0.7 starts from commit `93f91dcb814be7edf952f8b6f145e6ce551ac62d`.

### Implemented in v0.7
- `CalibrationProfile` for explicit region/year calibration inputs.
- `EvidencePoint` storing value, source, year, unit and note for provenance.
- Explicit adapters from normalized external indicators to social context.
- Explicit indicator-to-parameter mapping; no hidden country heuristics.
- Validation reports using normalized RMSE and relative absolute error.
- Regression tests for provenance, transparent mapping, bounds and validation.

### Research/data contract
UN World Population Prospects 2024 models demographic change through age/sex-specific fertility, mortality and net international migration and provides estimates/projections for 237 countries or areas. The simulation should ingest those quantities as external evidence rather than embedding country rates in engine code.
World Bank's Indicators API provides programmatic access to nearly 16,000 time-series indicators and supports multi-indicator and date-range queries. It requires no API key.

### Realism rules
1. Country labels never directly determine personality or emotions.
2. External indicators must retain source/year/unit provenance.
3. Normalization must be explicit and testable.
4. Simulation claims must distinguish mechanics, calibration fit and predictive validation.
5. Held-out data must be used before calling a model realistic.
6. Uncertainty should be preserved where source data provides it.

### Not yet implemented
- Live World Bank/UN ingestion inside the repository.
- IPUMS microdata ingestion.
- Country-specific social distributions.
- Causal estimation of how indicators change individual states.
- Held-out longitudinal validation.
- Migration, education, health, labor, finance and media feedback loops.

### Next target
Build a source-ingestion layer that can fetch/store World Bank indicator observations with provenance, cache raw observations, normalize them explicitly, and feed calibration profiles. Then add UN demographic import and cross-check simulated age/sex totals against reference trajectories before adding richer causal sectors.
