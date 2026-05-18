## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `prototype` under `skills/engineering/`. The skill creates target-project-local throwaway artifacts to answer one focused question before PRD creation or inside focused issue exploration.

## Acceptance criteria

- [ ] `skills/engineering/prototype/SKILL.md` exists and follows the lean schema.
- [ ] The workflow requires the prototype question to be stated before building.
- [ ] The workflow locates prototype artifacts close to the relevant code or route and marks them clearly as prototypes.
- [ ] The guardrails avoid persistence by default and skip production polish.
- [ ] The output contract includes question, approach, artifacts touched, verdict, and whether the prototype was deleted or absorbed.
- [ ] The workflow requires cleanup or explicit handoff before final closeout.

## Blocked by

- `issues/archive/003-session-start-progressive-disclosure.md`
- `issues/009-grill-with-docs.md`

## User stories addressed

- As an agent user, I can answer risky product or technical questions cheaply.
- As a maintainer, I can keep prototypes from becoming accidental production behavior.
