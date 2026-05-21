## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Add `verification-before-completion` under `skills/engineering/` as the shared closeout gate for claims of completion, correctness, review readiness, or successful implementation.

## Acceptance criteria

- [x] `skills/engineering/verification-before-completion/SKILL.md` exists and follows the lean schema.
- [x] The skill requires fresh evidence before success claims, such as command output, test results, inspected diffs, rendered artifacts, screenshots, or source reads.
- [x] The workflow distinguishes verified facts, assumptions, skipped checks, known failures, and residual risk.
- [x] The skill prevents stale proof reuse by requiring evidence gathered after the relevant change or review scope is known.
- [x] The skill covers subagent reports by requiring the main agent to sanity-check or reproduce important evidence before final claims.
- [x] The output contract includes a concise verification summary with command names, results, skipped checks, and remaining risk.
- [x] The skill is self-contained after installation and does not require this source repo's root files.

## Blocked by

- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`

## User stories addressed

- As an agent user, I can tell what was actually verified before an agent says work is complete.
- As a maintainer, I can wire one closeout discipline through multiple GOATED engineering skills.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm current closeout language in implemented skills.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
- Keep this skill broadly usable. It should not require a specific test runner, git host, CI system, or framework.
- Do not turn this into a replacement for `tdd`, `standards-and-spec-review`, `code-security-review`, or `doc-sync`; it verifies completion claims and routes missing proof.
