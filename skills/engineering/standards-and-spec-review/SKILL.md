---
name: standards-and-spec-review
description: Use when diff size, risk, acceptance ambiguity, scope fit, or uncertain project conventions justify a standards and/or spec review.
metadata:
  goated-category: engineering
---

# Standards And Spec Review

## Purpose

Review a completed or in-progress change against two independent contracts:

- **Standards**: whether the change follows the target project's documented standards, inferred conventions, and user-confirmed preferences, while respecting enforcement strength.
- **Spec**: whether the change satisfies the originating issue, PRD, ticket, or explicit request without missing requirements or adding unrequested scope.

This is a review gate, not an implementation workflow and not a security audit. It should produce high-signal findings backed by files, commands, docs, diffs, test evidence, or explicit assumptions.

## Activation

Load this skill when at least one axis remains meaningfully uncertain:

- **Spec**: acceptance coverage, intended behavior, allowed scope, exclusions,
  lifecycle movement, or public-contract fit.
- **Standards**: a larger or riskier diff makes direct inspection insufficient,
  a changed area spans conventions, or documented/inferred conventions conflict
  or remain uncertain.

Scale depth with diff size, risk, acceptance ambiguity, and convention
uncertainty. A small, familiar, low-risk change with clear acceptance can check
fit directly from the shared policy without loading this skill. Review only the
uncertain axis when practical; do not require ceremonial coverage of both.

## Inputs

- User request and target-project root path.
- Fixed point for the review, such as a base commit, branch, tag, PR base, or issue-start commit.
- Changed files, diffs, commits, staged changes, unstaged changes, or patch under review.
- Originating issue, PRD, ticket, acceptance criteria, implementation spec, user request, or reviewed plan.
- Existing `docs/agents/project-standards.md`, if present.
- Relevant root `CONTEXT.md`, `docs/agents/context-matrix.md`, ADRs, contributor docs, style guides, tests, commands, and nearby source files.
- Prior implementation notes, TDD evidence, prototype verdicts, or known skipped checks when available.

## Dependencies

Hard: None.

Soft:
- session-start-progressive-disclosure for unfamiliar target projects
- project-standards-calibration when docs/agents/project-standards.md is missing, stale, or standards need durable capture
- tdd when implemented behavior should have test evidence
- code-refinement when findings call for scoped behavior-preserving cleanup or simplification
- code-security-review when trust boundaries, user data, auth, persistence, execution, or unsafe config may be affected
- doc-sync after this review when behavior, standards, specs, public interfaces, or docs may have drifted
- verification-before-completion for complex, high-risk, delegated,
  multi-surface, or explicitly audited review closeout; otherwise verify narrow
  findings or no-findings wording directly

Fallback: If companion skills, git history, standards, or source spec are unavailable, inspect minimal local evidence, state lower confidence, and separate assumptions from findings.

## Workflow

1. Confirm the review scope:
   - Reuse fresh diff, source, spec, standards, and proof entries from the work
     envelope. Refresh only stale, invalidated, or claim-insufficient evidence.
   - Identify the target-project root and whether the review covers committed changes, staged changes, unstaged changes, or a supplied patch.
   - Identify the originating issue, PRD, ticket, spec, or user request. If none exists, review against the explicit user request and state lower spec confidence.
   - List changed files before reviewing. In git projects, use an equivalent of `git status --short`, `git diff --name-status <fixed-point>...HEAD`, and working-tree diff commands as appropriate for the requested scope.
   - Use non-mutating commands by default. Do not format, generate, migrate, rewrite, or otherwise repair files during the review unless the user separately asks for implementation.

2. Discover the fixed point:
   - Use an explicit base from the user, PR metadata, issue handoff, or review request when provided.
   - Otherwise infer from local evidence: current branch upstream, merge-base with the likely trunk branch, PR base, or the obvious base named by the project workflow.
   - Ask the user only when no baseline can be found or multiple plausible baselines would materially change the reviewed diff.
   - Record the fixed point, how it was chosen, and confidence.

3. Gather standards evidence:
   - Read `docs/agents/project-standards.md` when present and treat it as the strongest local standards profile.
   - If it is missing, inspect the minimum relevant docs, agent instructions, contributor guidance, configs, tests, and nearby files needed to infer standards.
   - State lower confidence when standards are inferred without a standards profile.
   - Separate documented standards, inferred conventions, and user-confirmed preferences when citing evidence. Treat `preference-only` entries as review evidence only when they do not conflict with tooling-enforced checks, documented standards, stronger project instructions, or clearly sourced local conventions.

4. Gather spec evidence:
   - Read the originating issue, PRD, ticket, accepted plan, acceptance criteria, and relevant user instructions.
   - Identify required behavior, non-goals, blocker notes, verification expectations, public interfaces, docs expectations, and explicit exclusions.
   - If the spec is ambiguous or incomplete, record the assumption before reviewing against it.

