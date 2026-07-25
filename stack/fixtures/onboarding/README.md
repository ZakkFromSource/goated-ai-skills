# Onboarding Fixtures

These portable V2 fixtures describe proportional onboarding and continuity
expectations. They are contract examples for deterministic validation and
manual review, not replayable transcripts or runtime automation.

Every scenario records:

- one onboarding profile and artifact budget;
- the create, refresh, or preserve action for each selected artifact;
- one shared evidence bundle with provenance and freshness;
- inferred-standard provenance when standards are inferred;
- normally silent orientation and fresh-state reuse;
- continuity storage, ignore verification, OS-temp fallback, and durable links.

The required scenarios cover a lightweight small project, a standard
incremental refresh, a governance-heavy full onboarding, and resuming from a
handoff. `scripts/validate_skills.py` checks their compact structural contract.
