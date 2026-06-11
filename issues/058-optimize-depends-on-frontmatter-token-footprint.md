## Parent PRD

No separate parent PRD. This issue continues the user-approved 2026-06-11 GOATED AI Skills token-optimization agenda from `issues/053-optimize-hotspot-skill-token-footprint.md`, `issues/054-optimize-code-security-review-token-footprint.md`, `issues/055-optimize-architecture-vocabulary-token-footprint.md`, `issues/056-optimize-reference-read-gate-token-footprint.md`, and `issues/057-optimize-delegation-boilerplate-token-footprint.md`.

## Type

AFK

## What to build

Optimize repeated `depends_on` frontmatter prose across implemented `SKILL.md` files without changing the lean schema, dependency behavior, fallback semantics, installed-skill self-containment, or skill-body instructions.

The intended change is a suite-wide selective frontmatter compression pass:

- AUDIT all 30 implemented `SKILL.md` files with `depends_on` blocks.
- PRESERVE the existing `depends_on` shape in every edited file:
  - `hard: []`
  - `soft:`
  - `fallback:`
- COMPRESS verbose `soft` dependency entries into compact condition/action routing cues.
- COMPRESS verbose `fallback` prose into compact wording while preserving skill-specific stop behavior.
- USE the body of each `SKILL.md` as evidence for whether a dependency constraint is already body-backed or is frontmatter-unique.
- EDIT frontmatter only; do not rewrite body sections in this issue.
- RECORD an edit/skip ledger for every `SKILL.md`, including body-backed versus frontmatter-unique dependency behavior.
- AVOID moving dependency behavior into repo-level, category-level, or cross-skill shared references because installed skills must remain self-contained.

The optimization target is repeated dependency-routing prose, not the dependency contract itself.

## Grill decision

After issue `057`, the next slice should be the broader `depends_on` sweep rather than trimming `verification-before-completion` repetition, compressing TDD guardrails, or building a before/after eval suite.

Rationale:

- `depends_on` remains the largest frontmatter cost at about 3,392 words across the 30 implemented skill files.
- The project standards require dependency behavior to stay explicit, but the current sentence-like wording is often more verbose than needed for routing metadata.
- Frontmatter is hot-path discovery and loading surface, so reducing repeated prose there has high value.
- This slice is safer after the focused specialist optimizations in issues `054`, `055`, `056`, and `057` because the suite now has clearer patterns for behavior-preserving compression.
- The user confirmed a suite-wide selective pass, preserving schema shape while compressing wording.

Recommended posture: apply a **preserve schema, compress routing prose** rule.

- Keep `hard`, `soft`, and `fallback` explicit in every `depends_on` block.
- Prefer compact `soft` entries shaped like `skill-name for trigger phrase` when the body already carries the detailed workflow behavior.
- Preserve behavioral verbs in `soft` entries when the dependency instruction is frontmatter-unique.
- Compress fallback wording, but keep skill-specific stop conditions such as pausing on unready PRDs, avoiding speculative findings, running phases sequentially, downgrading unsupported claims, or reporting residual risk.

## Grill refinement decisions

The implementation plan should use these settled decisions from the docs-grounded refinement session:

- Use one suite-wide selective pass across all 30 `depends_on` blocks.
- Preserve the existing YAML structure:
  - keep `hard: []`;
  - keep `soft:`;
  - keep `fallback:`.
- Treat `soft` entries as the main compression target.
- Convert verbose `soft` entries into compact condition/action routing cues.
- Use a compact fallback pattern where safe: inspect minimal evidence, state assumptions or lower confidence, narrow claims, and report residual risk when relevant.
- Preserve skill-specific fallback stop behavior instead of flattening every fallback into generic "do your best" wording.
- Keep the issue frontmatter-only:
  - use body sections as evidence for safe compression;
  - do not rewrite body sections in this slice.
- Classify each dependency block before editing:
  - **body-backed** means the body already states the sequencing rule, stop condition, proof gate, or fallback behavior clearly enough that the YAML can compress more aggressively.
  - **frontmatter-unique** means the YAML carries behavior not clearly repeated in the body, so the compressed wording must retain the behavior-driving verb or condition.
- Use an edit/skip ledger rather than requiring every block to change.
- Use subagents before edits for read-only classification and risk-flagging, then after edits for independent behavior-preservation review.
- Avoid a hard token-savings target. Require measured before/after counts and behavior-preserving reduction instead.
- Add this plan and the decisions directly to this issue so future agents do not depend on chat history.

