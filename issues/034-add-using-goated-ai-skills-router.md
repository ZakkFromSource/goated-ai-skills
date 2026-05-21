## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Add a portable `using-goated-ai-skills` router skill under `skills/agent-workflows/`. The skill should help an installed agent choose the right GOATED skill for the user's task while respecting user instructions, project instructions, and tiny-task escape hatches.

## Acceptance criteria

- [ ] `skills/agent-workflows/using-goated-ai-skills/SKILL.md` exists and follows the lean schema.
- [ ] The router distinguishes source-repo maintenance, target-project onboarding, target-project delivery, skill installation/adaptation, tiny one-off tasks, and explicit user overrides.
- [ ] The workflow tells agents to obey user and target-project instructions before GOATED routing advice.
- [ ] Tiny one-off tasks can proceed without full onboarding or planning ceremony.
- [ ] The skill routes PRD-level, architecture, cross-file, repeated, or public-facing work toward `session-start-progressive-disclosure` and `grill-with-docs`.
- [ ] The skill includes adapter notes for Codex, Claude Code, Hermes, OpenCode, and generic agents without depending on runtime bootstrap/plugin automation.
- [ ] The skill is self-contained after installation and does not require this source repo's root files.
- [ ] Runtime bootstrap, automatic skill loading, hook installation, and adapter manifest generation are explicitly out of scope for this issue.

## Blocked by

- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`
- `issues/029-expand-framework-agnostic-skill-creator.md`
- `issues/archive/006-agent-instructions-integrator.md`

## User stories addressed

- As an agent user, I can ask an installed GOATED stack for help and have it select the right skill path without memorizing every skill name.
- As a maintainer, I can add router behavior without changing the V1 docs-first installation model.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm the router fits the current V1 workflow docs.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md
- Keep the GOATED router portable. It should describe routing behavior, not install hooks or enforce runtime activation.
- Implement after `framework-agnostic-skill-porting` has been renamed and expanded so the router can reference the current public skill name.
- Make clear that installed skills are copied/adapted artifacts and should not depend on this source repo's issue files.
