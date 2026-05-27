## Parent PRD

No separate parent PRD. This issue is part of the user-approved 2026-05-26 post-V1 improvement issue set. Use this file as the implementation contract.

## Type

AFK

## What to build

Draft a manuals-first PRD for a future `documentation-writer` skill.

The PRD should scope the first release to user manuals, operator guides, onboarding guides, and durable product documentation. Documentation webpages or static-site generation should be deferred unless the PRD explicitly records a later phase.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `skills/engineering/README.md`
- `skills/engineering/doc-sync/SKILL.md`
- `skills/engineering/write-a-prd/SKILL.md`
- `docs/how-to-use.md`
- `issues/archive/016-doc-sync.md`

## Relevant source links

- `skills/engineering/doc-sync/SKILL.md` - existing documentation drift workflow that the new skill must not duplicate.
- `skills/engineering/write-a-prd/SKILL.md` - PRD output shape and source-grounded planning behavior.
- `skills/README.md` - lean schema and new skill creation rules.
- `CONTEXT.md` - source repo, installed skill, and target project boundaries.

## Acceptance criteria

- [ ] A new PRD is drafted at `issues/prd-goated-ai-skills-documentation-writer.md`.
- [ ] The PRD scopes v1 of `documentation-writer` to manuals-first durable documentation: user manuals, operator guides, onboarding guides, and product docs.
- [ ] The PRD clearly distinguishes `documentation-writer` from `doc-sync`: authoring planned docs versus syncing drift from changed behavior.
- [ ] The PRD defines audience, goals, non-goals, requirements, acceptance criteria, risks, open questions, and source evidence.
- [ ] The PRD defers documentation webpages/static-site generation unless explicitly captured as a future phase or non-goal.
- [ ] The PRD preserves public-safe, framework-agnostic, self-contained skill requirements.
- [ ] The PRD identifies the follow-up implementation issue as `issues/049-implement-documentation-writer-manuals-first.md`.

## Expected proof

- Manual Markdown review of the new PRD.
- Targeted `rg` checks for `documentation-writer`, `doc-sync`, `manual`, `webpage`, `static site`, and stale scope wording.
- Review that the PRD is ready for issue 049 or explicitly marks blockers/open questions.

## Blocked by

- None - can start immediately.

## User stories addressed

- As an agent user, I can ask for durable user-facing documentation, not only doc drift cleanup after implementation.
- As a maintainer, I can approve the new skill boundary before a skill folder is created.

## Implementation route

- Use `write-a-prd` to draft the PRD, with source-repo maintainer instructions taking precedence.
- Use `doc-sync` after writing if public docs need to mention the planned skill only after approval.

## Scope exclusions

- Do not create `skills/engineering/documentation-writer/` in this issue.
- Do not implement documentation website generation.
- Do not list the skill as implemented in category READMEs before issue 049 is complete.

