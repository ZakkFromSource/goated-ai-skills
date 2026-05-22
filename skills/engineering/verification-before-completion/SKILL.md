---
name: verification-before-completion
category: engineering
classification: portable
status: wip
description: Use before claiming work is complete, correct, fixed, passing, review-ready, documentation-synced, or successfully verified.
triggers:
  - user asks whether implementation, review, testing, docs, or closeout work is done
  - an agent is about to say work is complete, correct, fixed, passing, clean, reviewed, ready, or synced
  - an agent is about to close, archive, move, rename, or mark an issue, ticket, or handoff complete
  - command, test, build, lint, rendered artifact, screenshot, source read, diff, CI, or manual smoke-test evidence is needed before a success claim
  - subagent or tool reports need sanity-checking before the main agent relies on them
  - checks failed, were skipped, or cannot run and the final response needs honest residual risk
outputs:
  - exact claim being verified or downgraded
  - fresh evidence gathered after the relevant change, review scope, or claim is known
  - verified facts separated from assumptions, skipped checks, known failures, and residual risk
  - subagent or tool reports that were independently sanity-checked or marked unverified
  - issue lifecycle actions allowed, withheld, or downgraded based on verified acceptance and required review evidence
  - concise verification summary with evidence names, results, skipped checks, remaining risk, and next step
depends_on:
  hard: []
  soft:
    - tdd when missing proof is behavior, regression, red/green, or test-surface evidence
    - standards-and-spec-review when completion depends on issue fit, acceptance criteria, or project standards
    - code-security-review when completion depends on security-relevant behavior, trust boundaries, auth, user data, persistence, execution, or unsafe configuration
    - doc-sync when behavior, interfaces, docs, standards, configuration, or tests may have documentation drift
    - handoff when residual risk, skipped checks, known failures, or unfinished verification should be preserved for a future session
  fallback: If companion skills, commands, tools, artifacts, or runtime access are unavailable, inspect the smallest useful local evidence, state what is unverified, downgrade unsupported claims, and report residual risk.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Verification Before Completion

## Purpose

Gate completion, correctness, readiness, and success claims on fresh evidence.

Use this skill at closeout, before commit or PR summaries, before moving to another task, or whenever wording would imply that work is complete, correct, passing, reviewed, fixed, synced, or safe. The goal is not ceremony. The goal is that the final claim matches what was actually checked.

Treat issue lifecycle actions as completion claims. Closing, archiving, moving, renaming, or marking an issue, ticket, or handoff complete is allowed only when the completion claim is freshly verified and any required user, maintainer, PR, or project-defined review is complete.

This skill does not replace implementation, TDD, standards/spec review, security review, doc sync, or handoff. It verifies the claim being made and routes missing proof to the right workflow.

## Inputs

- The exact claim the agent wants to make.
- The relevant change, review scope, artifact, issue, PRD, user request, patch, commit range, or working-tree state.
- Evidence sources such as command output, tests, builds, linters, diffs, source reads, rendered artifacts, screenshots, CI results, manual checks, docs inspection, or subagent reports.
- Known failed checks, skipped checks, flaky checks, unavailable tools, environment limits, and safety constraints.
- User instructions about scope, urgency, acceptable risk, or requested level of verification.

## Workflow

1. Name the claim before proving it:
   - Write the claim as a concrete sentence, such as "the focused tests pass", "issue acceptance is covered", "docs are synced", or "the implementation is ready for review".
   - If the next action would close, archive, move, rename, or mark an issue complete, name that lifecycle action as the claim.
   - If the user asked only for a draft, analysis, or best-effort scan, verify only the claims you actually intend to make.
   - Do not use vague substitutes such as "looks good" when you mean a stronger claim.

2. Set the freshness boundary:
   - Evidence is fresh only if it was gathered after the relevant change, review scope, artifact, or completion claim was known.
   - A previous command run, earlier screenshot, stale CI result, old subagent note, or pre-change source read can provide context, but it does not prove the current claim.
   - If files, generated output, dependencies, configuration, or the review scope changed after evidence was gathered, treat that evidence as stale for affected claims.

3. Choose evidence that matches the claim:
   - Tests passing require test output for the relevant test command, suite, or CI job.
   - Build, lint, format, type, migration, generated-artifact, or docs claims require the corresponding command output or artifact inspection.
   - Bug-fix and feature-completion claims require proof of the original behavior or acceptance criteria, not just a code diff.
   - Issue closure or archive claims require acceptance criteria checked against current behavior and evidence that any required user, maintainer, PR, or project-defined review is complete.
   - Review-ready claims require inspected diffs, source reads, review gates, or artifact checks that match the requested review scope.
   - Documentation-sync claims require changed facts and relevant docs to have been checked.
   - Read [Evidence Map](references/evidence-map.md) when choosing proof, handling non-command evidence, or resisting shortcut rationalizations.

4. Gather and read the evidence:
   - Run the smallest command or inspect the smallest artifact set that can prove the claim without hiding important risk.
   - Read outputs before reporting them: exit code, failed count, skipped count, warnings, relevant paths, artifact state, screenshots, or source evidence.
   - For manual or visual checks, record what was inspected, from which artifact or screen, and what result was observed.
   - Do not run unsafe, destructive, expensive, credentialed, or irrelevant checks just to appear thorough. Mark them skipped with a reason and residual risk.

