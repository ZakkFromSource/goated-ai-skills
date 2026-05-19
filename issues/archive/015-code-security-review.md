## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Implement `code-security-review` under `skills/engineering/`. The skill performs a static review gate for high-evidence bugs, trust-boundary issues, data leaks, auth problems, injection paths, unsafe config, and exploitable patterns.

## Acceptance criteria

- [x] `skills/engineering/code-security-review/SKILL.md` exists and follows the lean schema.
- [x] The workflow identifies the review scope and changed files before reviewing.
- [x] The review reports only findings with strong evidence.
- [x] The output contract includes finding severity, affected path, evidence, impact, and recommended fix.
- [x] The guardrails state that the skill does not provide full audit coverage.
- [x] The workflow keeps security review separate from standards/spec review.

## Blocked by

- `issues/archive/013-tdd.md`

## User stories addressed

- As an agent user, I can catch high-confidence security and safety regressions before closeout.
- As a reviewer, I can trust that reported findings are evidence-backed and not speculative.
