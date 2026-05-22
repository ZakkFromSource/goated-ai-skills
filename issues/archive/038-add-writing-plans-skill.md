## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Add `writing-plans` under `skills/engineering/` as the GOATED skill for turning an approved issue or scoped task into an executable implementation plan immediately before implementation.

## Acceptance criteria

- [x] `skills/engineering/writing-plans/SKILL.md` exists and follows the lean schema.
- [x] The skill requires source inspection before exact file paths, commands, snippets, or expected outputs are written.
- [x] Plans include exact files to inspect or edit, commands to run, expected evidence, TDD steps when applicable, review steps, and doc-sync/verification closeout.
- [x] The default output is inline in chat or under an ignored local path such as `.local/plans/`, unless the user asks for tracked output.
- [x] The skill explains how to keep durable issues concise while putting volatile step-by-step details in just-in-time plans.
- [x] The workflow routes implementation to `tdd`, `subagent-driven-development`, or direct execution depending on task size and risk.
- [x] The skill is self-contained after installation and does not require this source repo's root files.

## Blocked by

- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`
- `issues/archive/036-add-verification-before-completion-skill.md`
- `issues/archive/012-prd-to-issues.md`

## User stories addressed

- As a future agent, I can convert an approved issue into exact implementation steps without relying on the original session history.
- As a maintainer, I can keep issue handoffs durable and concise while still enabling executable plans.

## Implementation notes

- Used `grill-with-docs`-equivalent planning to confirm inline-first output and one compact checklist reference.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md
- Related source inspiration: https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md
- No tracked sample plans were created.
