# End-To-End V2 Fixtures

These portable fixtures describe the four release-level workflows required by
the V2 spec. They are deterministic conformance contracts, not model
benchmarks. Each scenario records the proportional profile, selected and
conditional skills, evidence lifecycle, route signals, consolidated closeout,
and the representative V1/V2 instruction sets used by the context comparison
script.

Run:

```text
uv run python scripts/validate_skills.py
uv run python scripts/compare_v1_v2_context.py
```

The validator checks fixture structure and registry references. The comparison
script reads the preserved `v1-baseline` Git tag and reports instruction words
for each representative route. Host-driven review still decides whether the
fixture expectations preserve the required behavior.
