# Ticket 011: Produce Concise Docs, Prompts, And Closeouts

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Complete the user-facing output path so documentation, prompts, commit text,
learning capture, compact responses, and final closeouts add only the
information their artifact or decision genuinely requires.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Output And Communication,
  Skill Anatomy, Compression Policy, and Direct Transitions
- `skills/engineering/documentation-writer/SKILL.md`
- `skills/engineering/documentation-cleanup/SKILL.md`
- `skills/engineering/doc-sync/SKILL.md`
- `skills/engineering/commit-message/SKILL.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/learning-capture/SKILL.md`
- `skills/productivity/caveman/SKILL.md`

## Relevant Source Links

- `skills/engineering/documentation-writer/references/`
- `skills/productivity/goated-prompt/references/`
- `skills/productivity/learning-capture/references/`
- `stack/AGENTS.md`

## Acceptance Criteria

- [x] Documentation sync has a compact no-durable-impact result.
- [x] Documentation writing and cleanup remain separate from sync and load only
      for their actual artifact needs.
- [x] Commit-message output defaults to message text without staging, commit,
      push, or command suggestions.
- [x] GOATED prompt output places the finished prompt first and makes
      explanation optional.
- [x] Caveman changes response verbosity without weakening implementation,
      evidence, safety, or required artifact detail.
- [x] Learning capture honors the shared configurable approval policy.
- [x] Skill-specific output deltas consolidate into one task closeout.
- [x] Empty `None` fields and repeated path/check summaries are omitted unless
      omission would mislead.

## Expected Proof

- No-doc-impact and docs-required fixtures.
- Message-only commit fixture.
- Prompt-first fixture.
- Caveman safety and structured-artifact fixtures.
- Confirm-each and standing-consent capture fixtures.
- Multi-skill consolidated-closeout fixture.
- Word-budget and validator output.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`
- `tickets/005-turn-specs-into-delivery-tickets.md`
- `tickets/010-review-and-verify-conditionally.md`

## User Stories Addressed

- Derived: As a user, I receive the useful artifact first and one concise,
  evidence-backed closeout instead of repeated workflow reports.

## Implementation Route

- Use `writing-plans` to migrate these output-producing skills through
  representative artifact scenarios.

## Scope Exclusions

- Do not merge documentation writing, cleanup, and sync into one skill.
- Do not let compact output hide warnings, skipped checks, or residual risk.

## Implementation Proof

- Nine portable fixtures under `stack/fixtures/output-communication/` cover
  no-doc-impact and docs-required paths, message-only commits, prompt-first
  delivery, caveman safety and structured artifacts, confirm-each and standing
  learning-capture consent, and one consolidated multi-skill closeout.
- `uv run python -m unittest tests.test_validate_skills` passed all 75 tests.
- `uv run python scripts/validate_skills.py` passed 34 implemented skills, 34
  registry entries, and every fixture family, including 9 output-and-
  communication scenarios. The shared policy is 1,190 words, within its
  800-1,200 target.
- The seven output-producing skills meet their soft type budgets:
  documentation writer 1,193 words; documentation cleanup 1,199; doc sync
  1,195; commit message 1,159; GOATED prompt 1,194; learning capture 1,200; and
  caveman 677.
- `uv run python -m py_compile scripts/validate_skills.py
  tests/test_validate_skills.py` and `git diff --check` passed.
- Standards/spec review found no acceptance or standards gaps after correcting
  operator-guide and ticket-index drift. Security review was not applicable:
  no trust boundary, credential, persistence, dependency, permission, or
  sensitive configuration changed.
