# Ticket 006: Design Architecture And Plans Proportionally

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Clarify the route between current-state architecture mapping, prescriptive
architecture design, architecture review, and inline or durable implementation
planning using the V2 canonical names.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Proportional Planning
  Artifacts and Canonical V2 Vocabulary And Renames
- `skills/engineering/plan-codebase-architecture/SKILL.md`
- `skills/engineering/improve-codebase-architecture/SKILL.md`
- `skills/engineering/architecture-design-map/SKILL.md`
- `skills/engineering/writing-plans/SKILL.md`

## Relevant Source Links

- `skills/engineering/plan-codebase-architecture/references/`
- `skills/engineering/architecture-design-map/`
- `CONTEXT.md` — Architecture Design Language
- `stack/goated-stack.yaml`

## Acceptance Criteria

- [x] `design-codebase-architecture` becomes the canonical prescriptive skill.
- [x] `review-codebase-architecture` becomes the canonical review-only skill.
- [x] Old architecture skill names resolve through registry aliases.
- [x] Descriptive mapping remains distinct from design and review.
- [x] Architecture output uses the smallest useful visualization rather than
      defaulting to Mermaid.
- [x] `writing-plans` supports inline and durable modes.
- [x] Compact planning can be promoted without restarting discovery.
- [x] Each route emits the appropriate next-step signal without rebuilding the
      whole delivery pipeline.

## Expected Proof

- Current-state map versus architecture-design routing fixture.
- Architecture-review-only fixture.
- Inline and durable planning fixtures.
- Alias and renamed-reference validation.
- Manual review of example architecture outputs for proportional formatting.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`

## User Stories Addressed

- Derived: As a maintainer, I can request the right architecture or planning
  artifact without loading overlapping workflows.

## Implementation Route

- Use `writing-plans` to sequence renames, reference updates, templates,
  registry changes, and fixtures.

## Scope Exclusions

- Do not introduce architecture changes to target projects.
- Do not make diagrams mandatory.
- Do not combine descriptive mapping, design, and review into one skill.

## Implementation Proof

- `uv run python -m unittest discover -s tests -v` passed 38 tests, including
  canonical alias resolution, deprecated active-reference rejection,
  current-state-map versus architecture-design routing, review-only behavior,
  inline/durable planning, and promotion without discovery restart.
- `uv run python scripts/validate_skills.py` passed 32 implemented skills, 32
  registry entries, and five architecture/implementation-planning fixtures
  with zero blocking errors or human-review notes. Three unrelated
  learning-capture drift notes remain report-only.
- `stack/fixtures/architecture-planning/` covers descriptive versus
  prescriptive routing, review-only behavior, inline and durable plan modes,
  plan promotion, proportional visualization, shared evidence reuse, and
  one-signal routing.
- Targeted scans found no deprecated architecture names in active skill or user
  documentation. The V1 names remain only where history, the V2 rename table,
  this archived ticket, registry aliases, or alias-validation tests require
  them.
- Manual output review confirmed that architecture mapping and design templates
  allow prose, bullets, or tables for compact relationships and reserve Mermaid
  for flows, hierarchies, or topologies that materially benefit from a diagram.
- `git diff --check` returned no whitespace errors. Standards/spec review found
  no remaining findings, security review was not applicable, and documentation
  sync updated public routing, context, standards, fixtures, and validation
  guidance.
