# World Lab UI checkpoint — Scenario Lab test build

## Current state
The browser surface is now a prompt-first Scenario Lab rather than a large option form.

### User flow
1. Describe a scenario in natural language.
2. Optionally provide a real-world reference.
3. Choose only population and years; the prompt can also express scope such as "everyone" or "half the population".
4. Run the actual World Lab scenario engine.
5. Inspect baseline/scenario metrics, yearly divergence, individual agent samples, adoption records, mechanism, reference label, uncertainty, and replay identity.

### Supported prompt translation in this test build
The explicit rule-based translator recognizes:
- education / school / learning
- health / healthcare / medicine
- electricity / clean energy / energy
- technology / artificial intelligence / AI

Unknown mechanisms are rejected instead of silently invented.

Percentage language scales the declared prototype effect. Natural-language population phrases can set scope:
- everyone / every person / all people / entire population -> 100%
- half the population -> 50%
- quarter of the population -> 25%

This is a prototype translator, not an LLM and not a calibrated real-world causal model.

### Evidence boundary
A real-world reference entered in the UI is preserved as a provenance label. It is not automatically downloaded, validated, or treated as calibrated evidence.

### Verified end-to-end
- focused UI tests: 4 passed
- full repository suite: 93 passed
- HTTP health endpoint verified
- HTTP scenario endpoint verified with real simulation output
- HTML prompt/reference controls verified
- deterministic repeated scenario fingerprint verified
- yearly trajectory output verified

### Run locally
python -m worldlab.ui.server

Open:
http://127.0.0.1:8765

### What is real
The test surface executes the existing World kernel, generated individual agents, intervention engine, scenario orchestration, deterministic trajectories/branching infrastructure, exposure records, and replay/checkpoint identity.

### What is not claimed
This is a testable World Lab prototype, not a calibrated replica of Earth and not a predictor of real-world outcomes.
