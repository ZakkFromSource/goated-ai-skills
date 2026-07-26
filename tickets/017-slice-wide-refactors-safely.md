# Ticket 017: Slice Wide Refactors Safely

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

AFK

## What To Build

Extend `spec-to-tickets` with a `wide-refactor` branch for mechanical changes
whose blast radius prevents ordinary independently green vertical slices.

Support expand, bounded migrate batches, and contract. Preserve dependency
ordering, fresh-agent readiness, local-only ticket creation, acceptance
coverage, and ready-frontier reporting.

## Recommended First Reads

- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R3 and AC3.
- `skills/engineering/spec-to-tickets/SKILL.md` — current vertical slicing
  contract.
- `skills/engineering/spec-to-tickets/references/ticket-slicing-templates.md`
  — current ticket shapes.
- `stack/fixtures/planning/` — compact, full, single, and multi-ticket cases.

## Relevant Source Links

- `scripts/validate_skills.py`
- `tests/test_validate_skills.py`
- `https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md`

## Acceptance Criteria

- [ ] The skill defines when a change qualifies as a wide refactor instead of a
      vertical slice.
- [ ] Expand introduces the new form without breaking existing callers.
- [ ] Migrate batches are sized by evidence-backed blast radius and blocked by
      expand.
- [ ] Contract is blocked by every migration batch and proves no old callers
      remain.
- [ ] An integration-branch exception is available only when batches cannot
      remain green independently.
- [ ] The order output identifies the frontier whose blockers are complete.
- [ ] Fixtures prove ordinary product work still uses vertical slices.

## Expected Proof

- One ordinary vertical-slice fixture and one expand-migrate-contract fixture.
- A focused test for blocker consistency, contract fan-in, and frontier
  reporting.
- Fresh repository acceptance commands required by the parent spec.

## Blocked By

None.

## User Stories Addressed

- As a maintainer planning a broad mechanical migration, I can keep work
  bounded and dependency-aware without pretending it is a normal vertical
  feature slice.

## Implementation Route

- Use `writing-plans`, then fixture-first TDD.
- Use `standards-and-spec-review` against the parent contract.
- Use `doc-sync` and `verification-before-completion` before closeout.

## Scope Exclusions

- Do not add remote issue publication.
- Do not make integration branches the default.
- Do not embed exact implementation commands or file inventories in tickets.
