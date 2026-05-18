## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Define the practical authoring contract for implemented skills so later issues can create consistent, self-contained skill folders. Cover the PRD sections "Skill Schema", "Progressive Disclosure Requirements", "Subagent Requirements", and "Skill Taxonomy".

## Acceptance criteria

- [x] Repo docs state the required frontmatter fields: `name`, `category`, `classification`, `status`, `description`, `triggers`, `outputs`, `depends_on`, and `adapters`.
- [x] Repo docs explain valid category, classification, and status values.
- [x] Repo docs state that `SKILL.md` is the router and operating procedure, while detailed examples, templates, and stack-specific notes belong in directly linked `references/`.
- [x] Repo docs state the soft 300-line `SKILL.md` review threshold.
- [x] Repo docs include the global delegation rule: the main agent owns intent, orchestration, judgment, and user communication.
- [x] This issue does not create actual skill folders or `SKILL.md` files.

## Blocked by

- `issues/archive/001-confirm-scaffold-public-scope.md`

## User stories addressed

- As a maintainer, I can implement future skills without re-deciding schema or structure.
- As an agent user, I can install skills that remain self-contained after copying.
