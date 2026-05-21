## Parent PRD

`issues/prd-goated-ai-skills-v1-additions.md`

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Rename and expand `framework-agnostic-skill-porting` into `framework-agnostic-skill-creator`. The active skill should cover both creating a new GOATED skill from clarified intent and porting an existing skill, prompt, command, or workflow into GOATED shape.

## Acceptance criteria

- [ ] The folder is renamed from `skills/agent-workflows/framework-agnostic-skill-porting/` to `skills/agent-workflows/framework-agnostic-skill-creator/`.
- [ ] Frontmatter and heading use `framework-agnostic-skill-creator`.
- [ ] The skill has two explicit modes: create from clarified intent and port from source material.
- [ ] Port mode keeps `references/source-package-audit.md` as a required reference when source packages include adjacent support files.
- [ ] Create mode includes guidance for trigger-focused descriptions, script-vs-prose decisions, support-file splitting, and final review checks.
- [ ] Create mode folds in Superpowers `writing-skills` conventions, including trigger-only descriptions, pressure scenarios, and support-file pragmatism.
- [ ] The skill adds or updates `references/skill-evaluation.md` with TDD-for-skills guidance: RED baseline, pressure scenarios, rationalization capture, and GREEN verification.
- [ ] Active docs and context references use "skill creation and porting" rather than presenting porting as the whole workflow.
- [ ] Archived historical issues may keep their old names, but active runtime docs should point to the new skill name.

## Blocked by

- `issues/archive/008-framework-agnostic-skill-porting.md`
- `issues/archive/023-upgrade-framework-agnostic-skill-porting-source-audit.md`
- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`

## User stories addressed

- As a maintainer, I can create a new GOATED skill from clarified intent without pretending it came from an external source.
- As a maintainer, I can still port existing workflows through the stricter source package audit path.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm current authoring-contract language and public-boundary rules.
- Harvest useful heuristics from upstream write-a-skill: https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill
- Harvest useful Superpowers skill-writing guidance from:
  - https://github.com/obra/superpowers/tree/main/skills/writing-skills
  - https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md
- Preserve GOATED's lean schema, public-boundary checks, dependency classification, adapter notes, delegation contract, and self-contained skill validation.
- Do not add a standalone `write-a-skill` skill.