## Audit evidence to preserve

From the full-suite audit and prior optimization issues:

- 30 implemented `SKILL.md` files total about 52k words before the first optimization slice.
- Frontmatter was about 8.6k words, or 16.6% of all `SKILL.md` words.
- `depends_on` was the largest frontmatter cost at about 3.4k words.
- Body-section hotspots included:
  - `Workflow`: about 19.3k words
  - `Guardrails`: about 6.1k words
  - `Output Contract`: about 6.0k words
  - `Delegation`: about 4.9k words before issue `057`
- Engineering was the heaviest category at about 36.8k words across 19 skills.
- The suite is structurally healthy; the main optimization is to keep `SKILL.md` as hot-path router/procedure and compress or move detail without deleting behavior-changing guidance.

Current `depends_on` scan:

- 30 implemented `SKILL.md` files include `depends_on` blocks.
- Total `depends_on` footprint is about 3,392 words.
- Highest-word `depends_on` blocks at planning time:
  - `skills/engineering/writing-plans/SKILL.md` - about 190 words
  - `skills/engineering/plan-codebase-architecture/SKILL.md` - about 174 words
  - `skills/engineering/receiving-code-review/SKILL.md` - about 162 words
  - `skills/engineering/diagnose/SKILL.md` - about 161 words
  - `skills/engineering/subagent-driven-development/SKILL.md` - about 160 words
  - `skills/engineering/prd-to-issues/SKILL.md` - about 144 words
  - `skills/engineering/improve-codebase-architecture/SKILL.md` - about 143 words
  - `skills/engineering/documentation-cleanup/SKILL.md` - about 139 words
  - `skills/engineering/tdd/SKILL.md` - about 138 words
  - `skills/engineering/doc-sync/SKILL.md` - about 132 words
  - `skills/engineering/code-security-review/SKILL.md` - about 119 words
  - `skills/productivity/goated-prompt/SKILL.md` - about 118 words
  - `skills/engineering/documentation-writer/SKILL.md` - about 116 words
  - `skills/engineering/commit-message/SKILL.md` - about 116 words
  - `skills/engineering/standards-and-spec-review/SKILL.md` - about 116 words

## Settled optimization posture

- Optimize selectively, case by case.
- Reduce always-loaded tokens while preserving the parts that change agent behavior.
- Keep the lean schema stable; do not remove `hard: []` just to save a few words.
- Keep dependency behavior explicit enough that future agents know when to route to companion skills, when to continue directly, and when to downgrade or pause.
- Treat frontmatter as routing metadata and the body as the detailed workflow source.
- Compress aggressively only when the skill body already carries the behavior that the YAML currently repeats.
- Preserve frontmatter-unique constraints compactly when the body does not carry the same behavior.
- Preserve inline stop rules, proof gates, safety/privacy boundaries, false-positive controls, routing decisions, approval gates, and discipline-heavy reminders when they appear only in `depends_on`.
- Avoid repo-level shared references unless the installed-skill distribution model changes.
- Use `goated-prompt` and the IDK glossary as style inspiration for information-dense wording, not as a total voice transplant.
- Use uppercase IDK action keywords sparingly in frontmatter. Prefer readable compact routing cues over mechanical phrasing.

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
- `issues/057-optimize-delegation-boilerplate-token-footprint.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/goated-prompt/references/idk-glossary.md`
- Candidate `SKILL.md` files from the `depends_on` scan, opened only as needed.
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `AGENT.md` - maintainer contract, public boundary, self-contained installed skills, soft 300-line cap, and dependency behavior expectations.
- `CONTEXT.md` - definitions for `SKILL.md`, dependency, installed skill, self-contained skill, discipline-heavy skill, and source-repo/installed-skill/target-project boundaries.
- `skills/README.md` - lean schema, dependency behavior requirement, progressive disclosure contract, and installed-skill self-containment rule.
- `docs/agents/project-standards.md` - documented standard that implemented skills use structured `depends_on` with `hard`, `soft`, and `fallback`.
- `issues/053-optimize-hotspot-skill-token-footprint.md` - first token optimization wave and settled posture.
- `issues/054-optimize-code-security-review-token-footprint.md` - discipline-heavy specialist extraction pattern.
- `issues/055-optimize-architecture-vocabulary-token-footprint.md` - focused family optimization pattern.
- `issues/056-optimize-reference-read-gate-token-footprint.md` - reference gate compression and follow-up context.
- `issues/057-optimize-delegation-boilerplate-token-footprint.md` - prior suite-wide selective compression pattern and verification style.

