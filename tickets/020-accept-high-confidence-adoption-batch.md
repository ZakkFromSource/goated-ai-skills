# Ticket 020: Accept The High Confidence Adoption Batch

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

HITL — maintainer acceptance is required.

## What To Build

Perform the cross-slice conformance, documentation, context-cost, public
boundary, and maintainer acceptance pass for the five high-confidence
adoptions.

This ticket does not implement missing behavior. It verifies the integrated
result, routes defects back to their owning ticket, and records accepted
residual risks without waiting on invocation-topology or domain-modeling
experiments.

## Recommended First Reads

- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md`
- Tickets 015 through 019 and their implementation proof.
- `docs/v2-acceptance-report.md` — prior acceptance-report precedent.
- `docs/agents/project-standards.md` — required checks.
- `stack/AGENTS.md` — integrated ownership and closeout.

## Relevant Source Links

- `README.md`
- `CONTEXT.md`
- `docs/how-to-use.md`
- `docs/install.md`
- `skills/README.md`
- `stack/goated-stack.yaml`
- `scripts/validate_skills.py`
- `tests/`

## Acceptance Criteria

- [ ] Parent-spec AC1 through AC5, AC10, and AC11 are mapped to fresh evidence.
- [ ] New skills remain self-contained and route as specialists rather than
      controllers.
- [ ] Existing skill refinements preserve prior accepted behavior.
- [ ] Public docs describe implemented capabilities without presenting
      invocation or domain experiments as shipped.
- [ ] Context comparison reports any catalog or route-cost change honestly.
- [ ] Standards/spec, security where triggered, doc-sync, and full verification
      findings are resolved or explicitly accepted.
- [ ] The maintainer records accept, accept-with-residual-risk, or reject.

## Expected Proof

- Fresh output from all repository acceptance commands.
- Focused RED/GREEN and fixture evidence from Tickets 015 through 019.
- Manual standalone-package, link, Markdown, public-boundary, and diff review.
- Maintainer acceptance decision.

## Blocked By

- `tickets/archive/015-sharpen-skill-authoring-discipline.md`
- `tickets/archive/016-minimize-diagnostic-reproductions.md`
- `tickets/017-slice-wide-refactors-safely.md`
- `tickets/018-add-resolving-merge-conflicts.md`
- `tickets/019-add-source-grounded-research.md`

## User Stories Addressed

- As the GOATED maintainer, I can accept a coherent improvement release from
  fresh evidence without coupling it to speculative future architecture.

## Implementation Route

- Use `standards-and-spec-review`, conditional `code-security-review`,
  `doc-sync`, and `verification-before-completion`.
- Keep lifecycle movement pending until maintainer review is complete.

## Scope Exclusions

- Do not implement invocation topology or domain modeling here.
- Do not fold Ticket 013's validator refactor into acceptance fixes.
- Do not archive or mark source tickets complete before their own proof and
  review are accepted.
