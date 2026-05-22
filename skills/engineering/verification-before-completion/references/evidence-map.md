# Evidence Map

Read this reference when choosing evidence for a completion claim, when the work is docs-only or artifact-heavy, or when pressure makes stale proof tempting.

## Claim To Evidence

| Claim | Fresh evidence that can support it | Evidence that is not enough by itself |
| --- | --- | --- |
| Tests pass | Relevant test command, focused test output, CI job result, or test report gathered after the current change or scope is known | Earlier run, another agent's summary, no-failure assumption |
| Build, lint, typecheck, or format is clean | The matching command output or tool report for the relevant scope | A different check passing, clean-looking code, editor hints |
| Bug is fixed | Reproduction or regression proof for the original symptom, plus relevant surrounding checks | Code changed, plausible reasoning, unrelated tests |
| Feature or issue is complete | Acceptance criteria checked against current behavior, source, artifacts, docs, and relevant tests | Passing tests that do not cover acceptance, implementation notes alone |
| Issue or ticket can be archived or marked complete | Acceptance criteria checked against current behavior, source, artifacts, docs, relevant tests, and any required user, maintainer, PR, or project-defined review | Implementation done locally, ready for review, partial verification, or no explicit review evidence |
| Review-ready | Current diff or patch inspected, relevant review gates run or intentionally skipped, known risks reported | "Looks good", uninspected generated output, stale review notes |
| Docs are synced | Changed facts identified and relevant docs checked or updated | Updating one doc without checking affected docs, assuming docs are irrelevant |
| Rendered output is correct | Rendered artifact, screenshot, preview, generated file, or exported output inspected after the latest change | Source text only when rendering can change layout or behavior |
| Security-sensitive change is safe | Focused security review evidence for the changed trust path and explicit residual risk | Tests passing, standards review, or absence of obvious suspicious code |
| Delegated work is complete | Main-agent sanity check of changed paths, source, diffs, artifacts, or key command output | Subagent says "done" or "tests pass" without inspected evidence |

## Non-Command Evidence

Not every useful claim needs a command. Non-command evidence can be valid when it directly matches the claim and is fresh:

- Source reads: cite the paths, symbols, config, schema, or docs inspected.
- Diffs: cite the changed paths and what the diff proves or does not prove.
- Rendered artifacts: cite the file, screen, export, screenshot, or preview inspected.
- Manual smoke checks: cite the exact flow, input, environment, and observed result.
- CI or tool dashboards: cite the job, run, status, scope, and whether it applies to the current change.
- Documentation checks: cite the changed fact, docs searched, docs updated, and docs skipped.

When evidence is manual or visual, be specific enough that another agent can repeat the check.

## Freshness Checks

Before using evidence, ask:

- Was it gathered after the current change or review scope was known?
- Did any relevant file, generated artifact, dependency, configuration, test, or scope change afterward?
- Does the evidence cover the exact claim, or only a narrower one?
- Did the agent read the output or inspect the artifact, including failures, warnings, and skipped items?
- Is the evidence from a subagent or tool report that still needs main-agent sanity-checking?

If any answer weakens the proof, narrow the claim or report residual risk.

## Rationalization Counters

| Shortcut thought | Required replacement |
| --- | --- |
| "It passed earlier." | Treat earlier proof as context and gather fresh evidence for the current scope. |
| "This is only a docs change." | Verify the docs claim with source reads, diffs, link checks, rendered output, or explicit skipped-check notes. |
| "The subagent said it passed." | Inspect or reproduce important evidence before using it in the final claim. |
| "The linter passed, so it works." | Say only that the linter passed unless behavior or build proof was also gathered. |
| "I am confident." | Report the evidence that supports the claim or downgrade the wording. |
| "The check is expensive or unsafe." | Skip it explicitly with the reason and residual risk; do not imply it passed. |
| "No output means success." | Confirm the command exit status or tool convention before claiming success. |

## Verification Summary Pressure Scenarios

Use these scenarios to check whether the skill is changing agent behavior:

1. A test passed before the final edit. The correct summary treats it as stale for affected claims and reruns or downgrades.
2. A docs-only change has no test command. The correct summary cites source/diff/docs evidence and clearly lists skipped command checks.
3. A subagent reports success. The correct summary cites the main-agent diff, artifact, or command sanity check before accepting the report.
4. A check fails or cannot run. The correct summary says `failed` or `partially verified`, names the failure or skip reason, and avoids completion wording.
