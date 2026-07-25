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

- [ ] Documentation sync has a compact no-durable-impact result.
- [ ] Documentation writing and cleanup remain separate from sync and load only
      for their actual artifact needs.
- [ ] Commit-message output defaults to message text without staging, commit,
      push, or command suggestions.
- [ ] GOATED prompt output places the finished prompt first and makes
      explanation optional.
- [ ] Caveman changes response verbosity without weakening implementation,
      evidence, safety, or required artifact detail.
- [ ] Learning capture honors the shared configurable approval policy.
- [ ] Skill-specific output deltas consolidate into one task closeout.
- [ ] Empty `None` fields and repeated path/check summaries are omitted unless
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
