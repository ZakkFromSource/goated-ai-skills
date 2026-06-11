## Parent PRD

No separate parent PRD. This issue is based on the user-approved 2026-06-11 token-optimization audit and `grill-with-docs` decision session for the existing GOATED AI Skills suite.

## Type

AFK

## What to build

Optimize the first wave of high-token hotspot skills without reducing skill quality, routing clarity, proof discipline, or installed-skill self-containment.

The first implementation wave should focus on the highest-ROI hotspot skills:

- `skills/engineering/prd-to-issues/SKILL.md`
- `skills/engineering/commit-message/SKILL.md`
- `skills/engineering/write-a-prd/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`

The intended change is not a broad word diet. It is selective, case-by-case optimization:

- EXTRACT late-stage templates, long checklists, examples, and rare deep-dive material into directly linked local `references/` files.
- REFINE hot-path `SKILL.md` prose into denser operating instructions where behavior stays unchanged.
- PRESERVE inline stop rules, proof gates, safety/privacy boundaries, false-positive controls, routing decisions, approval gates, and discipline-heavy reminders that agents are likely to rationalize away.
- ADD local `references/` only inside each affected skill folder. Do not create repo-level shared references that would break standalone installation.
- APPLY hybrid IDK style where useful: use Information Dense Keywords and `Location -> Action -> Detail -> Proof` structure when they reduce ambiguity, but keep explanatory prose readable.

## Audit Evidence To Preserve

The full-suite audit inspected all 30 `SKILL.md` files, category READMEs, and local `references/` files. Subagents separately reviewed `agent-workflows`, `engineering`, and `productivity`; no files were edited during the audit.

Important measurements from the audit:

- 30 `SKILL.md` files total about 52k words.
- Frontmatter is about 8.6k words, or 16.6% of all `SKILL.md` words.
- `depends_on` is the largest frontmatter cost at about 3.4k words.
- Body-section hotspots:
  - `Workflow`: about 19.3k words
  - `Guardrails`: about 6.1k words
  - `Output Contract`: about 6.0k words
  - `Delegation`: about 4.9k words
- Engineering is the heaviest category at about 36.8k words across 19 skills.
- Agent workflows are about 11.5k words across 8 skills.
- Productivity is about 3.7k words across 3 skills.

The high-level verdict was that the suite is structurally healthy. The biggest token win is keeping `SKILL.md` as the hot-path router and operating procedure while moving write-time templates, checklists, examples, and rare deep-dive material into local `references/` files.

Expected savings are not a hard acceptance gate, but a careful pass should plausibly cut 15-25% of always-loaded `SKILL.md` body weight in the heaviest skills by moving detail behind explicit read gates instead of deleting it.

## Settled Decisions

- Optimization posture: selective, case-by-case compression.
- First implementation pass: hotspot skills first, not suite-wide light cleanup.
- Style: hybrid IDK-informed semantic compression.
- Primary goal: reduce always-loaded tokens while preserving the parts that make the skills change agent behavior.
- Use uppercase IDK action keywords mostly in templates, output contracts, and high-value workflow commands.
- Use the IDK vocabulary quietly in normal prose when all-caps would read like keyword soup.
- Do not treat `goated-prompt` as a total voice transplant. Treat it as a model for precise, information-dense classification language.
- Review the git diff after the first wave before deciding whether to apply the pattern more broadly.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `docs/agents/context-matrix.md`
- `docs/agents/project-standards.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/productivity/goated-prompt/references/idk-glossary.md`
- `skills/productivity/goated-prompt/references/prompt-review-checklist.md`
- `skills/engineering/prd-to-issues/SKILL.md`
- `skills/engineering/commit-message/SKILL.md`
- `skills/engineering/write-a-prd/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/source-package-audit.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`

## Relevant source links

