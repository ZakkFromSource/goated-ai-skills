## Parent PRD

No separate parent PRD. This issue continues the user-approved 2026-06-11 GOATED AI Skills token-optimization agenda from `issues/053-optimize-hotspot-skill-token-footprint.md` and `issues/054-optimize-code-security-review-token-footprint.md`.

## Type

AFK

## What to build

Optimize the architecture-skill vocabulary footprint across:

- `skills/engineering/architecture-design-map/SKILL.md`
- `skills/engineering/plan-codebase-architecture/SKILL.md`
- `skills/engineering/improve-codebase-architecture/SKILL.md`

The intended change is selective vocabulary extraction and semantic compression:

- REFINE each `Architecture Language` section so `SKILL.md` keeps only the role-critical terms needed for hot-path behavior.
- MOVE fuller definitions, examples, and nuance into the skill's own existing local reference where useful:
  - `architecture-design-map/references/diagram-patterns.md`
  - `plan-codebase-architecture/references/architecture-blueprint-patterns.md`
  - `improve-codebase-architecture/references/deepening-interface-patterns.md`
- PRESERVE the behavior-changing distinctions that prevent wrong routing:
  - `architecture-design-map` describes existing architecture and does not plan or rank improvements.
  - `plan-codebase-architecture` writes source-grounded blueprints before implementation and guards against speculative seams or overdesign.
  - `improve-codebase-architecture` reviews existing code for ranked improvement opportunities and guards against speculative refactor recommendations.
- KEEP every installed skill self-contained after copying. Do not create a repo-level or cross-skill shared architecture glossary.
- APPLY hybrid IDK-informed wording only where it makes the architecture language denser and clearer.

## Grill decision

After reviewing the follow-up candidates carried forward from issue `054`, the next slice is architecture vocabulary dedupe rather than delegation boilerplate, verification repetition, TDD guardrail compression, the broad `depends_on` sweep, or an eval suite.

Rationale:

- It is a specific optimization slice across a related skill family, matching the user's preference to handle focused optimizations before the broader `depends_on` sweep.
- The three architecture skills all carry overlapping inline vocabulary for module, interface, seam, adapter, deep module, shallow module, leverage, locality, and test surface concepts.
- Each skill already has a local reference file, so the implementation can use the issue `053` and `054` pattern without adding shared runtime dependencies.
- The risk is manageable if the hot path preserves only the terms that control routing, output quality, and anti-overdesign behavior.

User preference to carry forward: the broader `depends_on` sweep should still happen, but after the focused specialist optimizations are handled.

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
- The suite is structurally healthy; the main optimization is to keep `SKILL.md` as hot-path router/procedure and move write-time templates, checklists, examples, and rare deep-dive material into directly linked local `references/`.

Prior slices proved the pattern:

- Issue `053` moved large output templates from four hotspot skills into local references.
- Issue `054` moved security review coverage examples into a local checklist while preserving concrete-path, confidence, false-positive, severity, residual-risk, and not-full-audit gates inline.

Current target measurements from the docs-grounded decision pass:

- `architecture-design-map/SKILL.md`: about 213 lines / 1,986 words.
- `plan-codebase-architecture/SKILL.md`: about 203 lines / 1,898 words.
- `improve-codebase-architecture/SKILL.md`: about 195 lines / 1,944 words.
- Existing local references:
  - `diagram-patterns.md`: about 168 lines / 760 words.
  - `architecture-blueprint-patterns.md`: about 127 lines / 956 words.
  - `deepening-interface-patterns.md`: about 117 lines / 1,075 words.

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
- `issues/054-optimize-code-security-review-token-footprint.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/goated-prompt/references/idk-glossary.md`
- `skills/engineering/architecture-design-map/SKILL.md`
- `skills/engineering/architecture-design-map/references/diagram-patterns.md`
- `skills/engineering/plan-codebase-architecture/SKILL.md`
- `skills/engineering/plan-codebase-architecture/references/architecture-blueprint-patterns.md`
- `skills/engineering/improve-codebase-architecture/SKILL.md`
- `skills/engineering/improve-codebase-architecture/references/deepening-interface-patterns.md`
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `AGENT.md` - maintainer contract, public boundary, self-contained installed skills, soft 300-line cap, and support-file guidance.
- `CONTEXT.md` - definitions for `SKILL.md`, support files, references, discipline-heavy skills, delegated status enums, architecture design language, and source-repo/installed-skill/target-project boundaries.
- `skills/README.md` - lean schema, progressive disclosure contract, support-file linking rules, and delegation contract.
- `issues/053-optimize-hotspot-skill-token-footprint.md` - first successful local-reference extraction wave.
- `issues/054-optimize-code-security-review-token-footprint.md` - focused specialist extraction pattern and follow-up candidates.
- `skills/engineering/architecture-design-map/SKILL.md` - descriptive architecture map workflow with inline architecture vocabulary.
- `skills/engineering/plan-codebase-architecture/SKILL.md` - source-grounded architecture blueprint workflow with inline architecture vocabulary.
- `skills/engineering/improve-codebase-architecture/SKILL.md` - architecture improvement review workflow with inline architecture vocabulary.

## Acceptance criteria

