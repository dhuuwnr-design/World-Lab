# WORLD LAB PRESENTATION SERIALIZATION CHECKPOINT

Date: 2026-10-05
Branch: feature/v0.8-presentation-architecture
Commit: 7662ea8f363f014d953fba9e2ea066d11c006379

## Verified state

The presentation contract serializer/deserializer now preserves typed tuple fields and nested dataclass values during round-trip reconstruction.

The corrected path is:
- `to_dict()` converts frozen presentation dataclasses into JSON-compatible primitives.
- `from_dict()` now uses type hints to restore tuples/lists/dicts and nested presentation dataclasses.
- Existing contract validation remains enforced by the dataclass constructors.

## CI verification

GitHub Actions check:
- check: `test`
- status: completed
- conclusion: success
- result: 40 passed
- workflow job: 111600953498

The previous failure on commit 1477d2ecc342656be76308496574d0588050bec1 was diagnosed from the actual CI log: actor_ids/causes were reconstructed as lists instead of tuples and ProvenanceRecord remained a dictionary. That failure is fixed and verified.

## Next implementation target

Add explicit structured metadata at the event scheduling boundary, while keeping existing schedule(...) calls backward-compatible.

Metadata must remain declared by the simulation code rather than inferred from callback names:
- actor IDs
- mechanism IDs
- effects
- evidence references
- uncertainty

Then project declared metadata into EventRecord/CausalLink without inventing causality. After that, build real scenario branching/replay on deterministic state and replay identities.
