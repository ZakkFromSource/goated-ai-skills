## Parent PRD

Planned parent PRD: `issues/prd-goated-ai-skills-documentation-writer.md`, to be created and approved by `issues/048-draft-documentation-writer-prd.md` before this issue starts.

## Type

HITL

## What to build

Implement `documentation-writer` under `skills/engineering/` after the manuals-first PRD is approved.

The skill should create or update durable user-facing documentation such as manuals, operator guides, onboarding guides, and product docs. It should not replace `doc-sync`, and it should not own static-site generation in the first scope unless the approved PRD explicitly changes that.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `skills/engineering/README.md`
- `issues/prd-goated-ai-skills-documentation-writer.md`
- `issues/048-draft-documentation-writer-prd.md`
- `skills/engineering/doc-sync/SKILL.md`
- `skills/engineering/write-a-prd/SKILL.md`
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `skills/README.md` - lean schema, support-file policy, delegation contract, and implementation boundary.
- `skills/engineering/doc-sync/SKILL.md` - companion skill for documentation drift.
- `docs/how-to-use.md` - public operator manual that will need a skill reference after implementation.
- `README.md` and `skills/engineering/README.md` - skill catalog surfaces.

## Acceptance criteria

- [ ] `skills/engineering/documentation-writer/SKILL.md` exists and follows the lean schema.
- [ ] The skill is scoped to manuals-first durable documentation, using the approved PRD's audience, goals, and non-goals.
- [ ] The workflow gathers source evidence before writing docs and records assumptions, gaps, and unresolved product questions.
- [ ] The workflow chooses target-project documentation locations from existing conventions first, with a safe default only when none exists.
- [ ] The output contract covers created/updated docs, source evidence used, audience, scope, verification, doc-sync relationship, and remaining gaps.
- [ ] The skill routes documentation drift after implementation to `doc-sync` instead of duplicating that workflow.
- [ ] Delegation supports bounded source summarization, outline review, audience fit review, and documentation QA.
- [ ] Guardrails prevent private data, credentials, raw transcripts, unverified product claims, and static-site generation unless approved by the PRD.
- [ ] `README.md`, `docs/how-to-use.md`, and `skills/engineering/README.md` list the skill only after the implementation is complete.

## Expected proof

- Manual review of the new `SKILL.md` against lean schema and self-contained skill requirements.
- Targeted `rg` for `documentation-writer`, `doc-sync`, `manual`, `webpage`, `static site`, and stale planned/implemented wording.
- Public-boundary pass for private names, credentials, client data, sensitive context, and source-repo/runtime confusion.
- Manual Markdown review of updated catalog docs.

## Blocked by

- `issues/048-draft-documentation-writer-prd.md`
- Maintainer approval that `issues/prd-goated-ai-skills-documentation-writer.md` is ready for implementation.

## User stories addressed

- As an agent user, I can create durable manuals and product docs from source evidence.
- As a maintainer, I can keep manual authoring separate from documentation drift sync.

## Implementation route

- Use `grill-with-docs` if the approved PRD still has scope ambiguity.
- Use `writing-plans` before creating the skill folder.
- Use `doc-sync` and `verification-before-completion` before closeout.

## Scope exclusions

- Do not start before the PRD exists and is approved.
- Do not implement webpage or static-site generation unless the approved PRD explicitly includes it.
- Do not add private/domain-specific documentation assumptions to public main.

