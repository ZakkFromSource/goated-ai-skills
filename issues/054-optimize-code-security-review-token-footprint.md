## Parent PRD

No separate parent PRD. This issue continues the user-approved 2026-06-11 GOATED AI Skills token-optimization agenda from `issues/053-optimize-hotspot-skill-token-footprint.md`.

## Type

AFK

## What to build

Optimize `skills/engineering/code-security-review/SKILL.md` without reducing the behavior that makes it a high-confidence, false-positive-resistant security review gate.

The intended change is selective extraction and light semantic compression:

- EXTRACT long inline enumerations for entry points, trust boundaries, sensitive assets, dangerous sinks, high-risk classes, and severity examples into `skills/engineering/code-security-review/references/security-review-checklist.md`.
- PRESERVE inline the core discipline: trace concrete exploitability paths, avoid speculative findings, use the confidence gate, apply false-positive control, classify severity conservatively, and state residual risk.
- KEEP `SKILL.md` as the hot-path operating procedure and the local reference as the deeper checklist for review coverage.
- ADD only a local reference under the affected skill folder. Do not create repo-level, category-level, or cross-skill shared references.
- APPLY hybrid IDK-informed wording only where it improves clarity; do not turn nuanced security guardrails into noisy keyword prose.

## Grill decision

After reviewing the follow-up candidates from issue `053`, the next slice is `code-security-review` checklist extraction rather than the broader `depends_on` sweep.

Rationale:

- `code-security-review` is still a hotspot at roughly 196 lines / 2,386 words.
- Its biggest optimization opportunity is concentrated in dense inline security enumerations around evidence-path building, risk classes, and severity examples.
- It is a discipline-heavy skill, so a focused diff is safer than broad suite-wide frontmatter or delegation edits.
- This slice continues the proven issue `053` pattern: move reusable detail behind a local read gate while preserving behavior-changing stop rules inline.

User preference to carry forward: the broader `depends_on` sweep should still happen, but after the specific optimization slices are handled.

## Audit evidence to preserve

From the full-suite audit and issue `053`:

- 30 `SKILL.md` files total about 52k words before the first optimization slice.
- Frontmatter was about 8.6k words, or 16.6% of all `SKILL.md` words.
- `depends_on` was the largest frontmatter cost at about 3.4k words.
- Body-section hotspots included:
  - `Workflow`: about 19.3k words
  - `Guardrails`: about 6.1k words
  - `Output Contract`: about 6.0k words
  - `Delegation`: about 4.9k words
- Engineering was the heaviest category at about 36.8k words across 19 skills.
- The suite is structurally healthy; the main optimization is to keep `SKILL.md` as hot-path router/procedure and move write-time templates, checklists, examples, and rare deep-dive material into directly linked local `references/`.

Issue `053` successfully applied this pattern to four hotspot skills by moving heavy templates into local refs while preserving inline proof gates and stop rules. This issue applies the same philosophy to the security review skill, with extra caution because security review quality depends on concrete exploitability discipline.

## Settled optimization posture

