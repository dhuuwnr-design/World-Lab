# WORLD LAB RESOURCE CATALOG CHECKPOINT

Date: 2026-10-05
Branch: feature/v0.9-social-network-foundation

## Verified implementation

The repository contains a provenance-first external resource registry and the first controlled ingestion contract:

- `worldlab/core/resource_catalog.py`
- `worldlab/data/resources.json`
- `worldlab/core/ingestion.py`
- `worldlab/tests/test_resource_catalog.py`
- `worldlab/tests/test_ingestion.py`

The catalog currently records 8 high-value sources:

1. NASA Earthdata Search
2. NOAA NCEI Web Services
3. OpenStreetMap
4. World Bank Data Catalog
5. Mesa
6. Mesa-Geo
7. PCMDI Metrics
8. FLAME GPU 2

The ingestion layer now provides:
- immutable dataset manifests
- SHA-256 content identity
- an opt-in JSON fetch helper
- NCEI-style observation -> EvidenceRecord conversion
- offline fixtures for deterministic CI

## Truth conditions

This milestone does NOT claim that NASA, NOAA, OSM or World Bank bulk datasets have been downloaded into the repository.

A source is only `integrated` after its actual acquisition, checksum/version capture, transformation and validation have succeeded.

The NCEI adapter is a real ingestion path, but the committed test uses a small recorded fixture rather than live NOAA data. This keeps CI reproducible and avoids silently depending on network availability.

NOAA's official Access Data Service supports REST retrieval and can return JSON/CSV/NetCDF depending on dataset and parameters. citeturn0search0turn0search4

NASA's CMR provides programmatic discovery and metadata for Earth science holdings, which will be the basis for the NASA adapter rather than scraping pages. citeturn0search8

OpenStreetMap provides regional/bulk extraction paths; the full world should not be committed to Git. citeturn0search5turn0search7

## Next milestone

Build source-specific NASA/NOAA acquisition manifests and then a first real downloaded sample with recorded provenance, checksum, license and geographic mapping.