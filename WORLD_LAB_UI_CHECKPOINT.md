# World Lab UI checkpoint — experimental console

This adds a first mobile-friendly browser testing surface around the existing World kernel. It is explicitly an early test build, not the completed World Lab.

Capabilities:
- configurable population and deterministic seed
- world year/population/household/employment metrics
- sample individual inspection
- advance actual World kernel by years
- responsive browser layout with no web-framework dependency

Run:
python -m worldlab.ui.server

Next: intervention controls, scenario A/B comparison, individual causal traces, trajectories, evidence/provenance, then richer sector views.
