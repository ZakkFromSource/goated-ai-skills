## Parent PRD

No separate parent PRD. This issue continues the user-approved 2026-06-11 GOATED AI Skills token-optimization agenda from `issues/053-optimize-hotspot-skill-token-footprint.md`, `issues/054-optimize-code-security-review-token-footprint.md`, and `issues/055-optimize-architecture-vocabulary-token-footprint.md`.

## Type

AFK

## What to build

Optimize duplicate local-reference read gates across implemented `SKILL.md` files without weakening progressive disclosure, installed-skill self-containment, or behavior-shaping reference triggers.

The intended change is selective reference-link compression:

- AUDIT implemented `SKILL.md` files that link local `references/` files.
- IDENTIFY references that are linked once in `Workflow` or `Output Contract` and again in `References` with near-duplicate read/use conditions.
- REFINE each affected skill to keep one authoritative read/use condition per support file where practical.
- PRESERVE direct links from `SKILL.md` to every support file.
- PRESERVE clear read/use timing for every support file.
- KEEP behavior-critical reference gates inline when the point-of-use matters for agent behavior.
- AVOID broad rewrites to the reference files themselves unless a link label, stale wording, or read condition must be corrected.

The optimization target is duplicated link prose, not support-file removal. Local references remain first-class support files.

## Grill decision

After issue `055`, the next slice should be duplicate reference read gates rather than delegation boilerplate, verification repetition, TDD guardrail compression, the broad `depends_on` sweep, or an eval suite.

Rationale:

- It is a focused optimization slice that can be reviewed independently before broader suite-wide compression.
- It directly follows the `skills/README.md` support-file rule: link support files directly, tell agents when to read them, and avoid duplicating the same guidance in both places.
- The pattern is visible in the architecture skills just optimized, plus several other skills with local references.
- It is lower risk than delegation or TDD compression because reference links can be tightened while preserving the actual workflows, stop rules, and proof gates.
- It keeps the user's preference intact: perform specific optimizations before the broader `depends_on` sweep.

Recommended posture: apply a **one authoritative gate** rule, not a mechanical deletion rule.

- If the reference is needed at a precise workflow moment, keep the linked read gate inline and make `References` a compact inventory or remove duplicate condition prose.
- If the reference is general background or final-check guidance, keep the clear read/use condition in `References` and make workflow prose point generically to the relevant reference.
- If both locations genuinely serve different behavior, keep both but compress the repeated words.

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

Prior slices proved the local-reference pattern:

- Issue `053` moved large templates from hotspot skills into local references.
- Issue `054` moved security review checklist detail into a local reference.
- Issue `055` moved architecture vocabulary detail into existing local references.

This issue now tightens the repeated pointers created by that support-file bias.

## Current scan evidence

A targeted scan found multiple skills where the same local reference is mentioned in a workflow step and again under `References`:

- `skills/productivity/goated-prompt/SKILL.md`
- `skills/engineering/writing-plans/SKILL.md`
- `skills/engineering/write-a-prd/SKILL.md`
- `skills/engineering/architecture-design-map/SKILL.md`
- `skills/engineering/plan-codebase-architecture/SKILL.md`
- `skills/engineering/improve-codebase-architecture/SKILL.md`
- `skills/engineering/verification-before-completion/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/engineering/doc-sync/SKILL.md`
- `skills/engineering/grill-with-docs/SKILL.md`
- `skills/engineering/tdd/SKILL.md`
- `skills/engineering/code-security-review/SKILL.md`
- `skills/engineering/diagnose/SKILL.md`
- `skills/engineering/documentation-writer/SKILL.md`
- `skills/engineering/subagent-driven-development/SKILL.md`
- `skills/engineering/prototype/SKILL.md`
- `skills/engineering/commit-message/SKILL.md`
- `skills/engineering/prd-to-issues/SKILL.md`
- `skills/engineering/documentation-cleanup/SKILL.md`

This list is a starting point, not a mandate to edit every file. The implementation agent should inspect each candidate and skip files where the duplicate mention is actually behavior-preserving.

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
- `issues/055-optimize-architecture-vocabulary-token-footprint.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/goated-prompt/references/idk-glossary.md`
- Candidate `SKILL.md` files from the current scan evidence, opened only as needed.
- `skills/engineering/verification-before-completion/SKILL.md`

## Relevant source links

- `AGENT.md` - maintainer contract, public boundary, self-contained installed skills, soft 300-line cap, and support-file guidance.
- `CONTEXT.md` - definitions for `SKILL.md`, support files, references, progressive disclosure, installed skill self-containment, and public-safe boundaries.
- `skills/README.md` - lean schema, progressive disclosure contract, support-file linking rules, and "avoid duplicating the same guidance in both places" rule.
- `issues/053-optimize-hotspot-skill-token-footprint.md` - first local-reference extraction wave.
- `issues/054-optimize-code-security-review-token-footprint.md` - specialist checklist extraction pattern.
- `issues/055-optimize-architecture-vocabulary-token-footprint.md` - focused vocabulary extraction and carried-forward follow-up candidates.

## Acceptance criteria

