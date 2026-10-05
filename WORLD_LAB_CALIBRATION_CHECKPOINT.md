# WORLD LAB CALIBRATION CHECKPOINT

Date: 2026-10-05

## Completed
- Added explicit deterministic parameter-sweep calibration.
- Every trial stores candidate parameters, simulated outputs, and validation metrics.
- Selection is deterministic and uses normalized RMSE then relative absolute error.
- No parameter is inferred from a country label or hidden demographic stereotype.
- Calibration remains separate from the simulation kernel.

## Evidence direction
World Lab now has a transparent place to consume external time-series indicators. The World Bank Indicators API exposes thousands of time-series indicators and supports country/indicator/date-range queries without API keys. Its data and metadata can therefore become an auditable evidence input, but must be ingested with source/year/unit provenance and validated before affecting simulation parameters.

## Next
Build a real evidence ingestion layer with immutable dataset snapshots and time-series calibration/holdout validation. Then connect calibrated parameters to population-scale world initialization and scenario trajectories.