## Acceptance criteria

- [ ] All edited `SKILL.md` files still follow the lean schema.
- [ ] Every edited skill keeps `depends_on`, `hard`, `soft`, and `fallback` fields.
- [ ] Every edited skill remains self-contained after installation and depends only on its own folder plus target-project evidence at runtime.
- [ ] No repo-level, category-level, or cross-skill shared dependency reference is introduced.
- [ ] No runtime bootstrap, automatic loading, generated manifest, installer, hook, adapter automation, eval harness, CI check, or token dashboard is introduced.
- [ ] No installed Codex skill copies outside this source repo are edited.
- [ ] The implementation audits all 30 implemented `SKILL.md` `depends_on` blocks and records which files were edited or intentionally skipped.
- [ ] The edit/skip ledger records whether important dependency behavior is body-backed or frontmatter-unique for each skill.
- [ ] Body-backed `soft` entries are compressed into compact routing cues without duplicating body instructions.
- [ ] Frontmatter-unique `soft` entries preserve the behavioral verb, proof gate, stop condition, or routing condition that makes the dependency meaningful.
- [ ] `hard: []` remains explicit for skills with no hard dependency.
- [ ] `soft` dependency names remain valid implemented skill names or clearly intentional external/project evidence references when present.
- [ ] Fallback prose is compressed without becoming vague, generic, or actionless.
- [ ] Skill-specific fallback stop behavior remains clear, including pausing, narrowing scope, downgrading unsupported claims, avoiding speculative findings, or reporting residual risk where applicable.
- [ ] Discipline-heavy skills preserve dependency reminders that prevent shortcutting, overclaiming, skipped verification, false-positive reporting, unsafe edits, or ungrounded planning.
- [ ] `prd-to-issues` preserves its pause-on-unready-PRD fallback behavior.
- [ ] `code-security-review` preserves lower-confidence and residual-risk behavior instead of speculative findings.
- [ ] `subagent-driven-development` preserves sequential fallback behavior when subagents or review tools are unavailable.
- [ ] `verification-before-completion` preserves downgrade-unsupported-claims and residual-risk fallback behavior.
- [ ] `tdd` preserves behavior/regression/public-interface proof routing.
- [ ] Architecture skills preserve source-grounded planning/review dependency cues without overloading frontmatter.
- [ ] No behavior-changing stop rule, proof gate, safety/privacy boundary, false-positive control, routing decision, approval gate, or discipline-heavy warning is removed from the skill as a whole.
- [ ] The final diff is manually reviewed for dependency-behavior preservation, not only token reduction.

## Expected proof

- Record before/after rough word counts for all `depends_on` blocks and total edited `SKILL.md` files.
- Record the edit/skip ledger for all 30 `SKILL.md` files, including:
  - edited or skipped;
  - body-backed or frontmatter-unique;
  - preservation notes for dependency behavior and fallback behavior.
- Manual schema review of edited `SKILL.md` files.
- Targeted search to confirm every edited file still has `depends_on`, `hard`, `soft`, and `fallback`.
- Targeted search or scripted check to confirm `soft` dependency names still map to implemented skill names where applicable.
- Targeted review to confirm no fallback became vague "do your best" wording.
- Targeted search for accidental repo-root runtime dependency wording.
- Targeted search for accidental shared-reference, generated-manifest, hook, automation, token dashboard, or eval-harness wording.
- Manual public-boundary pass for private paths, credentials, client data, private notes, raw private source material, sensitive personal context, secrets, or real user data.
- Manual behavior review for edited discipline-heavy and routing-sensitive skills, especially `tdd`, `code-security-review`, `verification-before-completion`, `receiving-code-review`, `subagent-driven-development`, `prd-to-issues`, `writing-plans`, and architecture planning/review skills.
- Use `verification-before-completion` before claiming this issue is implemented, behavior-preserving, or ready for git review.

## Implementation evidence

Issue `058` implementation edited all 30 implemented `SKILL.md` `depends_on` blocks and skipped none. The pass was frontmatter-only.

Measured from `HEAD` to the working tree after implementation:

- `depends_on` words: 3,392 -> 2,740, a reduction of 652 words, or 19.22%.
- Edited `SKILL.md` words: 48,511 -> 47,859, a reduction of 652 words, or 1.34%.
- Diff stat for `skills/`: 30 files changed, 179 insertions, 179 deletions.

### Edit/skip ledger

