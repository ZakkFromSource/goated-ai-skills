## Parent PRD

No separate parent PRD. This issue is part of the user-approved 2026-05-26 post-V1 improvement issue set. Use this file as the implementation contract.

## Type

AFK

## What to build

Update `project-standards-calibration` so onboarding can capture a user-confirmed code style posture when project evidence does not already decide it.

The first supported preference should distinguish beginner-friendly code from advanced/terse code. The captured preference must be stored as `preference-only` and must not override documented standards or tooling-enforced style.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `docs/agents/project-standards.md`
- `docs/how-to-use.md`
- `skills/agent-workflows/project-standards-calibration/SKILL.md`
- `skills/engineering/standards-and-spec-review/SKILL.md`

## Relevant source links

- `skills/agent-workflows/project-standards-calibration/SKILL.md` - existing workflow for documented standards, inferred conventions, user preferences, and enforcement levels.
- `docs/agents/project-standards.md` - current standards profile shape and enforcement definitions.
- `skills/engineering/standards-and-spec-review/SKILL.md` - downstream consumer of documented standards, inferred conventions, and user-confirmed preferences.

## Acceptance criteria

- [ ] `project-standards-calibration` asks about code style preference only after inspecting documented standards, tooling, and inferred conventions.
- [ ] The workflow offers a beginner-friendly posture such as clear names, straightforward structure, and helpful comments.
- [ ] The workflow offers an advanced/terse posture such as denser abstractions allowed when justified, fewer comments, and stronger reliance on local conventions.
- [ ] The selected posture is written to `docs/agents/project-standards.md` under `User-Confirmed Preferences` with `preference-only` enforcement.
- [ ] The skill explicitly says the preference cannot override formatters, linters, contributor docs, existing style guides, or stronger project instructions.
- [ ] Public docs mention the preference capture only where it helps explain onboarding; do not turn it into a generic style lecture.

## Expected proof

- Manual review of `project-standards-calibration` output contract and guardrails.
- Targeted `rg` checks for `beginner`, `advanced`, `preference-only`, `User-Confirmed Preferences`, and stale standards wording.
- Scenario check: if local docs/tooling already define code style, the skill records that source instead of asking the preference question.

## Blocked by

- None - can start immediately.

## User stories addressed

- As an agent user, I can tell future agents whether I prefer highly readable beginner-friendly code or a terser advanced style.
- As a maintainer, I can keep preferences separate from real project standards.

## Implementation route

- Use `writing-plans` for exact edits after inspecting the listed files.
- Use `doc-sync` after the skill change because the onboarding public contract changes.

## Scope exclusions

- Do not add a global GOATED default code style for every project.
- Do not make the preference binary-only forever; implement the first option set without blocking future expansion.
- Do not add formatter, linter, or CI tooling in this issue.

