## Parent PRD

`issues/prd-goated-ai-skills-v1-additions.md`

## Type

AFK

## What to build

Update `architecture-design-map` so it handles quick "zoom out" requests as an inline mode. This should help users understand an unfamiliar code area by mapping the surrounding modules, callers, and project terms without creating a durable artifact by default.

## Acceptance criteria

- [ ] `skills/engineering/architecture-design-map/SKILL.md` includes triggers for "zoom out", "go up a layer", and unfamiliar-code orientation.
- [ ] The workflow distinguishes quick inline zoom-out from durable architecture-map creation.
- [ ] The quick mode inspects the focused file, symbol, feature, or subsystem plus nearby callers/importers before summarizing.
- [ ] The output contract covers a concise module/caller map, source references, uncertainty notes, and recommended next files to inspect.
- [ ] Guardrails prohibit refactor recommendations, architecture planning, or folder-name-only claims during quick zoom-out mode.
- [ ] The skill remains self-contained after installation.

## Blocked by

- `issues/archive/018-architecture-design-map.md`

## User stories addressed

- As an agent user, I can ask the agent to zoom out from unfamiliar code and get a source-grounded map of how it fits.
- As a future agent, I can distinguish quick orientation from durable architecture documentation.

## Implementation notes

- Use the upstream concept as inspiration: https://github.com/mattpocock/skills/blob/main/skills/engineering/zoom-out/SKILL.md
- Do not add a standalone `zoom-out` skill.
- Do not broaden `architecture-design-map` into refactor planning; route that to `improve-codebase-architecture` or `plan-codebase-architecture`.