- `AGENT.md` - maintainer contract, public boundary, self-contained installed skills, soft 300-line cap, and support-file guidance.
- `CONTEXT.md` - definitions for `SKILL.md`, support files, references, discipline-heavy skills, delegated status enums, and the source-repo/installed-skill/target-project boundary.
- `skills/README.md` - lean schema, progressive disclosure contract, delegation contract, and support-file linking rules.
- `skills/productivity/goated-prompt/SKILL.md` - style reference for dense classification, context calibration, prompt routing, assumptions, output contracts, and concise guardrails.
- `skills/productivity/goated-prompt/references/idk-glossary.md` - Information Dense Keyword guidance and `Location -> Action -> Detail` pattern.
- `skills/engineering/prd-to-issues/SKILL.md` - largest hotspot; embeds approval, issue, order-file, and report templates in `Output Contract`.
- `skills/engineering/commit-message/SKILL.md` - embeds several command/output variants; default command behavior should remain obvious inline.
- `skills/engineering/write-a-prd/SKILL.md` - embeds the full PRD template; a local reference can preserve template detail while making the skill body lighter.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` - largest agent-workflow hotspot; already uses references but still carries long mode/output details inline.

## Acceptance criteria

- [ ] The four first-wave hotspot `SKILL.md` files still follow the lean schema.
- [ ] Each edited skill remains self-contained after installation and depends only on its own folder plus target-project evidence at runtime.
- [ ] New reference files, if added, live one level down under the affected skill's own `references/` folder.
- [ ] Every new reference file is directly linked from its `SKILL.md` with a clear read condition.
- [ ] `prd-to-issues` moves bulky approval, issue, order-file, and report template detail into a local reference while preserving approval-before-writing, fresh-agent-ready issue handoff, blocker order, and local-only behavior.
- [ ] `commit-message` moves non-default output variants into a local reference while preserving the default copy-pasteable command shape, staging safety, quote safety, dirty-tree caveats, and no-mutation rule.
- [ ] `write-a-prd` moves the full PRD template into a local reference while preserving readiness checks, scope/non-goal discipline, source-evidence expectations, and implementation-boundary routing.
- [ ] `framework-agnostic-skill-creator` moves long mode/output details into a local reference where useful while preserving create/port/adapt/evaluate routing, privacy checks, portability checks, and support-file bias.
- [ ] Hybrid IDK style is applied only where it improves clarity: precise action verbs, dense artifact nouns, and `Location -> Action -> Detail -> Proof` structure where useful.
- [ ] Uppercase IDK keywords do not make normal explanatory prose feel mechanical or noisy.
- [ ] Important stop rules, proof gates, safety/privacy boundaries, false-positive controls, routing decisions, approval gates, and discipline-heavy warnings remain inline where needed.
- [ ] No required frontmatter fields are removed.
- [ ] No repo-level shared reference library is introduced.
- [ ] No runtime bootstrap, automatic loading, generated manifest, installer, hook, or adapter automation is introduced.
- [ ] No installed Codex skill copies outside this source repo are edited.
- [ ] `code-security-review`, `tdd`, `verification-before-completion`, architecture vocabulary compression, and suite-wide delegation/verification compression remain out of scope for this first wave unless the user explicitly expands the issue after reviewing the initial diff.
- [ ] The final diff is manually reviewed for behavior preservation, not only token reduction.

## Expected proof

- Run or record a before/after line and rough word-count comparison for the four edited `SKILL.md` files.
- Manual schema review of all four edited `SKILL.md` files.
- Manual check that every new support-file link resolves and has an explicit read condition.
- Targeted search for stale `No external references are required` wording in any edited skill that now has references.
- Targeted search for accidental repo-root runtime dependency wording in edited skills.
- Manual public-boundary pass for private paths, credentials, client data, private notes, raw private source material, or sensitive personal context.
- Manual behavior review for:
  - `prd-to-issues`: approval breakdown, issue template, recommended order file, blocker references, fresh-agent-ready context, scope exclusions, and local-only constraints.
  - `commit-message`: unstaged/all-dirty default command, staged-only behavior, multi-group plan behavior, quote safety, dirty-tree caveats, and skipped-verification caveats.
  - `write-a-prd`: PRD section shape, requirements/non-goals/acceptance criteria, source evidence, risks, open questions, and handoff to downstream skills.
  - `framework-agnostic-skill-creator`: create mode, port/adapt mode, source package audit routing, neutral skill shape, support files, evaluation, privacy, and portability.
- Manual review against the user-approved optimization posture: optimize without "lobotomizing"; move detail behind gates instead of deleting important behavior.
- Use `verification-before-completion` before claiming this issue is implemented, behavior-preserving, or ready for git review.

## Blocked by

- None - the user approved the first-wave scope and asked to create this issue before compacting the chat.

## User stories addressed

- As a maintainer, I can reduce always-loaded token cost in the heaviest GOATED skills without weakening behavior, proof discipline, or installed-skill self-containment.
- As an installed-skill user, I can load hotspot skills faster while still having full templates and checklists available when the workflow reaches the relevant step.
- As a future agent, I can resume implementation from this issue without needing the original chat history.
- As a reviewer, I can inspect a focused first-wave diff before deciding whether the same optimization style should apply to more skills.

## Implementation route

- Start the implementation session by reading this issue plus the recommended first reads.
- Use `writing-plans` before editing if the implementation agent needs a step-by-step patch plan after compacting.
- Use focused edits with `apply_patch`; do not run broad mechanical rewrites across the suite.
- Update one hotspot skill at a time, preserving behavior before moving to the next.
- Prefer local reference extraction first, then light semantic compression inside the touched `SKILL.md`.
- After edits, run targeted link/schema/text checks and manual review.
- Use `verification-before-completion` before claiming completion.
- Let the user review the git diff before starting broader follow-up waves.

## Scope exclusions

- Do not perform a suite-wide light cleanup in this issue.
- Do not optimize `code-security-review`, `tdd`, `verification-before-completion`, architecture vocabulary, or suite-wide delegation/verification contracts in this issue.
- Do not remove the lean schema or required frontmatter fields.
- Do not create category-level, repo-level, or cross-skill shared references unless a future issue changes the installed-skill distribution model.
- Do not create generated indexes, token dashboards, eval harnesses, CI checks, runtime automation, installer automation, plugin manifests, automatic skill loading, hooks, or adapter-sync tooling.
- Do not edit public README/catalog docs unless the first-wave implementation changes public behavior or documented skill inventory.
- Do not make installed skills depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local/` notes, or hidden chat history.