- Optimize selectively, case by case.
- Reduce always-loaded tokens while preserving the parts that change agent behavior.
- Move or compress late-stage templates, long checklists, repeated boilerplate, duplicate reference pointers, and verbose dependency prose.
- Preserve inline stop rules, proof gates, safety/privacy boundaries, false-positive controls, routing decisions, approval gates, and discipline-heavy reminders.
- Add local `references/` only inside each affected skill folder.
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
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/goated-prompt/references/idk-glossary.md`
- `skills/engineering/code-security-review/SKILL.md`
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `AGENT.md` - maintainer contract, public boundary, self-contained installed skills, soft 300-line cap, and support-file guidance.
- `CONTEXT.md` - definitions for `SKILL.md`, support files, references, discipline-heavy skills, delegated status enums, and source-repo/installed-skill/target-project boundaries.
- `skills/README.md` - lean schema, progressive disclosure contract, support-file linking rules, and delegation contract.
- `issues/053-optimize-hotspot-skill-token-footprint.md` - prior optimization issue, settled posture, implementation notes, and follow-up candidates.
- `skills/engineering/code-security-review/SKILL.md` - target skill; currently embeds security review checklists and severity examples inline.
- `skills/productivity/goated-prompt/references/idk-glossary.md` - use only where action/detail keywords reduce ambiguity.

## Acceptance criteria

- [ ] `skills/engineering/code-security-review/SKILL.md` still follows the lean schema.
- [ ] The edited skill remains self-contained after installation and depends only on its own folder plus target-project evidence at runtime.
- [ ] A new local reference exists at `skills/engineering/code-security-review/references/security-review-checklist.md`.
- [ ] The new reference is directly linked from `SKILL.md` with a clear read condition.
- [ ] Long inline enumerations for entry points, trust boundaries, sensitive assets, dangerous sinks, high-risk classes, and severity examples move into the local checklist reference where useful.
- [ ] The core workflow remains inline: confirm scope, build an evidence path before judging, validate context and false positives, classify severity, report residual risk, and route next work.
- [ ] The concrete-path requirement remains inline: no finding without reachable trigger, trust boundary, missing or broken guard, affected asset, and impact.
- [ ] The confidence gate remains inline: report only strong static evidence, roughly 80% confidence or higher, and downgrade speculative concerns to residual risk.
- [ ] False-positive controls remain inline: cross-check framework defaults, middleware, validation, ownership checks, policies, transactions, tests, and deployment config before reporting.
- [ ] The "not a full audit" boundary remains inline in Purpose, Output Contract coverage note, and Guardrails.
- [ ] Security report shape still includes review scope, trust-boundary map, findings or no-findings statement, assumptions/residual risk, and next step.
- [ ] Optional external references remain optional lookup aids, not runtime dependencies.
- [ ] Hybrid IDK wording improves clarity without making security guardrails mechanical or noisy.
- [ ] No required frontmatter fields are removed.
- [ ] No repo-level shared reference library is introduced.
- [ ] No runtime bootstrap, automatic loading, generated manifest, installer, hook, adapter automation, eval harness, CI check, or token dashboard is introduced.
- [ ] No installed Codex skill copies outside this source repo are edited.
- [ ] The final diff is manually reviewed for behavior preservation, not only token reduction.

## Expected proof

- Record before/after line and rough word counts for `skills/engineering/code-security-review/SKILL.md`.
- Manual schema review of the edited `SKILL.md`.
- Manual check that `references/security-review-checklist.md` resolves from `SKILL.md` and has a clear read condition.
- Targeted search for stale `This skill is self-contained after installation` wording that no longer matches the local-reference setup.
- Targeted search for accidental repo-root runtime dependency wording.
- Manual public-boundary pass for private paths, credentials, client data, private notes, raw private source material, sensitive personal context, secrets, or real user data.
- Manual behavior review for:
  - scope confirmation and fixed-point handling;
  - concrete entry point -> trust boundary -> asset/sink tracing;
  - high-risk class coverage;
  - severity classification;
  - false-positive control;
  - no-findings output;
  - assumptions and residual risk;
  - not-full-audit boundary;
  - delegation status handling;
  - optional external reference behavior.
- Use `verification-before-completion` before claiming this issue is implemented, behavior-preserving, or ready for git review.

## Blocked by

- None - the user approved `code-security-review` as the next focused optimization slice after reviewing issue `053` follow-up candidates.

## User stories addressed

- As a maintainer, I can reduce always-loaded token cost in a discipline-heavy security skill without weakening exploitability discipline or false-positive control.
- As an installed-skill user, I can load `code-security-review` faster while still having a detailed security checklist available when the review needs coverage guidance.
- As a reviewer, I can inspect a focused specialist diff before broader suite-wide compression begins.
- As a future agent, I can continue the token optimization agenda without relying on hidden chat history.

## Implementation route

- Start by reading this issue plus the recommended first reads.
- Use `writing-plans` before editing if the implementation agent needs a step-by-step patch plan after context compaction.
- Prefer local checklist extraction first, then light semantic compression inside `SKILL.md`.
- Keep the security review's behavior-critical discipline inline even if some words could be saved by moving it.
- Use focused edits with `apply_patch`; do not run broad mechanical rewrites across the suite.
- After edits, run targeted link/schema/text checks and manual behavior review.
- Use `verification-before-completion` before claiming completion.
- Let the user review the git diff before starting broader follow-up waves.

## Scope exclusions

- Do not perform the broader suite-wide `depends_on` sweep in this issue.
- Do not shorten suite-wide delegation boilerplate in this issue.
- Do not deduplicate architecture vocabulary in this issue.
- Do not optimize `tdd` guardrails in this issue.
- Do not trim `verification-before-completion` repetition in this issue.
- Do not add a before/after eval suite in this issue.
- Do not remove the lean schema or required frontmatter fields.
- Do not create category-level, repo-level, or cross-skill shared references.
- Do not create generated indexes, token dashboards, eval harnesses, CI checks, runtime automation, installer automation, plugin manifests, automatic skill loading, hooks, or adapter-sync tooling.
- Do not edit public README/catalog docs unless this implementation changes public behavior or documented skill inventory.
- Do not make installed skills depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local/` notes, or hidden chat history.

## Follow-up candidates

Carry these forward after this slice. The user specifically wants the broader `depends_on` sweep after the specific optimizations are handled.

- Compress `depends_on` prose across the suite from sentence form to compact condition form after focused specialist optimizations.
- Shorten repeated delegation boilerplate while preserving status enums and controller behavior where needed.
- Deduplicate architecture vocabulary across `architecture-design-map`, `plan-codebase-architecture`, and `improve-codebase-architecture`.
- Tighten duplicate reference mentions where a reference appears in both `Workflow` and `References`.
- Trim `verification-before-completion` repetition only where a skill repeats the same closeout gate multiple times.
- Treat TDD guardrail compression as a separate behavior-sensitive pass because the horizontal-slice warning is intentionally behavior-shaping.
- Consider a tiny before/after eval suite for representative skill outputs before applying the optimization style broadly.

## Implementation notes

- Use the IDK glossary as a precision tool, not decoration.
- Good IDK targets: checklist headings, compact workflow commands, output contract templates, and acceptance criteria.
- Risky IDK targets: exploitability discipline, false-positive controls, safety/privacy boundaries, and nuanced residual-risk language.
- Favor verbs such as EXTRACT, REFINE, PRESERVE, VALIDATE, MIRROR, DOCUMENT, and ANALYZE only where they reduce ambiguity.
- Preserve one explicit closeout gate when the skill can lead to clean, complete, reviewed, or ready claims.
- Keep optional CWE/OWASP references as optional lookup aids; do not make web access part of the installed skill's normal runtime path.
