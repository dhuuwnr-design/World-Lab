# WORLD LAB EVIDENCE CHECKPOINT

Date: 2026-10-05

## Completed
- Added `worldlab.evidence.datasets` for immutable, content-addressed evidence snapshots.
- Every observation carries source, source version, source year, geography, indicator, observation year, value, and unit provenance.
- Snapshot identity is SHA-256 over canonical, deterministically ordered observations.
- Duplicate geography/indicator/year observations are rejected instead of silently overwritten.
- Added CSV ingestion with an exact column contract and validation.
- Added chronological training/holdout splitting so later observations cannot enter calibration.
- Added holdout RMSE and relative-error evaluation separate from training calibration.

## Guardrails
- Evidence ingestion does not change simulation parameters by itself.
- Raw units are preserved; normalization/conversion must be explicit in an adapter.
- Country labels are identifiers, not hidden personality or culture parameters.
- Synthetic fixtures in tests are not real-world evidence.
- Holdout data is never passed to `CalibrationSweep`.

## Next
Connect validated evidence snapshots to explicit calibration profiles and population-scale initialization, then build multi-year trajectory evaluation with repeated time-series holdouts. After that, connect calibrated parameters to scenario branches and measure uncertainty rather than presenting a single deterministic future as fact.
