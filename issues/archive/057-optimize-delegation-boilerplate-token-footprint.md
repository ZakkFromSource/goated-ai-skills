## Parent PRD

No separate parent PRD. This issue continues the user-approved 2026-06-11 GOATED AI Skills token-optimization agenda from `issues/053-optimize-hotspot-skill-token-footprint.md`, `issues/054-optimize-code-security-review-token-footprint.md`, `issues/055-optimize-architecture-vocabulary-token-footprint.md`, and `issues/056-optimize-reference-read-gate-token-footprint.md`.

## Type

AFK

## What to build

Optimize repeated `## Delegation` boilerplate across implemented `SKILL.md` files without weakening subagent-aware behavior, single-agent fallback behavior, evidence requirements, delegated status enums, or controller next actions.

The intended change is selective delegation-section compression:

- AUDIT all implemented `SKILL.md` files with `## Delegation` sections.
- IDENTIFY repeated sentence patterns around main-agent ownership, bounded subagent use, evidence return requirements, delegated status handling, and unavailable-subagent fallback.
- REFINE each affected delegation section into denser wording while preserving skill-specific delegation boundaries.
- PRESERVE delegated status enums and controller behavior where a subagent result can change the main agent's next action.
- PRESERVE lightweight delegation guidance for simple evidence-gathering skills without inflating them into enum-heavy workflows.
- AVOID moving delegation behavior into repo-level or cross-skill shared references because installed skills must remain self-contained.

The optimization target is repeated boilerplate wording, not the delegation contract itself.

## Grill decision

After issue `056`, the next slice should be delegation boilerplate compression rather than the broader `depends_on` sweep, verification repetition, TDD guardrail compression, or a before/after eval suite.

Rationale:

- `056` carried forward the user's preference that the broad `depends_on` sweep should happen after focused specialist optimizations.
- Delegation remains the largest non-frontmatter follow-up candidate at about 4.9k words across the suite.
- The pattern is visible and reviewable: most sections repeat main-agent ownership, bounded subagent roles, evidence requirements, status handling, and single-agent fallback.
- The project standards require workflows to stay subagent-aware and single-agent-compatible, so this issue should compress wording while preserving behavior.
- A focused delegation pass is safer before touching dependency frontmatter because it can be reviewed against the existing `skills/README.md` Delegation Contract.

Recommended posture: apply a **preserve behavior, compress expression** rule.

- For enum-heavy delegation sections, keep `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED` behavior explicit, but compress repeated explanatory scaffolding.
- For lightweight delegation sections, keep bounded evidence-gathering guidance and fallback behavior without introducing unnecessary status enums.
- If a section already earns its length because the skill's delegation behavior is specialized, leave it mostly intact and record the skip.

## Grill refinement decisions

The implementation plan should use these settled decisions from the docs-grounded refinement session:

- Use a two-lane compression model:
  - **Lane A: enum-heavy delegation sections** keep delegated status enums and controller actions, compressed into a consistent shape.
  - **Lane B: lightweight delegation sections** keep bounded evidence requirements and single-agent fallback without adding status enums.
- Keep this as one suite-wide selective pass across all 30 `## Delegation` sections.
- Use a shared compact Lane A shape with skill-specific content:
  - `Main owns...`
  - `Delegate only...`
  - `Require...`
  - `Status handling...`
  - `Fallback...`
