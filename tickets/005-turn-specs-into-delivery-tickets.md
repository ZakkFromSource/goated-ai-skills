# Ticket 005: Turn Specs Into Durable Delivery Tickets

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Replace the PRD-to-issue route with portable compact/full specs and
dependency-aware delivery tickets while preserving historical V1 artifacts and
supporting old skill names through registry aliases.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Proportional Planning
  Artifacts, Canonical V2 Vocabulary And Renames, and Approval Policy
- `skills/engineering/write-a-prd/SKILL.md`
- `skills/engineering/prd-to-issues/SKILL.md`
- `skills/engineering/prd-to-issues/references/issue-breakdown-templates.md`
- `stack/goated-stack.yaml`

## Relevant Source Links

- `issues/prd-goated-ai-skills-v1-public-core.md`
- `issues/archive/`
- `docs/specs/`
- `tickets/`

## Acceptance Criteria

- [ ] `write-a-spec` becomes the canonical skill and supports compact and full
      modes.
- [ ] `spec-to-tickets` becomes the canonical slicing skill.
- [ ] `write-a-prd` and `prd-to-issues` resolve as registry aliases without
      duplicate skill folders.
- [ ] Spec and ticket terminology matches the V2 definitions.
- [ ] New default paths are `docs/specs/` and `tickets/`.
- [ ] Ticket creation honors an existing approved batch and asks again only
      when scope or action reach changes.
- [ ] Single- and multi-ticket outputs are fresh-agent-ready.
- [ ] Historical V1 PRDs and archived issues remain unchanged.

## Expected Proof

- Compact-spec and full-spec fixtures.
- Single-ticket and multi-ticket slicing fixtures.
- Alias-resolution validation.
- Historical-artifact preservation scan.
- Renamed-reference and link checks.
- Fresh-agent-ready review of generated sample tickets.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`
- `tickets/004-clarify-decisions-proportionally.md`

## User Stories Addressed

- Derived: As a maintainer, I can turn fuzzy intent into an appropriately sized
  spec and portable vertical delivery tickets.

## Implementation Route

- Use `writing-plans` before moving or rewriting skill folders.
- Apply the canonical rename, reference migration, aliases, templates, and
  behavioural fixtures as one complete route.

## Scope Exclusions

- Do not publish tickets to GitHub, Jira, Linear, or another remote tracker.
- Do not rename historical V1 planning artifacts.
- Do not embed exact implementation plans in delivery tickets.
