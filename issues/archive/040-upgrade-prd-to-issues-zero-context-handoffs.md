## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Upgrade `prd-to-issues` so generated issue handoffs carry enough context for future agents who have zero access to the original session, while still keeping detailed executable steps in `writing-plans`.

## Acceptance criteria

- [x] `skills/engineering/prd-to-issues/SKILL.md` is updated to require issue handoffs to include enough context for a fresh agent to start from the issue and linked sources.
- [x] Issue handoffs should include parent PRD path, relevant source links, recommended first-read docs, blockers, acceptance criteria, expected proof, and important scope exclusions when applicable.
- [x] The workflow routes future implementers to `grill-with-docs` before implementation and to `writing-plans` for exact executable steps.
- [x] The workflow warns against relying on hidden chat history, `.local/` notes, or unlinked upstream sources.
- [x] The workflow still avoids bloated implementation transcripts, stale command inventories, and full code snippets unless they prevent a likely mistake.
- [x] The skill remains self-contained after installation and does not require this source repo's root files.

## Blocked by

- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`
- `issues/archive/038-add-writing-plans-skill.md`
- `issues/archive/012-prd-to-issues.md`

## User stories addressed

- As a future implementation agent, I can pick up a local issue without needing the chat session that created it.
- As a maintainer, I can keep PRD-to-issues output durable, source-linked, and not overfit to one moment in the codebase.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm the existing issue template and local conventions.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md
- Related source inspiration: https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md
- Keep V1 local-only. Do not add remote issue tracker creation, labels, milestones, or project-board automation.
