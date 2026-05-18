## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Upgrade `prototype` with branch-specific references for logic/state prototypes and UI/layout prototypes. The skill should explicitly select the prototype branch, keep prototypes disposable, and make branch mechanics strong enough to change future agent behavior without hard-coding one framework.

Evidence:

- https://github.com/mattpocock/skills/tree/main/skills/engineering/prototype

## Acceptance criteria

- [ ] `skills/engineering/prototype/SKILL.md` links to `references/logic-prototype.md` and `references/ui-prototype.md` with clear read conditions.
- [ ] The workflow explicitly chooses between logic/state/data/API prototypes and UI/look/layout prototypes before choosing artifacts.
- [ ] Logic prototypes use full-frame terminal interaction as the preferred default for hand-driven state questions while allowing scripts, fixture harnesses, or isolated modules when better.
- [ ] UI prototypes use existing-route variants with shareable switching and production gating as the web default while allowing equivalent non-web controls.
- [ ] The output contract records branch chosen, any branch assumption, entrypoint, verdict, and cleanup state.
- [ ] Guardrails preserve the caveat that throwaway shells do not need tests, while absorbed production behavior does.
- [ ] The skill does not mandate React, Next, browser-only mechanics, Tailwind, `pnpm`, `bun`, or any specific package manager.

## Blocked by

- `issues/archive/011-prototype.md`

## User stories addressed

- As an agent user, I can get the right kind of prototype for a risky question instead of a generic demo.
- As a maintainer, I can keep branch-specific prototype mechanics self-contained without bloating `SKILL.md`.