| File | Decision | Classification | `depends_on` words | Preservation notes |
| --- | --- | --- | --- | --- |
| `skills/agent-workflows/agent-instructions-integrator/SKILL.md` | Edited | body-backed | 94 -> 72 | Installed-router, prompt, artifact-routing, verified-adapter fallback. |
| `skills/agent-workflows/context-matrix-map/SKILL.md` | Edited | body-backed | 69 -> 48 | Map-first routes, after-map calibration, evidence-backed claim gate. |
| `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` | Edited | mixed | 82 -> 62 | Public/cross-workflow grill gate, adapter route, handoff, assumptions, residual risk. |
| `skills/agent-workflows/handoff/SKILL.md` | Edited | mixed | 72 -> 59 | Re-orientation, affected context/standards routes, verification, gaps, lower confidence. |
| `skills/agent-workflows/project-context-calibration/SKILL.md` | Edited | body-backed | 98 -> 75 | Discovery, user-decision grill route, standards split, adapter route, lower-confidence CONTEXT gaps. |
| `skills/agent-workflows/project-standards-calibration/SKILL.md` | Edited | body-backed | 67 -> 48 | Orientation, matrix/context routes, verification, lower-confidence fallback. |
| `skills/agent-workflows/session-start-progressive-disclosure/SKILL.md` | Edited | body-backed | 53 -> 49 | Context map, root CONTEXT, standards routing, minimal-file fallback. |
| `skills/agent-workflows/using-goated-ai-skills/SKILL.md` | Edited | body-backed | 95 -> 76 | Serious-work orientation, docs-grounded grill, skill/adaptor/prompt routes, direct classification fallback. |
| `skills/engineering/architecture-design-map/SKILL.md` | Edited | frontmatter-unique/mixed | 103 -> 81 | Setup/context/standards routing, conflict/scope grill, durable-map doc-sync, lower-confidence fallback. |
| `skills/engineering/code-security-review/SKILL.md` | Edited | mixed/frontmatter-sensitive | 119 -> 90 | Spec/TDD/security-standards routes, verification gate, residual-risk fallback, no speculative findings. |
| `skills/engineering/commit-message/SKILL.md` | Edited | frontmatter-unique/mixed | 116 -> 92 | Standards/security/doc-sync pre-routes, verification before claimful commit wording, handoff, no invented intent/checks. |
| `skills/engineering/diagnose/SKILL.md` | Edited | mixed | 161 -> 130 | Expected-vs-reported grill, TDD vs architecture routing, security/doc/handoff routes, safe feedback loop, downgraded claims. |
| `skills/engineering/doc-sync/SKILL.md` | Edited | mixed | 132 -> 99 | Context/standards updates, standards/security pre-routes, verification, handoff, unverifiable drift-risk fallback. |
| `skills/engineering/documentation-cleanup/SKILL.md` | Edited | mixed | 139 -> 107 | Context/standards refresh, adapter repair, writer vs doc-sync split, verification, no destructive cleanup claims. |
| `skills/engineering/documentation-writer/SKILL.md` | Edited | mixed | 116 -> 92 | Unclear-audience grill, unsettled-requirements PRD route, doc-sync drift route, verification, narrower-doc fallback. |
| `skills/engineering/grill-with-docs/SKILL.md` | Edited | body-backed | 88 -> 72 | Orientation, source discovery, durable context/standards capture, doc-sync, verification, inspect-before-asking fallback. |
| `skills/engineering/improve-codebase-architecture/SKILL.md` | Edited | mixed | 143 -> 123 | Context/standards, current-state map, unclear-goal grill, TDD/PRD/issues routes, facts-vs-assumptions fallback. |
| `skills/engineering/plan-codebase-architecture/SKILL.md` | Edited | mixed | 174 -> 144 | Clarified-brief gate, PRD/context/standards/map/refactor routing, TDD/issues routes, blueprint facts-vs-assumptions fallback. |
| `skills/engineering/prd-to-issues/SKILL.md` | Edited | mixed | 144 -> 115 | PRD readiness, approval tradeoff grill, prototype/context/standards routes, verification, pause-on-unready-PRD fallback. |
| `skills/engineering/prototype/SKILL.md` | Edited | mixed | 101 -> 86 | Docs-sensitive grill, PRD/issues/TDD absorption routes, verification, assumptions, disposable fallback. |
| `skills/engineering/receiving-code-review/SKILL.md` | Edited | mixed | 162 -> 137 | Unclear-feedback grill, plan/TDD/spec/security/delegation/doc routes, verification, safe accepted items, downgraded claims. |
| `skills/engineering/standards-and-spec-review/SKILL.md` | Edited | mixed | 116 -> 92 | Standards calibration, TDD evidence, security/doc-sync routes, verification, assumptions-vs-findings fallback. |
| `skills/engineering/subagent-driven-development/SKILL.md` | Edited | mixed | 160 -> 138 | Plan/grill/prototype/architecture/TDD/review/security/doc routes, sequential fallback, unsupported claims avoided. |
| `skills/engineering/tdd/SKILL.md` | Edited | frontmatter-unique/mixed | 138 -> 112 | Behavior/interface/scope grill, vertical issue/prototype/standards routes, post-implementation reviews, proof fallback, residual risk. |
| `skills/engineering/verification-before-completion/SKILL.md` | Edited | body-backed | 108 -> 94 | Missing-proof routes, issue/security/doc/handoff routing, unverified facts, downgraded claims, residual risk. |
| `skills/engineering/write-a-prd/SKILL.md` | Edited | body-backed | 94 -> 72 | Orientation, docs-grounded grill, context/standards routes, issue-ready verification, unverifiable PRD assumptions. |
| `skills/engineering/writing-plans/SKILL.md` | Edited | mixed | 190 -> 159 | Issue/prototype/architecture/TDD/delegation/review/security/doc routes, narrow-plan/no-unverifiable-claims fallback. |
| `skills/productivity/caveman/SKILL.md` | Edited | mixed/non-skill constraints | 60 -> 55 | Output-contract and normal-clarity exceptions, persistence fallback. |
| `skills/productivity/goated-prompt/SKILL.md` | Edited | mixed | 118 -> 97 | GOATED router, lightweight vs docs-grounded grill split, PRD/plan/skill routes, assumptions, no undiscovered facts. |
| `skills/productivity/grill-me/SKILL.md` | Edited | body-backed | 80 -> 64 | Docs-grounded escalation, PRD/prototype/plan routes, unsourced-assumption labeling. |

