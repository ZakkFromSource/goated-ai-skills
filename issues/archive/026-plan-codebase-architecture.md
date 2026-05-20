## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `plan-codebase-architecture` under `skills/engineering/`. The skill plans a source-grounded architecture blueprint for a new project setup or clarified feature before implementation begins, using GOATED deep-module architecture language.

## Acceptance criteria

- [x] `skills/engineering/plan-codebase-architecture/SKILL.md` exists and follows the lean schema.
- [x] The skill requires a clarified brief, PRD, issue, or `grill-with-docs` result before writing a durable blueprint.
- [x] The workflow produces interface-level architecture blueprints, not speculative file trees.
- [x] The output contract includes planned modules, interfaces, hidden complexity, dependency/seam decisions, test surfaces, slice order, risks, open questions, and RFC/ADR triggers.
- [x] Durable blueprint defaults are mode-based: `docs/agents/architecture-plan.md` for project-wide setup and `docs/architecture/<slug>-architecture-plan.md` for feature-specific planning.
- [x] Guardrails keep the skill design-only and route PRD, issue breakdown, RFC/ADR capture, implementation, existing-code repair, and current-state diagrams to companion skills.
- [x] Delegation notes support bounded evidence gathering and competing interface blueprint passes.
- [x] V1 docs mention the skill in the public engineering workflow where needed.

## Blocked by

- `issues/archive/019-improve-codebase-architecture.md`

## User stories addressed

- As an agent user, I can plan project or feature architecture before implementation starts.
- As a maintainer, I can steer future implementation toward deep modules, clear interfaces, real seams, and testable slices.
