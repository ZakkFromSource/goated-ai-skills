# Proportional Planning Fixtures

These fixtures describe observable expectations for `write-a-spec` and
`spec-to-tickets`. They cover compact and full specs, ordinary vertical
slicing, and fresh-agent-ready expand-migrate-contract output for a qualifying
wide refactor.

`scripts/validate_skills.py` checks the default paths, required spec depth,
dependency order, ticket handoff fields, approval reuse, wide-refactor phase
ordering, evidence-backed migration boundaries, contract fan-in, and computed
ready-frontier reporting. Manual review of `samples/` should confirm that the
generated ticket shapes are fresh-agent-ready, preserve stable intent, and do
not embed volatile implementation plans.