- Preserve the explicit Lane A status return pattern: `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
- Preserve per-status controller actions inline in each enum-heavy `SKILL.md`; do not rely on a generic shared meaning.
- Use moderate compression: reduce repeated scaffolding first while preserving skill-specific nouns and behavioral cues such as `false-positive control`, `public interface`, `red or green evidence`, `doc status`, and `residual drift risk`.
- Patch by risk band rather than directory:
  - audit and edit/skip ledger first;
  - Lane B lightweight sections;
  - Lane A enum-heavy sections;
  - discipline-heavy and specialized sections last.
- Use subagents before edits for read-only classification and risk-flagging, then after edits for independent behavior-preservation review.
- Add the plan and decisions directly to this issue so future agents do not depend on chat history.
- Do not use a hard token-savings target. The success bar is behavior-preserving reduction plus measured before/after counts, duplicate scaffolding reduction, preserved status/evidence contracts, and clean review.

## Audit evidence to preserve

From the full-suite audit and prior optimization issues:

- 30 `SKILL.md` files total about 52k words before the first optimization slice.
- Frontmatter was about 8.6k words, or 16.6% of all `SKILL.md` words.
- `depends_on` was the largest frontmatter cost at about 3.4k words.
- Body-section hotspots included:
  - `Workflow`: about 19.3k words
  - `Guardrails`: about 6.1k words
  - `Output Contract`: about 6.0k words
  - `Delegation`: about 4.9k words
- Engineering was the heaviest category at about 36.8k words across 19 skills.
- The suite is structurally healthy; the main optimization is to keep `SKILL.md` as hot-path router/procedure and move or compress detail without deleting behavior-changing guidance.

Current delegation scan:

- 30 implemented `SKILL.md` files include `## Delegation` sections.
- Total delegation-section footprint is about 4,879 words.
- Highest-word delegation sections at planning time:
  - `skills/engineering/doc-sync/SKILL.md` - about 244 words
  - `skills/engineering/code-security-review/SKILL.md` - about 240 words
  - `skills/engineering/plan-codebase-architecture/SKILL.md` - about 234 words
  - `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` - about 232 words
  - `skills/engineering/tdd/SKILL.md` - about 228 words
  - `skills/engineering/improve-codebase-architecture/SKILL.md` - about 226 words
  - `skills/engineering/documentation-writer/SKILL.md` - about 225 words
  - `skills/engineering/prototype/SKILL.md` - about 215 words
  - `skills/engineering/standards-and-spec-review/SKILL.md` - about 214 words
  - `skills/engineering/writing-plans/SKILL.md` - about 199 words
- Roughly half the suite uses explicit delegated status enums; the rest uses lighter evidence, assumptions, uncertainty, and inspected-path guidance.

## Settled optimization posture

- Optimize selectively, case by case.
- Reduce always-loaded tokens while preserving the parts that change agent behavior.
- Move or compress late-stage templates, long checklists, repeated boilerplate, duplicate reference pointers, and verbose dependency prose.
- Preserve inline stop rules, proof gates, safety/privacy boundaries, false-positive controls, routing decisions, approval gates, and discipline-heavy reminders.
- Preserve delegated status enums when they affect controller behavior.
- Add local `references/` only inside each affected skill folder when they improve skill capability or keep `SKILL.md` lean; this issue is not expected to need new support files.
- Avoid repo-level shared references unless the installed-skill distribution model changes.
- Use `goated-prompt` and the IDK glossary as style inspiration for information-dense wording, not as a total voice transplant.
- Use uppercase IDK action keywords mostly in templates, output contracts, and compact high-value commands; keep normal explanatory prose readable.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `docs/agents/context-matrix.md`
- `docs/agents/project-standards.md`
- `issues/053-optimize-hotspot-skill-token-footprint.md`
- `issues/054-optimize-code-security-review-token-footprint.md`
- `issues/055-optimize-architecture-vocabulary-token-footprint.md`
- `issues/056-optimize-reference-read-gate-token-footprint.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/goated-prompt/references/idk-glossary.md`
- Candidate `SKILL.md` files from the delegation scan, opened only as needed.
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `AGENT.md` - maintainer contract, public boundary, self-contained installed skills, soft 300-line cap, and subagent policy.
- `CONTEXT.md` - definitions for `SKILL.md`, discipline-heavy skills, delegated status enums, subagent-aware and single-agent-compatible workflows, and source-repo/installed-skill/target-project boundaries.
- `skills/README.md` - lean schema, Delegation Contract, progressive disclosure contract, and installed-skill self-containment rule.
- `docs/agents/project-standards.md` - documented standard that workflows remain subagent-aware and single-agent-compatible.
- `issues/053-optimize-hotspot-skill-token-footprint.md` - first token optimization wave and settled posture.
- `issues/054-optimize-code-security-review-token-footprint.md` - discipline-heavy specialist extraction pattern.
- `issues/055-optimize-architecture-vocabulary-token-footprint.md` - focused family optimization pattern.
- `issues/056-optimize-reference-read-gate-token-footprint.md` - reference gate compression and follow-up decision context.

## Acceptance criteria

