## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Add `receiving-code-review` under `skills/engineering/` as the workflow for handling review feedback: verify it before obeying it, clarify unclear items, push back technically when needed, and implement accepted feedback one item at a time.

## Acceptance criteria

- [ ] `skills/engineering/receiving-code-review/SKILL.md` exists and follows the lean schema.
- [ ] The workflow requires understanding each review comment before editing.
- [ ] The workflow distinguishes accepted feedback, rejected feedback with technical rationale, unclear feedback that needs clarification, and non-actionable commentary.
- [ ] The workflow implements one actionable item at a time when practical and verifies each fix before moving on.
- [ ] The workflow routes security-relevant feedback to `code-security-review` and spec/behavior feedback to `standards-and-spec-review` or `tdd` as appropriate.
- [ ] The workflow routes closeout through `verification-before-completion`.
- [ ] The skill is self-contained after installation and does not require this source repo's root files.

## Blocked by

- `issues/036-add-verification-before-completion-skill.md`
- `issues/archive/014-standards-and-spec-review.md`
- `issues/archive/015-code-security-review.md`

## User stories addressed

- As an agent user, I can give review feedback and have the agent handle it thoughtfully instead of blindly agreeing.
- As a maintainer, I can keep review response technical, evidence-backed, and respectful of project intent.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm how this skill should interact with existing review skills.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/receiving-code-review/SKILL.md
- Related source inspiration: https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md
- Keep tone GOATED-native: direct, evidence-backed, and collaborative.