5. Sanity-check delegated or tool-reported proof:
   - Treat subagent reports, generated summaries, external tools, and CI dashboards as evidence leads.
   - Before relying on important delegated evidence, the main agent must inspect the relevant diff, source, artifact, command output, log, screenshot, or rerun a focused check.
   - If important delegated evidence cannot be reproduced or inspected, label it as unverified delegated evidence and do not use it for a completion claim.

6. Classify the result:
   - **Verified facts** are directly supported by fresh evidence.
   - **Assumptions** are plausible but not directly proven.
   - **Skipped checks** are checks not run or artifacts not inspected, with reasons.
   - **Known failures** are failing commands, broken artifacts, rejected claims, or review findings.
   - **Residual risk** is what remains uncertain after the evidence gathered.
   - Allow only the part of the claim supported by verified facts. Downgrade or withhold unsupported claims.
   - If required review is still pending, report the work as ready for review, partially verified, or otherwise residual-risk-bearing, and leave the issue active.

7. Route missing proof:
   - Use `tdd` when behavior or regression proof is missing and a testable implementation path exists.
   - Use `standards-and-spec-review` when issue fit, acceptance coverage, standards, or unrequested scope is unclear.
   - Use `code-security-review` when the claim touches trust boundaries, auth, permissions, user data, persistence, unsafe execution, or security-sensitive configuration.
   - Use `doc-sync` when changed behavior or docs may have drifted.
   - Use `handoff` when the work cannot be safely completed now and a future agent needs the exact residual risk.

8. Report the verification summary before the success claim:
   - Put evidence and limitations next to the claim.
   - If evidence supports only a narrower statement, use the narrower statement.
   - If checks failed or were skipped, say so plainly and name the next useful step.

## Output Contract

Return a compact summary shaped like this:

```markdown
## Verification Summary

- Claim checked: <completion, correctness, passing, review-ready, docs-synced, or other claim>
- Status: <verified | partially verified | not verified | failed>
- Verified facts: <fresh evidence-backed facts>
- Evidence and commands: <command names and results, source reads, diffs, artifacts, screenshots, CI, manual checks, or "none">
- Assumptions: <assumptions still present, or "None">
- Skipped checks: <checks or artifacts skipped with reasons, or "None">
- Known failures: <failures, warnings that block the claim, rejected evidence, or "None">
- Residual risk: <remaining uncertainty, or "Low">
- Completion claim: <allowed claim, downgraded claim, or "do not claim completion">
- Next step: <finish, rerun check, fix failure, route to another skill, or handoff>
```

For a very small direct command, a one-line summary is acceptable only when it still names the command or artifact and does not overclaim.

## Delegation

The main agent owns the final claim, evidence standard, risk judgment, and user communication.

When subagents are available, use them for bounded verification passes, such as:

- running a focused command in a separate environment;
- inspecting a diff, artifact, screenshot, or documentation surface;
- checking whether a claim-to-evidence match is strong enough;
- pressure-testing whether skipped checks or stale evidence were overclaimed;
- reviewing the verification summary for unsupported wording.

Require delegated verification results to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- paths, artifacts, screenshots, diffs, or commands inspected;
- fresh evidence gathered and when it applies;
- assumptions, skipped checks, known failures, residual risk, and confidence;
- recommendation about the claim, not an unsupervised final claim.

Handle delegated status this way: `DONE` means integrate the evidence after sanity-checking important proof; `DONE_WITH_CONCERNS` means inspect the concerns before making any success claim; `NEEDS_CONTEXT` means provide the missing scope, artifact, command, or expected behavior and re-dispatch or verify locally; `BLOCKED` means narrow the claim, choose a safer proof path, report residual risk, or hand off.

If subagents are unavailable, perform the same verification sequentially with a narrower context budget.

## Guardrails

- Do not claim completion, correctness, passing checks, review readiness, docs sync, security confidence, or successful implementation without fresh matching evidence.
- Do not close, archive, move, rename, or mark an issue, ticket, or handoff complete unless all required acceptance and review evidence supports that lifecycle action.
- Do not reuse stale proof as if it proves the current scope.
- Do not treat a passing partial check as proof for a broader claim.
- Do not treat code changes, clean-looking diffs, or generated summaries as proof that behavior works.
- Do not treat subagent success reports as proof until important evidence is inspected or reproduced by the main agent.
- Do not hide failed checks, skipped checks, warnings, flaky results, missing artifacts, or environment limits behind positive wording.
- Do not run unsafe or irrelevant commands to satisfy the form of verification. Report why they were skipped.
- Do not require a specific test runner, CI provider, git host, browser, artifact renderer, or agent framework.
- Do not include private notes, credentials, ignored scratch content, client data, secrets, sensitive personal context, or real user data in verification summaries.
- Do not require this source repo's root files after installation. The skill may rely only on its own files and target-project evidence.

## References

- [Evidence Map](references/evidence-map.md) - read when matching claims to proof, using non-command evidence, handling delegated evidence, or countering shortcut rationalizations.
