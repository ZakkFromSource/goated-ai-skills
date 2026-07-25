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
- `skills/engineering/write-a-spec/SKILL.md`
- `skills/engineering/spec-to-tickets/SKILL.md`
- `skills/engineering/spec-to-tickets/references/ticket-slicing-templates.md`
- `stack/goated-stack.yaml`

## Relevant Source Links

- `issues/prd-goated-ai-skills-v1-public-core.md`
- `issues/archive/`
- `docs/specs/`
- `tickets/`

## Acceptance Criteria

- [x] `write-a-spec` becomes the canonical skill and supports compact and full
      modes.
- [x] `spec-to-tickets` becomes the canonical slicing skill.
- [x] `write-a-prd` and `prd-to-issues` resolve as registry aliases without
      duplicate skill folders.
- [x] Spec and ticket terminology matches the V2 definitions.
- [x] New default paths are `docs/specs/` and `tickets/`.
- [x] Ticket creation honors an existing approved batch and asks again only
      when scope or action reach changes.
- [x] Single- and multi-ticket outputs are fresh-agent-ready.
- [x] Historical V1 PRDs and archived issues remain unchanged.

## Expected Proof

- Compact-spec and full-spec fixtures.
- Single-ticket and multi-ticket slicing fixtures.
- Alias-resolution validation.
- Historical-artifact preservation scan.
- Renamed-reference and link checks.
- Fresh-agent-ready review of generated sample tickets.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`
- `tickets/archive/004-clarify-decisions-proportionally.md`

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

## Implementation Proof

- `uv run python -m unittest discover -s tests -v` passed 32 tests, including
  canonical alias resolution, compact/full spec contracts, dependency ordering,
  approval reuse, and fresh-agent sample validation.
- `uv run python scripts/validate_skills.py` passed 32 implemented skills, 32
  registry entries, and four planning fixtures with zero blocking errors or
  human-review notes. Three unrelated learning-capture drift notes remain
  report-only.
- `stack/fixtures/planning/` contains compact/full spec fixtures, single/multi
  ticket fixtures, three fresh-agent-ready sample tickets, and a multi-ticket
  order sample.
- Targeted scans found the V1 names only in registry aliases and alias tests
  outside preserved V1 sources; remaining `docs/prds/` mentions are explicitly
  identified as legacy target-project conventions.
- `git diff --name-only` over `issues/`, `issues/archive/`, the V1 parent
  product artifact, and the historical V1 ADR returned no changes.
- `git diff --check` returned no whitespace errors. Manual standards/spec
  review found no remaining findings, and documentation sync updated public
  routing, install, context, standards, and order docs.
