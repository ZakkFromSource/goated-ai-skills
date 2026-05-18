## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `commit-message` under `skills/engineering/`. The skill drafts a concise, information-rich commit message from local diffs, originating specs, and verified checks.

## Acceptance criteria

- [ ] `skills/engineering/commit-message/SKILL.md` exists and follows the lean schema.
- [ ] The workflow inspects local diffs and relevant issue or PRD context before drafting.
- [ ] The output contract includes a commit subject, optional body, verification summary, and known caveats.
- [ ] The guardrails state that the skill does not stage, commit, or push changes.
- [ ] The workflow works with generic git context and treats platform-specific context as optional.
- [ ] The skill avoids exposing private details in public commit text.

## Blocked by

- `issues/013-tdd.md`
- `issues/014-standards-and-spec-review.md`
- `issues/015-code-security-review.md`
- `issues/016-doc-sync.md`

## User stories addressed

- As an agent user, I can get a clear commit message after verified work.
- As a maintainer, I can preserve useful change history without coupling the skill to one hosting platform.
