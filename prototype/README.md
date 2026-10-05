# WORLD LAB — October 13 prototype

This is the first showable prototype of the civilization-observatory direction.

What is real:
- The browser calls a Python server.
- The server creates a deterministic synthetic population with a persistent individual agent for every generated person.
- A scenario contract binds population scope, intervention, model version, evidence and uncertainty.
- Baseline and intervention worlds are branched from a deterministic checkpoint.
- Adoption is decided by the individual-agent decision model.
- The result is measured with the existing divergence metrics.
- Exposure/adoption counts and individual samples are returned to the UI.

Run from the repository root:

    python scripts/serve_prototype.py

Open http://127.0.0.1:8765.

This prototype intentionally labels outcomes as model outputs. It is not presented as a real-world predictor.
