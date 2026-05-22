---
name: standards-and-spec-review
category: engineering
classification: portable
status: wip
description: Use when reviewing changes since a fixed point along separate standards and spec/issue-fit axes, including issue acceptance, missed requirements, or unrequested scope.
triggers:
  - user asks for a standards review, spec review, issue-fit review, acceptance review, or closeout review
  - implementation work is complete and needs a review gate before security review, doc sync, commit, or handoff
  - a change needs comparison against docs/agents/project-standards.md, an issue handoff, PRD, ticket, or implementation spec
  - a reviewer needs standards findings separated from missed requirements or unrequested scope
outputs:
  - review scope with fixed point, changed files, spec source, standards source, and evidence inspected
  - standards findings separated from spec findings
  - evidence-backed findings with affected paths, source evidence, impact, confidence, and recommended fix
  - explicit no-findings statements for clean review axes
  - assumptions, confidence, residual risk, and recommended next step
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before reviewing an unfamiliar target project
    - project-standards-calibration when docs/agents/project-standards.md is missing, stale, or standards need durable capture
    - tdd before this review when behavior was implemented and should have test evidence
    - code-security-review after this review when trust boundaries, user data, auth, persistence, execution, or unsafe configuration may be affected
    - doc-sync after this review when behavior, standards, specs, public interfaces, or docs may have drifted
    - verification-before-completion before claiming the review is complete, clean, or ready for the next closeout step
  fallback: If companion skills, git history, project standards, or a source spec are unavailable, inspect the smallest relevant local evidence, state lower confidence, and separate assumptions from findings.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Standards And Spec Review

## Purpose

Review a completed or in-progress change against two independent contracts:

- **Standards**: whether the change follows the target project's documented standards, inferred conventions, and user-confirmed preferences.
- **Spec**: whether the change satisfies the originating issue, PRD, ticket, or explicit request without missing requirements or adding unrequested scope.

This is a review gate, not an implementation workflow and not a security audit. It should produce high-signal findings backed by files, commands, docs, diffs, test evidence, or explicit assumptions.

## Inputs

- User request and target-project root path.
- Fixed point for the review, such as a base commit, branch, tag, PR base, or issue-start commit.
- Changed files, diffs, commits, staged changes, unstaged changes, or patch under review.
- Originating issue, PRD, ticket, acceptance criteria, implementation spec, user request, or reviewed plan.
- Existing `docs/agents/project-standards.md`, if present.
- Relevant root `CONTEXT.md`, `docs/agents/context-matrix.md`, ADRs, contributor docs, style guides, tests, commands, and nearby source files.
- Prior implementation notes, TDD evidence, prototype verdicts, or known skipped checks when available.

## Workflow

1. Confirm the review scope:
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
   - Separate documented standards, inferred conventions, and user-confirmed preferences when citing evidence.

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
   - Recommend `code-security-review` when the change may touch security-relevant behavior.
   - Recommend `doc-sync` when docs or durable artifacts may need updates.
   - Recommend commit-message or handoff only after review findings and required follow-up are addressed or intentionally accepted.
   - Use `verification-before-completion` before claiming no findings, review completion, review readiness, or next-step readiness; for draft reviews or best-effort scans, verify only the claim being made and state residual risk.

## Output Contract

Return a compact review shaped like this:

```markdown
## Review Scope

- Fixed point: <ref/commit/source and confidence>
- Changed files: <paths or summary>
- Spec source: <issue/PRD/ticket/request or "not found">
- Standards source: <docs/agents/project-standards.md, discovered evidence, or "not found">
- Evidence inspected: <files, commands, docs, diffs, assumptions>

## Standards Findings

- <No findings, or one finding per bullet>
  - Affected path: <path>
  - Evidence: <standard, convention, command, doc, or assumption>
  - Impact: <why it matters for maintainability, consistency, verification, or workflow>
  - Confidence: <high, medium, or low, with a short reason>
  - Recommended fix: <specific change>

## Spec Findings

- <No findings, or one finding per bullet>
  - Affected path: <path>
  - Evidence: <requirement, acceptance criterion, issue note, diff, command, or assumption>
  - Impact: <missed behavior, unrequested scope, acceptance risk, or verification gap>
  - Confidence: <high, medium, or low, with a short reason>
  - Recommended fix: <specific change>

## Assumptions And Confidence

- <assumptions, lower-confidence areas, skipped checks, or residual risk>

## Next Step

- <implementation fixes, code-security-review, doc-sync, commit-message, handoff, or none>
```

If there are no findings on either axis, still include the review scope, explicit no-findings statements, assumptions or residual risk, and the next recommended workflow.

## Delegation

The main agent owns the fixed-point decision, final review judgment, axis separation, and user communication.

When subagents are available, use them only for bounded evidence gathering or independent review passes, such as:

- identifying changed files and the fixed point;
- extracting standards from `docs/agents/project-standards.md` or local docs;
- summarizing the originating spec or acceptance criteria;
- reviewing standards compliance for one source area;
- reviewing spec fit for one source area;
- checking whether reported findings are evidence-backed and in the correct axis.

Require every subagent result to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- paths inspected;
- commands run or deliberately skipped;
- evidence found with source paths;
- assumptions, confidence, and residual risk;
- candidate findings separated into standards and spec concerns.

Handle delegated status this way: `DONE` means merge the candidate evidence and findings into the main review judgment; `DONE_WITH_CONCERNS` means inspect concerns about fixed point, standard source, spec source, confidence, or axis separation before reporting; `NEEDS_CONTEXT` means provide the missing diff, baseline, spec, standards artifact, command output, or source path and re-dispatch; `BLOCKED` means narrow the review scope, choose a clearer fixed point, split standards and spec passes, or escalate to the user.

If subagents are unavailable, perform the same work sequentially with a narrower context budget.

## Guardrails

- Do not perform or claim a security audit. Route exploitable risk, trust-boundary issues, auth, data leaks, injection, unsafe execution, and unsafe config concerns to `code-security-review`.
- Do not mix standards findings and spec findings into one undifferentiated list.
- Do not report speculative findings. If evidence is weak, record an assumption or residual risk instead.
- Do not run mutating commands such as formatters, generators, migrations, codemods, or auto-fixers as part of review unless the user explicitly asks for implementation.
- Do not treat missing `docs/agents/project-standards.md` as a failure by itself; fall back to discovered evidence and state lower confidence.
- Do not invent project standards from ecosystem habits, personal taste, or generic best practices without local evidence.
- Do not treat every supporting edit as unrequested scope; explain the contract, behavior, maintenance, or verification impact.
- Do not silently choose a fixed point when multiple plausible baselines would change the review result.
- Do not broaden the review into implementation, refactoring, architecture redesign, doc-sync, commit writing, or handoff unless the user separately requests that work.
- Do not include private notes, ignored local scratch files, credentials, client data, sensitive personal context, or real user data in review output.
- Do not require this source repo's root docs after installation. The skill may rely only on its own instructions and target-project evidence.

## References

No external references are required. This skill is self-contained after installation.
