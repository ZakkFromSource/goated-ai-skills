## Parent PRD

No separate parent PRD. This issue is part of the user-approved 2026-05-26 post-V1 improvement issue set. Use this file as the implementation contract.

## Type

AFK

## What to build

Audit the named GOATED skills and add minimal routing or guardrail language where it helps preserve the project philosophy: vertical behavior slices, deep modules with small public interfaces, and focused task ownership.

This is a calibration pass. Do not paste the full philosophy into every skill.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md`
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md`
- `skills/engineering/architecture-design-map/SKILL.md`
- `skills/engineering/plan-codebase-architecture/SKILL.md`
- `skills/engineering/prototype/SKILL.md`
- `skills/engineering/write-a-prd/SKILL.md`
- `skills/engineering/prd-to-issues/SKILL.md`
- `skills/engineering/writing-plans/SKILL.md`
- `skills/engineering/subagent-driven-development/SKILL.md`
- `skills/agent-workflows/handoff/SKILL.md`

## Relevant source links

- `CONTEXT.md` - normative deep-module, seam, and progressive-disclosure language.
- `skills/engineering/subagent-driven-development/references/implementer-prompt.md` - existing compact GOATED quality bar.
- `skills/engineering/subagent-driven-development/references/reviewer-prompt.md` - existing reviewer quality guidance.
- `skills/engineering/writing-plans/references/plan-review-checklist.md` - existing planning quality checks.
- `skills/engineering/tdd/references/deep-modules.md` - deeper reference for module-design philosophy.

## Acceptance criteria

- [ ] All named skills are audited for existing vertical-slice, deep-module, and focused-task language.
- [ ] `agent-instructions-integrator` and `using-goated-ai-skills` get only compact routing language for serious implementation or architecture work.
- [ ] `architecture-design-map` stays descriptive and gains, at most, a guardrail against turning maps into philosophy-driven refactor advice.
- [ ] `prototype` gains, if needed, a small note that absorbable logic/API prototypes should preserve a small useful interface and avoid production-like scaffolding.
- [ ] `write-a-prd` gains, if needed, a light cue that implementation notes should support later vertical issue slicing without becoming architecture design.
- [ ] `plan-codebase-architecture`, `prd-to-issues`, `writing-plans`, `subagent-driven-development`, and existing subagent prompts are left unchanged when they already satisfy the quality bar.
- [ ] `handoff` mentions next slice or module focus only when relevant; it must not become a philosophy recap.
- [ ] The final report lists which skills changed and which were intentionally left unchanged.

## Expected proof

- Targeted `rg` before and after for `vertical`, `deep module`, `public interface`, `focused`, `horizontal`, and `shallow`.
- Manual review against the soft 300-line `SKILL.md` cap and self-contained skill rule.
- Public-boundary review confirming no private project assumptions were added.

## Blocked by

- None - can start immediately.

## User stories addressed

- As an agent user, I get consistent GOATED behavior across routing, planning, issue slicing, delegation, and handoff.
- As a maintainer, I can reinforce the philosophy without bloating every skill.

## Implementation route

- Use `writing-plans` for exact edits and no-op decisions.
- Use `doc-sync` if docs or category READMEs need alignment after the audit.

## Scope exclusions

- Do not rewrite already strong skills just to touch every named file.
- Do not add architecture advice to purely descriptive or continuity skills unless it preserves existing evidence.
- Do not create a shared global reference file unless the audit proves repeated text would otherwise bloat skills.

