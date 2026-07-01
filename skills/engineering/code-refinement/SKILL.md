---
name: code-refinement
description: Use after implementation or when asked to simplify, clean up, or refactor recently changed code while preserving behavior and avoiding unrelated churn.
metadata:
  goated-category: engineering
---

# Code Refinement

## Purpose

Refine recently changed target-project code without changing behavior. Use this as a scoped post-change pass after implementation, generated code, or TDD green evidence, and before standards/spec review, security review when relevant, doc sync, and final verification. For non-trivial code-producing delivery work, treat this skill as a default run-or-explicit-skip closeout gate.

This skill optimizes in this order:

1. Preserve behavior.
2. Improve readability and local reasoning.
3. Reduce duplication, unnecessary branches, and repeated setup.
4. Remove needless abstraction only when clarity improves.
5. Reduce line count only when the result is also clearer.

It is not a broad architecture scan, generic code review, standards review, security audit, or documentation sync. It edits code only inside a known scope and routes larger design or proof questions to companion skills.

## Inputs

- User request, implementation summary, accepted issue, PRD slice, plan, review note, or TDD evidence.
- Target-project root and current working-tree state.
- Scoped change set: current diff, staged changes, task-touched files, explicit user paths, or a narrow patch.
- Relevant source files, tests, fixtures, commands, linters, formatters, snapshots, generated-file conventions, and nearby style examples.
- Existing project standards, root context docs, agent instructions, ADRs, and public-interface docs when they affect naming, style, proof, or allowed scope.
- Known user-authored changes, skipped checks, weak test infrastructure, or files that must not be touched.

## Dependencies

Hard: None.

Soft:
- tdd when behavior, regression coverage, public interfaces, or a red/green/refactor loop is still needed
- improve-codebase-architecture when cleanup pressure reveals broad architecture friction, shallow modules, false seams, or hard-to-test design
- plan-codebase-architecture when a public interface, module boundary, dependency seam, file ownership, or migration strategy should change
- standards-and-spec-review after refinement when issue fit, acceptance coverage, or project standards need review
- code-security-review after refinement when trust boundaries, auth, permissions, user data, persistence, unsafe execution, or dependency behavior are touched
- doc-sync when refinement changes public names, docs-relevant examples, commands, tests, or reports possible documentation drift
- verification-before-completion before claiming behavior was preserved, checks pass, code is refined, docs are synced, or the change is ready

Fallback: If companion skills, tests, commands, or clean diffs are unavailable, limit edits to low-risk clarity changes, propose first when risk is material, and report the weaker proof and residual risk.

## Workflow

1. Confirm activation and scope:
   - Use this skill for non-trivial post-change cleanup, generated or agent-written awkward code, recently changed code that should be simplified, or explicit requests such as "clean this up", "simplify this diff", "make this easier to read", or "refactor this without behavior changes".
   - For non-trivial code-producing delivery work, either run this skill or explicitly skip it with a short reason before moving to later review gates.
   - Skip this skill for tiny mechanical edits, generated files that should not be hand-edited, docs-only changes, formatting-only changes, no meaningful refinement candidates, user override, and already-clear one-line fixes.
   - Identify the target-project root and the refinement scope: current diff, staged diff, task-touched files, explicit user paths, or supplied patch.
   - Inspect working-tree state before editing. If files contain unrelated user-authored changes mixed with the refinement scope, edit around them carefully or propose changes first.
   - Do not expand from a known scope into nearby cleanup unless the user explicitly approves the broader scope.

2. Choose edit mode or proposal mode:
   - Use **edit mode** when scope is explicit, relevant proof is available or discoverable, changes are local, and public interfaces are not affected.
   - Use **proposal mode** when the request is broad, proof is weak, user-authored changes are mixed in, public interfaces or module boundaries might be affected, the cleanup is subjective, or the safest next step is user selection.
   - In proposal mode, return candidate refinements with evidence, expected benefit, risk, and proof needed. Do not mutate files until the user approves or narrows the scope.

