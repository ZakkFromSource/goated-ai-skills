# Ticket 001: Establish The Compatible Contract

## Parent Spec

`docs/specs/2026-07-25-workflow-migration.md`

## Type

AFK

## What To Build

Establish the approved compatibility contract that downstream consumers can
adopt without breaking current behavior.

## Recommended First Reads

- `docs/specs/2026-07-25-workflow-migration.md` — migration contract.
- `src/contracts/` — current public contract.

## Relevant Source Links

- `tests/contracts/` — current compatibility proof.

## Acceptance Criteria

- [ ] The compatible contract is exposed through the existing public seam.
- [ ] Current consumers continue to pass their contract tests.

## Expected Proof

- Focused contract tests and the nearby compatibility suite.

## Blocked By

None.

## Scope Exclusions

- Do not migrate consumers in this ticket.
- Do not remove the legacy contract.
