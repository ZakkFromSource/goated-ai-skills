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

- [ ] `design-codebase-architecture` becomes the canonical prescriptive skill.
- [ ] `review-codebase-architecture` becomes the canonical review-only skill.
- [ ] Old architecture skill names resolve through registry aliases.
- [ ] Descriptive mapping remains distinct from design and review.
- [ ] Architecture output uses the smallest useful visualization rather than
      defaulting to Mermaid.
- [ ] `writing-plans` supports inline and durable modes.
- [ ] Compact planning can be promoted without restarting discovery.
- [ ] Each route emits the appropriate next-step signal without rebuilding the
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