3. Establish behavior-preservation proof:
   - Prefer green focused tests, type checks, lint, format, snapshot checks, visual/manual checks, or other project-defined commands that already protect the changed behavior.
   - For non-trivial refinement edits, capture pre-refinement evidence before editing when feasible, then rerun the same focused checks afterward.
   - If no useful proof exists, name the desired proof, explain why it is unavailable, keep edits smaller, and do not claim behavior preservation beyond what was checked.
   - If behavior should change or new behavior coverage is needed, route to `tdd` instead of using this skill as a shortcut.

4. Read local patterns before changing code:
   - Inspect nearby source and tests for naming, structure, helper shape, error handling, comments, markup, CSS organization, and fixture style.
   - Prefer local project conventions over generic preferences.
   - Read [Refinement Patterns](references/refinement-patterns.md) when choosing cleanup moves, resisting clever compactness, or evaluating Python, HTML, CSS, test, comment, duplication, branch, helper, or markup/style refinements.

5. Refine in small reversible moves:
   - Improve names, grouping, branch structure, duplication, local helpers, comments, test setup, markup, and style organization only when behavior and readability are preserved.
   - Keep public APIs, routes, schemas, file/module ownership, dependency seams, and architecture boundaries stable by default.
   - Do not collapse explicit logic into dense expressions, nested ternaries, clever chaining, or line-count-driven rewrites.
   - Do not delete tests, weaken assertions, or hide behavior proof. Test cleanup is allowed only when coverage remains equivalent or clearer through the same public interface.
   - After each meaningful refinement step, rerun the smallest useful proof when the project makes that practical.

6. Route larger findings instead of smuggling them into cleanup:
   - Route to `improve-codebase-architecture` when repeated refinement friction suggests broad architecture opportunities.
   - Route to `plan-codebase-architecture` when a better design would change public interfaces, module ownership, dependency seams, file structure, migration strategy, or multiple callers.
   - Route to `tdd` when the desired cleanup needs behavior changes, new tests, regression coverage, or public-interface proof.
   - Route to `doc-sync` when public names, examples, commands, workflows, or docs-relevant tests changed or when drift is suspected.
   - Route to `code-security-review` when the refinement touches security-relevant code paths.

7. Verify and close the refinement:
   - Rerun focused checks that match the refined scope. Run broader nearby checks when the local proof is too narrow for the risk.
   - Review the final diff for accidental behavior changes, unrelated churn, public-interface changes, weakened tests, and docs drift.
   - Use `verification-before-completion` before saying behavior was preserved, checks pass, refinement is done, or the change is ready for review.
   - Assemble the closeout packet before the final response. The wording may be compact or natural, but every required Output Contract field must be accounted for with a value, `None`, `not applicable`, or a short fallback reason.
   - Report skipped checks, known weak proof, deferred architecture opportunities, docs follow-up, and residual risk.
   - Include a compact contract-coverage line and the narrowest closeout claim allowed by the evidence.

## Output Contract

After edit mode, report all required fields below. The final response may use compact or natural wording, but it must account for each field. Do not omit a field because it feels obvious; use `None`, `not applicable`, or a short fallback reason when needed.

```markdown
## Code Refinement

- Scope: <current diff, touched files, explicit paths, or patch>
- Mode: edit
- Pre-refinement proof: <commands/checks/source evidence, or fallback reason>
- Refinements made: <readability, duplication, branch, helper, test, comment, markup, or style changes>
- Public interface impact: <none, or routed concern>
- Tests/proof rerun: <commands/checks and results>
- Docs/security follow-up: <none, routed to doc-sync/code-security-review, or residual risk>
- Deferred candidates: <architecture/TDD/standards follow-up, or none>
- Residual risk: <skipped checks, weak proof, mixed user changes, or low>
- Closeout claim: <narrow claim allowed by verification-before-completion>
- Contract coverage: <all required fields accounted for, or incomplete - missing fields/reason>
```