- [ ] All three edited `SKILL.md` files still follow the lean schema.
- [ ] Each edited skill remains self-contained after installation and depends only on its own folder plus target-project evidence at runtime.
- [ ] No repo-level, category-level, or cross-skill shared architecture glossary is introduced.
- [ ] Existing local references are reused or expanded where useful instead of adding unnecessary support files.
- [ ] Every moved or expanded reference detail is directly linked from the relevant `SKILL.md` with a clear read condition.
- [ ] `Architecture Language` sections are compressed to the smallest useful hot-path vocabulary for each skill.
- [ ] Common architecture definitions no longer repeat in full sentence form across all three `SKILL.md` files.
- [ ] `architecture-design-map` still preserves inline the map-only boundary: describe existing architecture, do not plan new architecture, rank improvements, or produce refactor proposals.
- [ ] `architecture-design-map` still preserves source-evidence, uncertainty, Mermaid-first mapping, quick zoom-out, and durable artifact behavior.
- [ ] `plan-codebase-architecture` still preserves inline the clarified-intent gate, design-only boundary, deep-module bias, real-seam rule, anti-overdesign checks, public test surface planning, and downstream routing.
- [ ] `improve-codebase-architecture` still preserves inline the review-only boundary, evidence-before-judgment rule, deletion test, false-seam control, ranked opportunity discipline, test-surface discipline, and no-implementation boundary.
- [ ] Architecture terms remain readable. Hybrid IDK wording should improve clarity without making the prose mechanical.
- [ ] No required frontmatter fields are removed.
- [ ] No runtime bootstrap, automatic loading, generated manifest, installer, hook, adapter automation, eval harness, CI check, or token dashboard is introduced.
- [ ] No installed Codex skill copies outside this source repo are edited.
- [ ] The final diff is manually reviewed for behavior preservation, not only token reduction.

## Expected proof

- Record before/after line and rough word counts for the three edited `SKILL.md` files.
- Record any word-count changes in touched local references.
- Manual schema review of all three edited `SKILL.md` files.
- Manual check that every reference link resolves from its `SKILL.md` and has a clear read condition.
- Targeted search for stale reference wording, duplicate full vocabulary definitions, and accidental repo-root runtime dependency wording.
- Manual public-boundary pass for private paths, credentials, client data, private notes, raw private source material, sensitive personal context, secrets, or real user data.
- Manual behavior review for:
  - `architecture-design-map`: descriptive map boundary, source evidence, uncertainty notes, quick zoom-out behavior, Mermaid-first output, and no planning or improvement leakage.
  - `plan-codebase-architecture`: clarified-intent gate, design-only scope, deep-module and real-seam discipline, anti-overdesign controls, test-surface planning, and downstream routing.
  - `improve-codebase-architecture`: review-only scope, evidence-before-judgment, deletion test, false-seam checks, ranked opportunities, replace-don't-layer testing discipline, and no implementation leakage.
- Use `verification-before-completion` before claiming this issue is implemented, behavior-preserving, or ready for git review.

## Blocked by

- None - the docs-grounded decision pass selected this as the next focused optimization slice after issue `054`.

## User stories addressed

- As a maintainer, I can reduce repeated architecture vocabulary in always-loaded skill bodies without weakening the architecture skills' distinct behaviors.
- As an installed-skill user, I can load architecture workflows with less duplicated terminology while still having local references for deeper definitions and examples.
- As a reviewer, I can inspect a focused three-skill diff before broader suite-wide compression begins.
- As a future agent, I can continue the token optimization agenda without relying on hidden chat history.

## Implementation route

- Start by reading this issue plus the recommended first reads.
- Use `writing-plans` before editing if the implementation agent needs a step-by-step patch plan after context compaction.
- Prefer refining the existing local references before adding new support files.
- Keep each `SKILL.md` as the hot-path operating procedure and each local reference as deeper optional guidance.
- Compress vocabulary only when the term is already backed by the skill's workflow or local reference.
- Preserve role-defining boundaries inline even if they are repeated across the architecture family.
- Use focused edits with `apply_patch`; do not run broad mechanical rewrites across the suite.
- After edits, run targeted link/schema/text checks and manual behavior review.
- Use `verification-before-completion` before claiming completion.
- Let the user review the git diff before starting broader follow-up waves.

## Scope exclusions

- Do not perform the broader suite-wide `depends_on` sweep in this issue.
- Do not shorten suite-wide delegation boilerplate in this issue.
- Do not trim `verification-before-completion` repetition in this issue.
- Do not optimize `tdd` guardrails in this issue.
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
- Tighten duplicate reference mentions where a reference appears in both `Workflow` and `References`.
- Trim `verification-before-completion` repetition only where a skill repeats the same closeout gate multiple times.
- Treat TDD guardrail compression as a separate behavior-sensitive pass because the horizontal-slice warning is intentionally behavior-shaping.
- Consider a tiny before/after eval suite for representative skill outputs before applying the optimization style broadly.

## Implementation notes

- Use the IDK glossary as a precision tool, not decoration.
- Good IDK targets: compact read conditions, output labels, acceptance criteria, and short vocabulary definitions.
- Risky IDK targets: architecture tradeoff nuance, anti-overdesign gates, false-seam discipline, and source-evidence requirements.
- For `architecture-design-map`, keep vocabulary descriptive and map-oriented. Avoid importing planning or improvement vocabulary into the hot path unless needed to reject wrong routing.
- For `plan-codebase-architecture`, keep deep module, real seam, dependency category, and public test surface language explicit enough to shape plans.
- For `improve-codebase-architecture`, keep deletion test, false seam, locality, leverage, and replace-don't-layer testing language explicit enough to shape recommendations.
- Prefer existing local references as the vocabulary detail homes. Add a new local reference only if the existing reference would become incoherent.
