## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Add `subagent-driven-development` under `skills/engineering/` as the GOATED workflow for using fresh implementer and reviewer agents on implementation tasks while preserving main-agent ownership and single-agent fallback.

## Acceptance criteria

- [ ] `skills/engineering/subagent-driven-development/SKILL.md` exists and follows the lean schema.
- [ ] The workflow uses a fresh implementer per task when subagents are available and a sequential fallback when they are not.
- [ ] The workflow includes spec review, quality review, and final review phases before completion claims.
- [ ] Delegated work statuses include `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
- [ ] Implementer and reviewer prompt templates live under `skills/engineering/subagent-driven-development/references/`.
- [ ] The skill requires subagents to return evidence such as changed paths, commands, test results, assumptions, and concerns.
- [ ] The main agent remains responsible for orchestration, integration, conflict resolution, and final user communication.
- [ ] The workflow routes closeout through `verification-before-completion`.
- [ ] The skill is self-contained after installation and does not require this source repo's root files.

## Blocked by

- `issues/archive/036-add-verification-before-completion-skill.md`
- `issues/038-add-writing-plans-skill.md`
- `issues/archive/014-standards-and-spec-review.md`
- `issues/archive/015-code-security-review.md`

## User stories addressed

- As an agent user, I can ask for parallel implementation help and still get reviewable, evidence-backed work.
- As a maintainer, I can standardize delegated development without assuming every framework has identical subagent tools.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm current repo language for subagent-aware and single-agent-compatible workflows.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md
- Related source inspiration: https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents
- Related reviewer-prompt inspiration: https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md
- Do not require a specific agent product. Use adapter notes for Codex, Claude Code, Hermes, OpenCode, and generic agents where useful.