## Blocked by

- None - the docs-grounded decision pass selected a suite-wide selective `depends_on` frontmatter compression pass and resolved the main scope decisions.

## User stories addressed

- As a maintainer, I can reduce repeated dependency-routing prose without weakening dependency behavior.
- As an installed-skill user, I can load skills with less frontmatter bloat while still seeing when companion skills matter.
- As a reviewer, I can inspect a focused frontmatter-only cleanup with a clear edit/skip ledger.
- As a future agent, I can continue the token optimization agenda without relying on hidden chat history.

## Implementation plan

- Plan target: `issues/058-optimize-depends-on-frontmatter-token-footprint.md`.
- Plan location: this tracked issue file.
- Source inspected before writing this issue: `AGENT.md`, `CONTEXT.md`, `skills/README.md`, `docs/agents/project-standards.md`, `issues/057-optimize-delegation-boilerplate-token-footprint.md`, the installed `grill-with-docs` workflow, the installed `prd-to-issues` workflow, and a fresh `depends_on` heading/count scan across implemented `SKILL.md` files.
- Execution route: direct frontmatter prose edits with subagent-supported audit and review; no TDD route because this is a docs/skill-instruction optimization, not executable behavior.
- Slice shape: one suite-wide selective frontmatter optimization across the 30 existing `depends_on` blocks.
- Module/interface focus: not architecture-relevant; the protected interface is the installed-skill dependency contract.
- Assumptions: all implemented skills intentionally use structured `depends_on` frontmatter; detailed workflow behavior belongs in the skill body; `depends_on` should route and qualify companion-skill use without duplicating full procedures.
- Stop conditions: pause if a dependency behavior cannot be classified as body-backed or frontmatter-unique, if compression would remove a unique stop condition or proof gate, if fallback wording becomes vague, if a shared reference becomes tempting, or if post-edit review flags behavior regression.

### Steps

1. Re-read the first-read sources and current `git status --short`; keep pre-existing unrelated dirty work out of scope.
2. Run a targeted scan for all 30 implemented `SKILL.md` files, current `depends_on` word counts, `soft` entries, fallback strings, and dependency names.
3. Dispatch read-only classification subagents:
   - one reviewer classifies high-risk dependency blocks and frontmatter-unique behavior to preserve;
   - one reviewer classifies body-backed dependency blocks and likely aggressive-compression candidates.