- [ ] All edited `SKILL.md` files still follow the lean schema.
- [ ] Every edited skill remains self-contained after installation and depends only on its own folder plus target-project evidence at runtime.
- [ ] No repo-level, category-level, or cross-skill shared reference library is introduced.
- [ ] No local reference file is removed merely to save tokens.
- [ ] Every support file referenced by an edited `SKILL.md` remains directly linked from that `SKILL.md`.
- [ ] Every linked support file still has a clear read/use condition.
- [ ] Duplicate reference mentions are tightened so near-identical read/use conditions do not appear in both workflow prose and `References` unless they serve different behavior.
- [ ] Behavior-critical point-of-use gates remain inline where timing affects workflow quality.
- [ ] `References` sections remain useful as compact inventories, canonical reference gates, or are omitted only when the workflow already carries the direct link and read condition clearly.
- [ ] No `No external references are required` wording remains in an edited skill that links local support files.
- [ ] No behavior-changing stop rule, proof gate, safety/privacy boundary, false-positive control, routing decision, approval gate, or discipline-heavy warning is removed.
- [ ] Hybrid IDK wording improves clarity without making normal prose mechanical.
- [ ] No required frontmatter fields are removed.
- [ ] No runtime bootstrap, automatic loading, generated manifest, installer, hook, adapter automation, eval harness, CI check, or token dashboard is introduced.
- [ ] No installed Codex skill copies outside this source repo are edited.
- [ ] The final diff is manually reviewed for behavior preservation, not only token reduction.

## Expected proof

- Record before/after line and rough word counts for edited `SKILL.md` files.
- Record which candidate files were inspected and intentionally skipped.
- Manual schema review of edited `SKILL.md` files.
- Manual check that every edited support-file link resolves and has a clear read/use condition.
- Targeted search for duplicate local-reference read conditions in edited files.
- Targeted search for stale `No external references are required` wording in edited files.
- Targeted search for accidental repo-root runtime dependency wording.
- Manual public-boundary pass for private paths, credentials, client data, private notes, raw private source material, sensitive personal context, secrets, or real user data.
- Manual behavior review for edited discipline-heavy skills to ensure reference-gate compression did not remove stop rules, proof gates, or routing decisions.
- Use `verification-before-completion` before claiming this issue is implemented, behavior-preserving, or ready for git review.

## Blocked by

- None - the docs-grounded decision pass selected this as the next focused optimization slice after issue `055`.

## User stories addressed

- As a maintainer, I can reduce repeated reference-link prose without weakening progressive disclosure.
- As an installed-skill user, I can see when to load local support files without paying for duplicated instructions in every skill body.
- As a reviewer, I can inspect a focused support-file-link cleanup before broader delegation or dependency compression begins.
- As a future agent, I can continue the token optimization agenda without relying on hidden chat history.

## Implementation route

- Start by reading this issue plus the recommended first reads.
- Use `writing-plans` before editing if the implementation agent needs a step-by-step patch plan after context compaction.
- Run a targeted scan for local reference links in `SKILL.md` files.
- Inspect each candidate before editing; do not apply a blind regex replacement.
- Keep one authoritative read/use condition per reference where practical.
- Preserve point-of-use gates when the reference timing changes behavior.
- Use focused edits with `apply_patch`; do not run broad mechanical rewrites across the suite.
- After edits, run targeted link/schema/text checks and manual behavior review.
- Use `verification-before-completion` before claiming completion.
- Let the user review the git diff before starting broader follow-up waves.

## Scope exclusions

- Do not perform the broader suite-wide `depends_on` sweep in this issue.
- Do not shorten suite-wide delegation boilerplate in this issue.
- Do not trim `verification-before-completion` repetition except when it is solely duplicate reference-link prose.
- Do not optimize `tdd` guardrails beyond duplicate reference-link prose in this issue.
- Do not add a before/after eval suite in this issue.
- Do not remove the lean schema or required frontmatter fields.
- Do not create category-level, repo-level, or cross-skill shared references.
- Do not create generated indexes, token dashboards, eval harnesses, CI checks, runtime automation, installer automation, plugin manifests, automatic skill loading, hooks, or adapter-sync tooling.
- Do not edit public README/catalog docs unless this implementation changes public behavior or documented skill inventory.
- Do not make installed skills depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local` notes, or hidden chat history.

## Follow-up candidates

Carry these forward after this slice. The user specifically wants the broader `depends_on` sweep after the specific optimizations are handled.

- Compress `depends_on` prose across the suite from sentence form to compact condition form after focused specialist optimizations.
- Shorten repeated delegation boilerplate while preserving status enums and controller behavior where needed.
- Trim `verification-before-completion` repetition only where a skill repeats the same closeout gate multiple times.
- Treat TDD guardrail compression as a separate behavior-sensitive pass because the horizontal-slice warning is intentionally behavior-shaping.
- Consider a tiny before/after eval suite for representative skill outputs before applying the optimization style broadly.

## Implementation notes

- Use the IDK glossary as a precision tool, not decoration.
- Good IDK targets: compact read conditions, reference labels, output labels, and proof notes.
- Risky IDK targets: discipline-heavy warnings, safety/privacy boundaries, false-positive controls, TDD anti-rationalization gates, and nuanced tradeoff language.
- Prefer `Read <reference> when...` only once per support file unless the second mention serves a materially different workflow moment.
- For multi-reference skills, consider a compact `References` inventory with short labels while keeping detailed gates at point of use.
- For skills with a single reference, consider keeping the link only at point of use if the `References` section adds no unique routing value.
- For discipline-heavy skills, preserve the strongest behavior-shaping gate even if a few extra words remain.
