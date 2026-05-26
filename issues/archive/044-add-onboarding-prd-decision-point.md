## Parent PRD

No separate parent PRD. This issue is part of the user-approved 2026-05-26 post-V1 improvement issue set. Use this file as the implementation contract.

## Type

AFK

## What to build

Add an optional `write-a-prd` decision point to Target Project Onboarding for cases where onboarding uncovers project-level product scope, roadmap intent, or acceptance criteria needed before architecture planning or issue breakdown.

This is a routing and documentation upgrade, not a requirement that onboarding always creates a PRD.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `docs/how-to-use.md`
- `docs/install.md`
- `README.md`
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md`
- `skills/engineering/write-a-prd/SKILL.md`
- `skills/engineering/architecture-design-map/SKILL.md`
- `skills/engineering/plan-codebase-architecture/SKILL.md`

## Relevant source links

- `docs/how-to-use.md` - current Pipeline 1 and Pipeline 2 diagrams.
- `README.md` - public workflow summary and source/target-project boundary language.
- `docs/install.md` - target-project artifact defaults and docs-first installation model.
- `skills/engineering/architecture-design-map/SKILL.md` - descriptive map guardrails.
- `skills/engineering/plan-codebase-architecture/SKILL.md` - existing `write-a-prd` routing when product scope is unclear.

## Acceptance criteria

- [ ] Target Project Onboarding docs include optional `write-a-prd` routing only when onboarding needs project-level product scope, roadmap intent, or acceptance criteria.
- [ ] `architecture-design-map` remains described as a current-state, source-grounded mapping skill, not a PRD prerequisite or planning substitute.
- [ ] `README.md`, `docs/how-to-use.md`, and `docs/install.md` consistently mention conditional `docs/prds/` artifacts without making PRDs mandatory for onboarding.
- [ ] `using-goated-ai-skills` can route onboarding toward `write-a-prd` when the onboarding goal itself is PRD-level, while preserving tiny-task and delivery distinctions.
- [ ] `write-a-prd` and `plan-codebase-architecture` remain aligned: fuzzy product scope routes to PRD creation before durable architecture planning.
- [ ] No wording implies runtime automation, installer behavior, or automatic PRD generation.

## Expected proof

- Targeted `rg` checks for `Target Project Onboarding`, `write-a-prd`, `architecture-design-map`, `docs/prds`, and stale pipeline diagrams.
- Manual Markdown review of updated docs and skills.
- Self-contained skill review confirming installed skills do not rely on this source repo's root files.

## Blocked by

- None - can start immediately.

## User stories addressed

- As an agent user, I can use onboarding to capture project-level product intent when it matters before architecture planning.
- As a maintainer, I can keep onboarding lightweight by making PRD creation conditional instead of mandatory.

## Implementation route

- Use `grill-with-docs` before implementation if the onboarding/delivery boundary becomes unclear.
- Use `writing-plans` for exact edit steps after reading the listed sources.

## Scope exclusions

- Do not implement a new PRD skill.
- Do not require every onboarded project to have `docs/prds/`.
- Do not turn `architecture-design-map` into a planning or refactor skill.

