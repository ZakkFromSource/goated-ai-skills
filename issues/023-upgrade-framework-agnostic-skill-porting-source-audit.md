## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Upgrade `framework-agnostic-skill-porting` so it treats a provided source folder, repo slice, or public skill package as a complete package to inventory before adapting it. This prevents future agents from reading only an obvious entrypoint while missing support files that carry real workflow behavior.

Evidence:

- https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills

## Acceptance criteria

- [ ] `skills/agent-workflows/framework-agnostic-skill-porting/SKILL.md` requires a source package manifest before judging a port.
- [ ] `skills/agent-workflows/framework-agnostic-skill-porting/references/source-package-audit.md` exists and is directly linked from `SKILL.md` with clear read conditions.
- [ ] The workflow says a provided source folder or repo slice is recursively inventoried and first-party support files are read before behavior is summarized.
- [ ] The output contract includes `Files/Links Inspected` and `Skipped Files / Why`.
- [ ] The workflow treats templates, references, scripts, examples, assets, and producer/consumer artifacts as source behavior evidence, not optional decoration.
- [ ] Boundary checks distinguish source repo maintenance, installed-skill runtime behavior, and target-project artifacts.
- [ ] Guardrails prevent copying branded names, tool commands, instruction-file precedence, issue-tracker conventions, or docs-layout assumptions as universal GOATED behavior.

## Blocked by

- `issues/archive/008-framework-agnostic-skill-porting.md`

## User stories addressed

- As a maintainer, I can safely adapt an external skill folder without missing support files that define its real behavior.
- As a future agent, I can report exactly what source files I inspected or skipped before recommending a portable GOATED shape.