- [ ] All edited `SKILL.md` files still follow the lean schema.
- [ ] Every edited skill remains self-contained after installation and depends only on its own folder plus target-project evidence at runtime.
- [ ] No repo-level, category-level, or cross-skill shared delegation reference is introduced.
- [ ] No runtime bootstrap, automatic loading, generated manifest, installer, hook, adapter automation, eval harness, CI check, or token dashboard is introduced.
- [ ] No installed Codex skill copies outside this source repo are edited.
- [ ] The implementation audits all 30 implemented `SKILL.md` delegation sections and records which files were edited or intentionally skipped.
- [ ] Repeated main-agent ownership prose is compressed without removing who owns final judgment, user intent, integration, and user communication.
- [ ] Repeated subagent-use prose is compressed without allowing broad unsupervised rewrites, unbounded delegation, or duplicate work.
- [ ] Repeated evidence-return prose is compressed without removing inspected paths, commands run or skipped, source evidence, assumptions, confidence, uncertainty, residual risk, or changed-file evidence where the skill needs them.
- [ ] Delegated status enums remain explicit wherever `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED` can change the controller's next action.
- [ ] Controller behavior for each retained status remains clear enough that a future agent knows whether to integrate, inspect concerns, provide missing context, narrow scope, re-dispatch, report risk, or escalate.
- [ ] Lightweight delegation sections are not inflated into enum-heavy workflows when simple evidence requirements are enough.
- [ ] Discipline-heavy skills preserve the delegation reminders that prevent shortcutting, overclaiming, false-positive reporting, unsafe edits, or skipped verification.
- [ ] `subagent-driven-development` preserves its controller-specific delegation lifecycle and does not become a generic delegation paragraph.
- [ ] `verification-before-completion` preserves final-claim ownership and delegated-evidence sanity-check behavior.
- [ ] `tdd` preserves red/green evidence, public-interface, and no-internal-coupling delegation boundaries.
- [ ] `code-security-review` preserves concrete-path, false-positive, severity, and residual-risk delegation boundaries.
- [ ] Hybrid IDK wording improves density without making delegation sections mechanical, ambiguous, or noisy.
- [ ] No behavior-changing stop rule, proof gate, safety/privacy boundary, false-positive control, routing decision, approval gate, or discipline-heavy warning is removed.
- [ ] The final diff is manually reviewed for behavior preservation, not only token reduction.

## Expected proof

- Record before/after line and rough word counts for edited `SKILL.md` delegation sections and total edited `SKILL.md` files.
- Record which delegation sections were inspected and intentionally skipped.
- Manual schema review of edited `SKILL.md` files.
- Targeted search for delegated status enums in edited files to confirm enum-bearing skills still define controller behavior.
- Targeted search for accidental repo-root runtime dependency wording.
- Targeted search for accidental shared-reference or generated-manifest wording.
- Manual public-boundary pass for private paths, credentials, client data, private notes, raw private source material, sensitive personal context, secrets, or real user data.
- Manual behavior review for edited discipline-heavy skills, especially `tdd`, `code-security-review`, `verification-before-completion`, `receiving-code-review`, `subagent-driven-development`, and architecture planning/review skills.
- Use `verification-before-completion` before claiming this issue is implemented, behavior-preserving, or ready for git review.

## Blocked by

- None - the docs-grounded decision pass selected delegation boilerplate compression as the next focused optimization slice after issue `056`.

## User stories addressed

- As a maintainer, I can reduce repeated delegation wording without weakening subagent-aware workflows.
- As an installed-skill user, I can load skills with less repeated boilerplate while still seeing how delegation should be controlled.
- As a reviewer, I can inspect a focused delegation cleanup before the broader `depends_on` sweep begins.
- As a future agent, I can continue the token optimization agenda without relying on hidden chat history.

## Implementation plan

- Plan target: `issues/057-optimize-delegation-boilerplate-token-footprint.md`.
- Plan location: this tracked issue file.
- Source inspected: `AGENT.md`, `CONTEXT.md`, `skills/README.md`, `docs/agents/project-standards.md`, this issue, and representative delegation sections from `doc-sync`, `code-security-review`, `tdd`, `subagent-driven-development`, `prd-to-issues`, and `goated-prompt`.
- Execution route: direct prose edits with subagent-supported audit and review; no TDD route because this is a docs/skill-instruction optimization, not executable behavior.
- Slice shape: one suite-wide selective prose optimization across the 30 existing delegation sections.
- Module/interface focus: not architecture-relevant; the protected interface is the installed-skill delegation contract.
- Assumptions: all implemented skills intentionally remain subagent-aware and single-agent-compatible; status enums are required only when delegated results change controller action.
- Stop conditions: pause if a section's delegation behavior is unclear, if compression would remove per-status controller action, if a discipline-heavy warning cannot be preserved compactly, if a broad shared reference becomes tempting, or if subagent review flags behavior regression.

### Steps

1. Re-read the first-read sources and current `git status --short`; keep pre-existing unrelated dirty work out of scope.
2. Run a targeted scan for all `## Delegation` sections, word counts, status enum usage, and status-handling wording across implemented `SKILL.md` files.
3. Dispatch read-only classification subagents:
   - one reviewer classifies Lane A enum-heavy and specialized sections, with risky wording to preserve;
   - one reviewer classifies Lane B lightweight sections and skip candidates.
