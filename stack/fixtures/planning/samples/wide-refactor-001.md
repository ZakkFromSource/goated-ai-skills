# Ticket 001: Expand The Shared Symbol Contract

## Parent Spec

`docs/specs/2026-07-25-shared-symbol-migration.md`

## Type

AFK

## What To Build

Introduce the new shared symbol beside the legacy form so existing callers
continue to work while bounded consumer migrations proceed.

## Recommended First Reads

- `docs/specs/2026-07-25-shared-symbol-migration.md` — approved migration contract.
- `src/contracts/` — current shared symbol seam.

## Relevant Source Links

- `tests/contracts/` — compatibility proof for old and new callers.

## Acceptance Criteria

- [ ] New callers can use the new shared symbol.
- [ ] Existing callers continue to use the legacy form without breaking.

## Expected Proof

- Focused compatibility tests for both forms.
- Existing nearby contract suite.

## Blocked By

None.

## Scope Exclusions

- Do not migrate consumers in this ticket.
- Do not remove the legacy shared symbol.
