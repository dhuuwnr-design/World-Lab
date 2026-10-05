# WORLD LAB RESOURCE CATALOG CHECKPOINT

Date: 2026-10-05
Branch: feature/v0.9-social-network-foundation

## Verified implementation

The repository now contains a provenance-first external resource registry:

- `worldlab/core/resource_catalog.py`
- `worldlab/data/resources.json`
- `worldlab/tests/test_resource_catalog.py`

The catalog currently records 8 high-value sources:

1. NASA Earthdata Search
2. NOAA NCEI Web Services
3. OpenStreetMap
4. World Bank Data Catalog
5. Mesa
6. Mesa-Geo
7. PCMDI Metrics
8. FLAME GPU 2

Each entry records provider, URI, resource type, license/terms note, access method, intended World Lab layers, spatial/temporal scope, resolution, integration status, provenance notes and limitations.

## Important truth condition

This checkpoint does NOT claim that these datasets have been downloaded into the repository.

`cataloged` means the source is registered for controlled ingestion.
`review_only` means an external software project is an architecture/reference candidate.
`integrated` is reserved for data that has actually passed an ingestion and validation path.

This keeps the repository honest while making real-world acquisition reproducible.

## Research basis

NASA Earthdata Search currently exposes 2.2 billion+ Earth observations for discovery.
NOAA NCEI provides programmatic weather/climate services.
OpenStreetMap data is ODbL-licensed.
The World Bank Data Catalog exposes thousands of development datasets.
Mesa/Mesa-Geo, PCMDI Metrics and FLAME GPU 2 were reviewed as relevant public software references, with their current licenses recorded above.

## Next milestone

Build the first controlled ingestion adapter:

source metadata -> remote dataset selection -> checksum/version capture -> EvidenceRecord -> geographic/environment mapping -> validation fixture.

No large raw dataset should be committed to Git merely to make the repository larger. Large sources should remain externally cached or object-stored, while compact manifests, checksums, transformations and reproducible fixtures belong in the repository.