## Follow-up candidates

These were identified in the audit but are intentionally deferred until the first-wave diff is reviewed:

- Compress `depends_on` prose across the suite from sentence form to compact condition form.
- Shorten repeated delegation boilerplate while preserving status enums and controller behavior where needed.
- Move `code-security-review` entry point, asset, sink, risk-class, and severity enumerations into `references/security-review-checklist.md`.
- Deduplicate architecture vocabulary across `architecture-design-map`, `plan-codebase-architecture`, and `improve-codebase-architecture`.
- Tighten duplicate reference mentions where a reference appears in both `Workflow` and `References`.
- Trim `verification-before-completion` repetition only where a skill repeats the same closeout gate multiple times.
- Treat TDD guardrail compression as a separate behavior-sensitive pass because the horizontal-slice warning is intentionally behavior-shaping.
- Consider a tiny before/after eval suite for representative skill outputs before applying the style broadly.

## Implementation notes

- Use the IDK glossary as a precision tool, not decoration.
- Good IDK targets: workflow commands, output contract templates, acceptance criteria, and compact implementation notes.
- Risky IDK targets: explanatory guardrails, discipline-heavy warnings, safety/privacy boundaries, and nuanced tradeoff language.
- Favor verbs such as EXTRACT, REFINE, PRESERVE, VALIDATE, MIRROR, DOCUMENT, and ANALYZE when they reduce ambiguity.
- Favor artifact nouns such as FILE, MODULE, DEFAULT, TYPE, PACKAGE, reference, template, gate, route, evidence, proof, fallback, residual risk, and source of truth.
- Preserve one explicit closeout gate per skill when the skill can lead to completion, ready, synced, passing, or reviewed claims.
