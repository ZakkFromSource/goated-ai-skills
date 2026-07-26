# Ticket 022: Implement Accepted Invocation Topology

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

HITL — starts only after Ticket 021 records an explicit maintainer go decision
and approved consumer.

## What To Build

Implement only the invocation semantics accepted in Ticket 021 across the
neutral registry contract and the approved real consumer.

Update schema, validator, registry entries, adapter or installation output,
fixtures, migration guidance, and public docs as required by the accepted
mapping. Preserve standalone behavior and honest fallbacks on unsupported
hosts.

## Recommended First Reads

- Ticket 021's accepted report and maintainer decision.
- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R6, AC6, and
  AC7.
- `stack/goated-stack.yaml`
- `stack/schemas/stack-registry.schema.json`
- `scripts/validate_skills.py`
- `docs/install.md`
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md`

## Relevant Source Links

- The approved host's current official documentation and adapter surface.
- `tests/test_validate_skills.py`
- `stack/fixtures/routing/`
- `docs/migration-v1-to-v2.md` or a new versioned migration artifact if the
  accepted design requires one.

## Acceptance Criteria

- [ ] Only accepted semantics and combinations enter the schema.
- [ ] Every production metadata field is consumed by the approved adapter or
      installation path.
- [ ] Unsupported hosts receive an explicit safe fallback.
- [ ] Integrated invocation policy does not break individual installation.
- [ ] Explicit, implicit, router-only, and hidden/reference behavior are tested
      only to the strength supported by the host evidence.
- [ ] Registry and adapter drift is detected by deterministic validation where
      practical.
- [ ] Context and migration impact are documented.
- [ ] Parent-spec AC7, AC10, and AC11 have fresh proof.

## Expected Proof

- Schema-negative and adapter-translation tests.
- Host-level experiment or manual verification matching Ticket 021's evidence
  standard.
- Fresh repository acceptance and context-comparison commands.
- Manual fallback, migration, standalone-package, and public-boundary review.

## Blocked By

- `tickets/021-investigate-invocation-topology.md`

Ticket 013 is not a functional dependency. Re-plan against its completed module
boundaries or sequence overlapping validator edits.

## User Stories Addressed

- As an integrated-stack user, I can reduce inappropriate autonomous skill
  selection where my host supports it without losing portable standalone
  behavior.

## Implementation Route

- Use `writing-plans`, TDD, `standards-and-spec-review`, conditional
  `code-security-review`, `doc-sync`, and `verification-before-completion`.

## Scope Exclusions

- Do not implement semantics rejected or left unsupported by Ticket 021.
- Do not expand one-host evidence into universal compatibility claims.
- Do not build a general installer or marketplace product.
