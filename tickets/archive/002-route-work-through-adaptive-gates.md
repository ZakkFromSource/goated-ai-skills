# Ticket 002: Route Work Through Adaptive Gates

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Make one task flow through a centrally selected, proportionate V2 route using
the work envelope, shared evidence, configurable approval, route signals, and
checkpoint re-evaluation without mandatory routing narration.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Adaptive Work Profile through
  Delivery Gate Matrix, Approval Policy, and Output And Communication
- `stack/AGENTS.md`
- `stack/goated-stack.yaml`
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md`
- `skills/agent-workflows/session-start-progressive-disclosure/SKILL.md`

## Relevant Source Links

- `stack/templates/work-envelope.md`
- `stack/templates/evidence-entry.md`
- `scripts/validate_skills.py`

## Acceptance Criteria

- [x] The router records the agreed profile dimensions, risk flags, data
      sensitivity, action reach, workflow intensity, and proof strategy.
- [x] Required, conditional, and meaningful skipped gates are selected once.
- [x] Route re-evaluation occurs only at the defined checkpoints or a material
      signal.
- [x] Fresh evidence is reused and affected evidence can be invalidated.
- [x] `confirm-each-write`, `approve-batch`, `standing-session-consent`, and
      `draft-without-applying` are represented with a risk-adaptive default.
- [x] Existing approval remains valid until scope or action reach changes.
- [x] Skills report internal deltas while the main agent produces one
      consolidated closeout.
- [x] Tiny work has a near-zero-ceremony path.

## Expected Proof

- Fixtures for tiny bypass, standard work, checkpoint escalation, restricted
  data, external-changing action, approval reuse, and evidence invalidation.
- Registry and skill validation output.
- Instruction-size comparison for the V1 and V2 router path.
- Manual review that the router does not silently activate a long pipeline.

## Blocked By

- `tickets/archive/001-establish-v2-integrated-stack-foundation.md`

## User Stories Addressed

- Derived: As a user, my agent selects a proportional route once and reuses
  evidence instead of repeatedly rebuilding the workflow.

## Implementation Route

- Use `writing-plans` to define the registry changes, router rewrite, templates,
  and focused behavioural fixtures.
- Use the current shared-policy and registry contracts rather than inventing a
  runtime controller.

## Scope Exclusions

- Do not add model selection, runtime cost fields, automatic framework
  enforcement, or a dedicated evaluation skill.
- Do not migrate specialist skill procedures beyond what is needed to prove
  this routed slice.

## Implementation Proof

- `uv run python -m unittest discover -s tests -v` passed 14 tests, including
  routing-fixture vocabulary, gate, checkpoint, approval-reuse, evidence, and
  required-scenario behavior.
- `uv run python scripts/validate_skills.py` passed 32 implemented skills, 32
  registry entries, and 7 adaptive-routing fixtures with zero blocking errors
  or human-review notes. Three unrelated learning-capture schema-drift notes
  remain report-only.
- `stack/fixtures/routing/` covers tiny bypass, standard work, checkpoint
  escalation, restricted data, external-changing action, approval reuse, and
  evidence invalidation.
- The preserved `v1-baseline` router is 1,541 whitespace-delimited words; the
  V2 router is 1,151 words. Router plus full orientation is 2,307 words in V1
  and 1,884 words in V2.
- Manual router review confirmed that routine route selection stays internal,
  the full orientation skill is conditional, and the tiny fixture prohibits a
  silently activated clarification/planning/review/handoff pipeline.
- Standards/spec review found no findings. Documentation sync updated the
  durable context matrix and standards profile for routing-fixture validation.
