# Ticket 024: Add Accepted Active Domain Modeling

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

HITL — starts only after Ticket 023 records an explicit maintainer go decision
and accepted ownership boundary.

## What To Build

Implement the narrow active domain-modeling remedy accepted in Ticket 023.

If the accepted remedy is a new `domain-modeling` skill, deliver its
self-contained workflow, directly linked references, registry and routing
metadata, pressure fixtures, validation coverage, and synchronized public
guidance. If the maintainer instead accepts a refinement to existing skills,
revise this ticket's implementation scope before editing.

## Recommended First Reads

- Ticket 023's accepted evaluation and maintainer decision.
- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R7, AC8, and
  AC9.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- Current skills named in Ticket 023's ownership matrix.
- `stack/AGENTS.md`
- `CONTEXT.md` and `docs/adr/README.md`

## Relevant Source Links

- `stack/goated-stack.yaml`
- `scripts/validate_skills.py`
- `skills/README.md`
- Relevant category README and public operator guidance.

## Acceptance Criteria

- [ ] Implementation matches the accepted ownership boundary from Ticket 023.
- [ ] The workflow activates only when terminology or a consequential domain
      decision is actively changing.
- [ ] It checks current vocabulary and code behavior, stress-tests edge cases,
      and proposes a narrow context or ADR delta.
- [ ] Writes occur only when current approval and project convention cover
      them; read-only or proposal fallback remains useful.
- [ ] It does not perform broad onboarding, rebuild context artifacts, or force
      glossary-only `CONTEXT.md`.
- [ ] Neighboring skills point to one authoritative active-modeling procedure
      without copying it.
- [ ] Standalone and integrated pressure scenarios prove the accepted value.
- [ ] Parent-spec AC9 through AC11 have fresh evidence.

## Expected Proof

- RED/GREEN reruns of Ticket 023's pressure scenarios.
- Focused registry, routing, link, public-boundary, and write-approval tests.
- Fresh repository acceptance and context-comparison commands.
- Standards/spec, docs, and full verification review.

## Blocked By

- `tickets/023-evaluate-active-domain-modeling.md`

Ticket 013 is not a functional dependency. Sequence overlapping validator work
or plan against its completed module boundaries.

## User Stories Addressed

- As a project team, I can settle and preserve precise domain language at the
  moment it changes without triggering a broad onboarding refresh.

## Implementation Route

- Use `framework-agnostic-skill-creator`, `writing-plans`, TDD or equivalent
  behavior proof, `standards-and-spec-review`, `doc-sync`, and
  `verification-before-completion`.

## Scope Exclusions

- Do not implement a broader remedy than Ticket 023 accepted.
- Do not make all terminology discussion or architecture work invoke the skill.
- Do not make context or ADR writes automatic.
