---
name: verification-before-completion
description: Use before claiming that complex, high-risk, delegated, multi-surface, or explicitly audited work is done, fixed, or passing; narrow work can verify directly without it.
metadata:
  goated-category: engineering
---

# Verification Before Completion

## Purpose

Gate completion, correctness, readiness, and success claims on fresh evidence.

Fresh, claim-scoped evidence is universal. This skill is the full controller,
not a mandatory closeout payload for every task.

Treat issue lifecycle actions as completion claims. Closing, archiving, moving, renaming, or marking an issue, ticket, or handoff complete is allowed only when the completion claim is freshly verified and any required user, maintainer, PR, or project-defined review is complete.

This skill does not replace implementation, TDD, standards/spec review, security review, doc sync, or handoff. It verifies the claim being made and routes missing proof to the right workflow.

## Activation

Load the full controller when work is complex, high-risk, delegated,
multi-surface, or explicitly audited. Those conditions justify reconciling
multiple claims, evidence sources, specialist deltas, skipped checks, and
residual risks. They always hold when the task's route is `full`, a subagent
changed code, a security-sensitive file changed, or the branch's work is 400
or more changed lines.

For narrow, low-risk, single-surface work, verify directly from shared policy:
name the claim, gather fresh matching evidence, report failures or skips, and
limit wording to what the evidence proves. In standalone use without shared
policy, apply that compact discipline here without reconstructing the full
workflow or requiring a formal skip report.

## Inputs

- The exact claim the agent wants to make.
- The relevant change, review scope, artifact, issue, PRD, user request, patch, commit range, or working-tree state.
- Evidence sources such as command output, tests, builds, linters, diffs, source reads, rendered artifacts, screenshots, CI results, manual checks, docs inspection, or subagent reports.
- Known failed checks, skipped checks, flaky checks, unavailable tools, environment limits, and safety constraints.
- User instructions about scope, urgency, acceptable risk, or requested level of verification.

## Dependencies

Hard: None.

Soft:
- tdd for missing behavior, regression, or test-surface proof
- code-refinement for scoped behavior-preserving cleanup before a review-ready or closeout claim
- software-design-principles when a claim covers a changed module, interface, error-handling path, or configuration surface
- standards-and-spec-review for issue fit, acceptance, or standards
- code-security-review for security-relevant behavior or trust boundaries
- doc-sync for possible documentation drift
- handoff when residual risk or unfinished verification needs continuity

Fallback: If companion skills, commands, tools, artifacts, or runtime access are unavailable, inspect minimal evidence, state unverified facts, downgrade unsupported claims, and report residual risk.

## Workflow

1. Name the claim before proving it:
   - Reuse the work envelope's current claims, selected gates, evidence entries,
     specialist findings, and known gaps instead of rebuilding task history.
   - Write the claim as a concrete sentence, such as "the focused tests pass", "issue acceptance is covered", "docs are synced", or "the implementation is ready for review".
   - If the next action would close, archive, move, rename, or mark an issue complete, name that lifecycle action as the claim.
   - If the user asked only for a draft, analysis, or best-effort scan, verify only the claims you actually intend to make.
   - State a stronger claim directly instead of a vague substitute such as "looks good".

2. Set the freshness boundary:
   - Evidence is fresh only if it was gathered after the relevant change, review scope, artifact, or completion claim was known.
   - A previous command run, earlier screenshot, stale CI result, old subagent note, or pre-change source read can provide context, but it does not prove the current claim.
   - If files, generated output, dependencies, configuration, or the review scope changed after evidence was gathered, treat that evidence as stale for affected claims.

3. Choose evidence that matches the claim:
   - Tests passing require test output for the relevant test command, suite, or CI job.
   - Build, lint, format, type, migration, generated-artifact, or docs claims require the corresponding command output or artifact inspection.
   - Bug-fix and feature-completion claims require proof of the original behavior or acceptance criteria, not just a code diff.
   - When a feature depends on runtime data, such as a profile, a configuration, or a model, exercise it against the owner's active data, not only fixtures.
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
   - Use `code-refinement` when recently changed code needs scoped cleanup before a review-ready or closeout claim and behavior should not change.
   - Use `standards-and-spec-review` when issue fit, acceptance coverage, standards, or unrequested scope is unclear.
   - Use `code-security-review` when the claim touches trust boundaries, auth, permissions, user data, persistence, unsafe execution, or security-sensitive configuration.
   - Use `doc-sync` when changed behavior or docs may have drifted.
   - Use `handoff` when the work cannot be safely completed now and a future agent needs the exact residual risk.

8. Report the verification summary before the success claim:
   - Put evidence and limitations next to the claim.
   - If evidence supports only a narrower statement, use the narrower statement.
   - If checks failed or were skipped, say so plainly and name the next useful step.
   - Update the envelope with verified facts, stale or rejected evidence,
     remaining gaps, and route deltas. The controlling agent owns one
     consolidated final response.

## Output Contract

Return a verification delta shaped like this:

```markdown
- Claim checked: <completion, correctness, passing, review-ready, docs-synced, or other claim>
- Status: <verified | partially verified | not verified | failed>
- Evidence delta: <fresh, reused, invalidated, stale, or rejected entries>
- Gaps: <assumptions, skipped checks, failures, and residual risk>
- Completion claim: <allowed claim, downgraded claim, or "do not claim completion">
- Route delta: <new proof, review, docs, fix, decision, or handoff gate; omit when unchanged>
```

Do not repeat source content, specialist reports, or the full work envelope. For
standalone use, include enough scope and evidence detail to keep the result
auditable without another artifact.

## Delegation

Main owns the final claim, evidence standard, risk judgment, and communication.
Delegate only bounded commands, artifact/diff inspection, claim-strength checks,
stale-evidence pressure tests, or summary review. Delegates return inspected
surfaces and commands, fresh applicable evidence, assumptions, skips, failures,
risk, confidence, status, and a recommendation—not a final claim; resolve
concerns or missing context first, narrow or stop on `BLOCKED`, and verify
sequentially without delegation.

## Guardrails

- Claim completion, correctness, passing checks, review readiness, docs sync, security confidence, or successful implementation only with fresh matching evidence.
- Match proof to claim breadth: a passing partial check, code change, clean-looking diff, or generated summary does not prove that broader behavior works.
- Report failed checks, skipped checks, warnings, flaky results, missing artifacts, and environment limits plainly, not behind positive wording.
- Use whatever test runner, CI provider, git host, browser, artifact renderer, or agent framework the project has; none is required.
- Keep credentials, secrets, and private or real user data out of verification summaries.

## References

Linked support file, read at the workflow gate above: [Evidence Map](references/evidence-map.md).