5. Review the diff on two axes:
   - Standards axis: look for deviations from documented standards, local conventions, naming/layout patterns, schema or API conventions, test style, docs style, dependency behavior, and required verification.
   - Spec axis: look for missed acceptance criteria, behavior mismatches, partial implementation, unrequested scope, changed public contracts, missing tests or docs required by the spec, and stale issue assumptions.
   - When the diff includes issue closure, archive moves, renames, or completion-status edits, treat that lifecycle movement as part of spec fit and check whether acceptance and required review evidence support it.
   - Keep findings in the correct axis. If a concern is both a standards and spec issue, report it once in the primary axis and cross-reference the other axis briefly.

6. Report only evidence-backed findings:
   - Each finding must include affected path, evidence source, impact, confidence, and recommended fix.
   - Prefer precise file paths, line references when available, command output summaries, and quoted requirement names over broad impressions.
   - Treat unrequested scope as a finding only when it changes public behavior, maintenance burden, verification expectations, or the agreed contract.
   - If an axis has no findings, say that explicitly.
   - Include residual risk for skipped commands, missing specs, absent standards profile, unreviewed generated files, large diffs, or weak test evidence.

7. Recommend the next step:
   - Recommend implementation fixes when findings exist.
   - Recommend `code-refinement` when findings are scoped behavior-preserving cleanup, simplification, or local refactor issues.
   - Recommend `code-security-review` when the change may touch security-relevant behavior.
   - Recommend `doc-sync` when docs or durable artifacts may need updates.
   - Recommend commit-message or handoff only after review findings and required follow-up are addressed or intentionally accepted.
   - Verify findings and no-findings wording against fresh scoped evidence.
     Load `verification-before-completion` only when complexity, risk,
     delegation, multiple surfaces, or an explicit audit warrants the full
     controller.
   - Emit findings, confidence changes, proof gaps, and route deltas into the
     envelope rather than producing a competing closeout.

## Output Contract

Return findings for the activated axis or axes. Include fixed point, changed
scope, evidence inspected, confidence, and residual risk once, then report:

```markdown
- `<axis> finding`: affected path, requirement or convention, evidence, impact,
  confidence, and recommended fix.
- `<axis> no findings`: exact reviewed scope and material residual risk.
- `Route delta`: newly required implementation, security, docs, proof, or user
  decision; omit when unchanged.
```

Do not repeat the full envelope, another specialist's report, or the controller's
final closeout.

## Delegation

Main owns the fixed-point decision, final review judgment, axis separation, and user communication.

Delegate only bounded evidence or review passes: identify changed files/fixed point, extract standards, summarize spec/acceptance criteria, review standards or spec fit for one area, or check whether findings are evidence-backed and in the correct axis.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths inspected; commands run or skipped; source-path evidence; assumptions, confidence, residual risk; and candidate findings separated into standards vs spec concerns.

Status handling: `DONE` merges evidence/findings into the review judgment; `DONE_WITH_CONCERNS` requires review of fixed point, standard source, spec source, confidence, or axis separation before reporting; `NEEDS_CONTEXT` gets missing diff, baseline, spec, standards artifact, command output, or source path before re-dispatch; `BLOCKED` narrows scope, chooses a clearer fixed point, splits axes, or escalates.

If subagents are unavailable, run the same work sequentially with a narrower context budget.

## Guardrails

- Do not perform or claim a security audit. Route exploitable risk, trust-boundary issues, auth, data leaks, injection, unsafe execution, and unsafe config concerns to `code-security-review`.
- Do not mix standards findings and spec findings into one undifferentiated list.
- Do not report speculative findings. If evidence is weak, record an assumption or residual risk instead.
- Do not run mutating commands such as formatters, generators, migrations, codemods, or auto-fixers as part of review unless the user explicitly asks for implementation.
- Do not treat missing `docs/agents/project-standards.md` as a failure by itself; fall back to discovered evidence and state lower confidence.
- Do not invent project standards from ecosystem habits, personal taste, or generic best practices without local evidence.
- Do not let user-confirmed `preference-only` entries outweigh tooling-enforced checks, documented standards, stronger project instructions, or clearly sourced local conventions.
- Do not treat every supporting edit as unrequested scope; explain the contract, behavior, maintenance, or verification impact.
- Do not silently choose a fixed point when multiple plausible baselines would change the review result.
- Do not broaden the review into implementation, refactoring, architecture redesign, doc-sync, commit writing, or handoff unless the user separately requests that work.
- Do not include private notes, ignored local scratch files, credentials, client data, sensitive personal context, or real user data in review output.
- Do not require this source repo's root docs after installation. The skill may rely only on its own instructions and target-project evidence.

## References

No external references are required. This skill is self-contained after installation.