After proposal mode, report all required fields below. Proposal mode is not an edit claim; make that explicit in the closeout claim.

```markdown
## Code Refinement Proposal

- Scope: <requested or inferred scope>
- Why not editing yet: <broad scope, weak proof, mixed changes, public interface risk, or subjective cleanup>
- Candidate refinements: <one bullet per candidate with benefit and risk>
- Proof needed: <tests/checks/manual verification before/after>
- Recommended next step: <approve narrowed edits, route to TDD, route to architecture, or skip>
- Closeout claim: <proposal-only claim, such as no files changed and behavior preservation not verified>
- Contract coverage: <all required fields accounted for, or incomplete - missing fields/reason>
```

When skipped as the regular closeout gate before edit or proposal mode, report a compact skip note:

```markdown
## Code Refinement Skip

- Scope: <changed files, current diff, explicit paths, or "not applicable">
- Skip reason: <tiny change, docs-only, generated file, no meaningful refinement candidate, user override, weak proof requiring later proposal, or other reason>
- Next gate: <standards/spec review, security review, doc-sync, verification-before-completion, or other next step>
- Contract coverage: skip reason accounted for; edit/proposal fields not applicable because refinement mode did not run
```

## Delegation

Main owns scope, dirty-worktree judgment, edit/proposal mode, final edits, proof interpretation, and user communication.

Delegate only bounded read-only review unless a larger workflow explicitly assigns writes: inspect the scoped diff for candidate refinements, identify behavior-drift risk, check mixed user changes, compare local style conventions, inspect test proof strength, or pressure-test the final diff for unrelated churn.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths inspected; commands run or skipped; candidate refinements with benefit/risk; behavior-drift concerns; public-interface concerns; mixed-change warnings; assumptions; confidence; and recommended next action.

Status handling: `DONE` integrates safe candidates; `DONE_WITH_CONCERNS` reviews risk before editing; `NEEDS_CONTEXT` gets missing scope, diff, test command, standard, or user decision; `BLOCKED` switches to proposal mode, routes to a companion skill, or reports the blocker.

If subagents are unavailable, run the same review sequentially with a narrower context budget.

## Guardrails

- Do not edit outside the current diff, task-touched files, explicit user paths, or approved scope.
- Do not rewrite unrelated user-authored dirty worktree changes.
- Do not change behavior, public APIs, schemas, routes, CLI contracts, module ownership, dependency seams, file structure, or migration strategy by default.
- Do not use "simpler" to mean fewer lines, denser expressions, clever one-liners, nested ternaries, or hidden control flow.
- Do not remove named concepts, domain language, or comments that explain invariants, business rules, security constraints, or surprising behavior just because the code still runs.
- Do not introduce abstractions that only move code around, hide one local branch, or make tests easier by leaking internals.
- Do not delete, weaken, or rewrite tests to match the refined implementation unless equivalent behavior proof remains through the public interface.
- Do not hand-edit generated files unless the project explicitly treats them as source.
- Do not claim behavior preservation from a clean diff alone. Use fresh proof or report weaker confidence.
- Do not replace the Output Contract with loose prose such as "cleaned up and tests pass"; final closeout must account for every required field or explicitly report the skip reason.
- Do not omit required Output Contract facts because the value is `None`, `not applicable`, or inconvenient. State the value or fallback reason.
- Do not claim code was refined after proposal mode or skip mode; say proposal-only or skipped when no refinement edits were made.
- Do not replace `tdd`, `improve-codebase-architecture`, `standards-and-spec-review`, `code-security-review`, `doc-sync`, or `verification-before-completion`.
- Do not include private notes, ignored scratch content, credentials, client data, sensitive personal context, secrets, or real user data in reports or examples.
- Do not require this source repo's root files, issue files, `.local` notes, or hidden chat history after installation. The skill may rely only on its own instructions, local support files, and target-project evidence.

## References

Linked support file, read at the workflow gate above: [Refinement Patterns](references/refinement-patterns.md).
