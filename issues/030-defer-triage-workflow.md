## Parent PRD

`issues/prd-goated-ai-skills-v1-additions.md`

## Type

AFK

## What to build

Record the upstream `triage` workflow as deferred/out of scope for V1. It is useful future work, but V1 remains local/docs-first and should not add remote issue tracker labels, comments, closing behavior, or state-machine mutation.

## Acceptance criteria

- [ ] `.out-of-scope/future-automation-and-validation.md` records issue-tracker triage workflows as deferred beyond V1.
- [ ] The deferred note mentions remote issue tracker state, label mapping, generated comments, closing issues, and reporter follow-up as reasons to defer.
- [ ] No `triage` skill folder is added in V1.
- [ ] Any useful future concepts are described as V1.1/post-V1 possibilities, not current acceptance blockers after this issue is complete.

## Blocked by

- None - can start immediately

## User stories addressed

- As a maintainer, I can preserve a promising future workflow without expanding V1 into remote tracker operations.
- As an agent user, I can trust V1 remains local-first and docs-first.

## Implementation notes

- Use the upstream package as deferred inspiration: https://github.com/mattpocock/skills/tree/main/skills/engineering/triage
- Do not implement issue tracker adapters, labels, remote comments, or close operations in V1.