4. Build an audit ledger with every `SKILL.md`, lane classification, risk band, intended edit/skip decision, and preservation notes.
5. Patch Lane B lightweight sections first using compact evidence/fallback wording; do not introduce status enums unless the audit finds a controller-action need.
6. Patch Lane A enum-heavy sections with the shared compact shape while keeping each skill's `Status` enum and per-status controller actions inline.
7. Patch discipline-heavy and specialized sections last, especially `tdd`, `code-security-review`, `verification-before-completion`, `receiving-code-review`, `subagent-driven-development`, and architecture planning/review skills.
8. Record before/after line and rough word counts for edited delegation sections and edited `SKILL.md` files.
9. Run targeted checks:
   - schema fields still present in edited `SKILL.md` files;
   - enum-bearing edited files still define status handling;
   - no accidental repo-root runtime dependency wording;
   - no shared delegation reference, generated manifest, hook, automation, token dashboard, or eval harness wording;
   - no public-boundary leaks.
10. Dispatch post-edit review subagents:
   - enum/discipline reviewer checks retained status contracts, controller actions, and discipline gates;
   - lightweight reviewer checks evidence/fallback clarity, self-contained wording, and no status-enum inflation.
11. Integrate reviewer concerns, rerun targeted checks, and use `verification-before-completion` before claiming the issue is behavior-preserving or ready for git review.

### Residual risk

- Moderate wording risk remains because delegation prose controls agent behavior. Mitigate with the audit ledger, risk-band patch order, independent review, and final manual behavior review.
- No hard token target is used, so the final savings may be smaller than an aggressive compression pass. That is acceptable if behavior and review clarity are preserved.

## Implementation route

- Start by reading this issue plus the recommended first reads.
- Use `writing-plans` before editing if the implementation agent needs a step-by-step patch plan after context compaction.
- Run a targeted scan for `## Delegation` sections and delegated status enum usage across implemented `SKILL.md` files.
- Group candidates by risk:
  - enum-heavy controller sections;
  - lightweight evidence-gathering sections;
  - discipline-heavy sections;
  - specialized controller workflows such as `subagent-driven-development`.
- Inspect each candidate before editing; do not apply a blind regex replacement.
- Prefer semantic compression inside `SKILL.md` over moving delegation behavior into references.
- Use focused edits with `apply_patch`; do not run broad mechanical rewrites across the suite.
- After edits, run targeted schema/text/status checks and manual behavior review.
- Use `verification-before-completion` before claiming completion.
- Let the user review the git diff before starting the broader `depends_on` sweep.

## Scope exclusions

- Do not perform the broader suite-wide `depends_on` sweep in this issue.
- Do not trim `verification-before-completion` repetition except where it appears solely as delegation boilerplate in another skill.
- Do not optimize `tdd` guardrails beyond delegation-section boilerplate in this issue.
- Do not remove or change local reference files merely to save tokens.
- Do not remove the lean schema or required frontmatter fields.
- Do not create category-level, repo-level, or cross-skill shared references.
- Do not create generated indexes, token dashboards, eval harnesses, CI checks, runtime automation, installer automation, plugin manifests, automatic skill loading, hooks, or adapter-sync tooling.
- Do not edit public README/catalog docs unless this implementation changes public behavior or documented skill inventory.
- Do not make installed skills depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local/` notes, or hidden chat history.

## Follow-up candidates

Carry these forward after this slice. The user specifically wants the broader `depends_on` sweep after the specific optimizations are handled.

- Compress `depends_on` prose across the suite from sentence form to compact condition form after focused specialist optimizations.
- Trim `verification-before-completion` repetition only where a skill repeats the same closeout gate multiple times.
- Treat TDD guardrail compression as a separate behavior-sensitive pass because the horizontal-slice warning is intentionally behavior-shaping.
- Consider a tiny before/after eval suite for representative skill outputs before applying the optimization style broadly.

## Implementation notes

- Use the IDK glossary as a precision tool, not decoration.
- Good IDK targets: short delegation labels, evidence requirements, status handling, proof notes, and controller action wording.
- Risky IDK targets: discipline-heavy warnings, safety/privacy boundaries, false-positive controls, TDD anti-rationalization gates, and nuanced tradeoff language.
- Prefer compact patterns such as `Main owns...`, `Delegate only...`, `Require...`, and `Status handling...` when they remain readable.
- Preserve status enums when they encode controller behavior; do not collapse them into vague "handle results appropriately" wording.
- A shorter delegation section is only successful if a future agent can still decide what to delegate, what evidence to require, and how to react to each result.