4. Build an audit ledger with every `SKILL.md`, current `depends_on` word count, body-backed/frontmatter-unique classification, intended edit/skip decision, and preservation notes.
5. Patch low-risk body-backed `soft` entries first using compact condition/action routing cues.
6. Patch fallback wording where the fallback is repetitive, while preserving skill-specific stop behavior.
7. Patch high-risk and frontmatter-unique entries last, keeping the behavior-driving verb or condition explicit.
8. Leave any block unchanged when the existing wording already earns its length or compression would make routing less clear.
9. Record before/after word counts for edited `depends_on` blocks and total edited `SKILL.md` files.
10. Run targeted checks:
    - schema fields still present in edited `SKILL.md` files;
    - `depends_on`, `hard`, `soft`, and `fallback` still present;
    - `soft` dependency names still valid;
    - fallbacks are still actionable and not vague;
    - no accidental repo-root runtime dependency wording;
    - no shared dependency reference, generated manifest, hook, automation, token dashboard, or eval harness wording;
    - no public-boundary leaks.
11. Dispatch post-edit review subagents:
    - behavior reviewer checks retained dependency routing, frontmatter-unique constraints, proof gates, stop conditions, and fallback semantics;
    - schema/lightweight reviewer checks valid names, concise fallback clarity, self-contained wording, and no shared-reference drift.
12. Integrate reviewer concerns, rerun targeted checks, and use `verification-before-completion` before claiming the issue is behavior-preserving or ready for git review.

### Residual risk

- Moderate wording risk remains because frontmatter influences skill routing before the body is read. Mitigate with body-backed/frontmatter-unique classification, the edit/skip ledger, independent review, and final manual behavior review.
- No hard token target is used, so the final savings may be smaller than an aggressive compression pass. That is acceptable if dependency behavior and review clarity are preserved.

## Implementation route

- Start by reading this issue plus the recommended first reads.
- Use `writing-plans` before editing if the implementation agent needs a step-by-step patch plan after context compaction.
- Run a targeted scan for `depends_on` blocks and dependency names across implemented `SKILL.md` files.
- Inspect each candidate before editing; do not apply a blind regex replacement.
- Prefer semantic compression inside frontmatter over moving dependency behavior into references.
- Use focused edits with `apply_patch`; do not run broad mechanical rewrites across the suite.
- After edits, run targeted schema/text/name/fallback checks and manual behavior review.
- Use `verification-before-completion` before claiming completion.
- Let the user review the git diff before starting the next optimization slice.

## Scope exclusions

- Do not edit body sections in this issue except to fix an accidental frontmatter edit if one occurs.
- Do not remove `hard: []`, `soft:`, or `fallback`.
- Do not change skill descriptions, triggers, outputs, adapters, workflow steps, delegation sections, guardrails, or references.
- Do not trim `verification-before-completion` repetition except where it appears solely in `depends_on` frontmatter.
- Do not optimize TDD guardrails in this issue.
- Do not remove or change local reference files merely to save tokens.
- Do not remove the lean schema or required frontmatter fields.
- Do not create category-level, repo-level, or cross-skill shared references.
- Do not create generated indexes, token dashboards, eval harnesses, CI checks, runtime automation, installer automation, plugin manifests, automatic skill loading, hooks, or adapter-sync tooling.
- Do not edit public README/catalog docs unless this implementation changes public behavior or documented skill inventory.
- Do not make installed skills depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local/` notes, or hidden chat history.

## Follow-up candidates

Carry these forward after this slice.

- Trim `verification-before-completion` repetition only where a skill repeats the same closeout gate multiple times.
- Treat TDD guardrail compression as a separate behavior-sensitive pass because the horizontal-slice warning is intentionally behavior-shaping.
- Consider a tiny before/after eval suite for representative skill outputs before applying the optimization style broadly.

## Implementation notes

- Treat `depends_on` as routing metadata, not a second copy of the workflow.
- Prefer compact patterns such as:
  - `grill-with-docs for ambiguous scope, success criteria, or tradeoffs`
  - `tdd when behavior, public interface, or regression proof changes`
  - `doc-sync after behavior, docs, schema, or workflow contract changes`
- Body-backed entries can compress harder because the body still carries the detailed instruction.
- Frontmatter-unique entries should keep the verb that tells the agent what to do, such as pause, verify, inspect, downgrade, avoid, run sequentially, or report residual risk.
- A shorter `depends_on` block is only successful if a future agent can still decide which companion skill to load, when to continue directly, and how to behave when companion skills or evidence are unavailable.
