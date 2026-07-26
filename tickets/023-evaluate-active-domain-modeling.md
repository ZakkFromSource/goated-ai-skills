# Ticket 023: Evaluate Active Domain Modeling

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

HITL — the maintainer must accept or reject a new public skill after reviewing
the overlap evidence.

## What To Build

Evaluate whether GOATED loses settled terminology or consequential domain
decisions during delivery because current ownership is split across onboarding,
clarification, specification, and architecture workflows.

Run pressure scenarios against the current stack, document observed failures
and existing successful ownership, propose the narrowest remedy, and produce a
go/revise/no-go recommendation for a separate `domain-modeling` skill.

## Recommended First Reads

- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R7 and AC8.
- `skills/agent-workflows/project-context-calibration/SKILL.md`
- `skills/engineering/grill-with-docs/SKILL.md`
- `skills/engineering/write-a-spec/SKILL.md`
- `skills/engineering/design-codebase-architecture/SKILL.md`
- `skills/engineering/review-codebase-architecture/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`

## Relevant Source Links

- `CONTEXT.md`
- `docs/adr/README.md`
- `stack/fixtures/clarification/`
- `stack/fixtures/architecture-planning/`
- `https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md`

## Acceptance Criteria

- [ ] Current ownership is mapped by trigger, read behavior, candidate update,
      write behavior, approval, and output.
- [ ] Pressure scenarios cover a newly coined term, overloaded language,
      code-versus-glossary contradiction, reversible design choice, and
      ADR-worthy decision.
- [ ] RED evidence distinguishes actual loss or ceremony from hypothetical
      concern.
- [ ] Remedies compare refining current skills, adding a reference primitive,
      and adding an independently invokable skill.
- [ ] The recommendation states invocation value, context cost, overlap risk,
      write boundary, and standalone behavior.
- [ ] The maintainer records go, revise, or no-go.

## Expected Proof

- Reusable scenario packet and observed current-stack results.
- Source-grounded ownership matrix.
- Maintainer decision with residual uncertainty.

## Blocked By

- `tickets/015-sharpen-skill-authoring-discipline.md`

## User Stories Addressed

- As the GOATED maintainer, I can add active domain modeling only when evidence
  shows it improves delivery without duplicating onboarding and clarification.

## Implementation Route

- Use `framework-agnostic-skill-creator` in proposal/evaluation mode.
- Use `grill-with-docs` only for unresolved ownership decisions.
- Use `verification-before-completion` for the recommendation claim.

## Scope Exclusions

- Do not create or register a new skill.
- Do not rewrite project `CONTEXT.md` or create ADRs merely to run the
  evaluation.
- Do not assume `CONTEXT.md` must be glossary-only.
