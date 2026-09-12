---
name: code-refinement
description: Use when explicitly asked to simplify or refactor code, or when concrete refinement debt is observed in a recent change and behavior must stay stable.
metadata:
  goated-category: engineering
---

# Code Refinement

## Purpose

Refine recently changed target-project code without changing behavior. Activate
this full workflow only for an explicit cleanup request or concrete refinement
debt: confusing names, duplication, excessive branching, unnecessary
abstraction, shallow indirection, difficult local reasoning, or substantially
generated or agent-written code that exhibits those problems. Ordinary
readability review and TDD's local refactor-after-green do not require this
skill.

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
- review-codebase-architecture when cleanup pressure reveals broad architecture friction, shallow modules, false seams, or hard-to-test design
- design-codebase-architecture when a public interface, module boundary, dependency seam, file ownership, or migration strategy should change
- standards-and-spec-review after refinement when issue fit, acceptance coverage, or project standards need review
- code-security-review after refinement when trust boundaries, auth, permissions, user data, persistence, unsafe execution, or dependency behavior are touched
- doc-sync when refinement changes public names, docs-relevant examples, commands, tests, or reports possible documentation drift
- verification-before-completion before claiming behavior was preserved, checks pass, code is refined, docs are synced, or the change is ready

Fallback: If companion skills, tests, commands, or clean diffs are unavailable, limit edits to low-risk clarity changes, propose first when risk is material, and report the weaker proof and residual risk.

## Workflow

1. Confirm activation and scope:
   - Activate for explicit requests such as "clean this up", "simplify this diff", "make this easier to read", or "refactor this without behavior changes".
   - Otherwise activate only after naming concrete debt in the scoped change. Substantially generated or agent-written code qualifies when focused review finds awkwardness or difficult local reasoning; its origin alone is not debt.
   - If there is no explicit request or concrete debt, return to the current workflow without loading this skill or producing a formal skip report.
   - Identify the target-project root and the refinement scope: current diff, staged diff, task-touched files, explicit user paths, or supplied patch.
   - Inspect working-tree state before editing. If files contain unrelated user-authored changes mixed with the refinement scope, edit around them carefully or propose changes first.
   - Do not expand from a known scope into nearby cleanup unless the user explicitly approves the broader scope.

2. Choose edit mode or proposal mode:
   - Use **edit mode** when current authorization covers local, reversible changes, relevant proof is available or discoverable, and public interfaces are preserved. Preserve separable user-authored edits in the same file.
   - Use **proposal mode** when a material choice remains unresolved: scope is unclear, user changes cannot be separated safely, proof cannot support the proposed edit, or an interface or module-boundary change is not authorized. Subjective cleanup or a mixed file alone does not require a new approval.
   - In proposal mode, gather available safe evidence and return candidates with benefit, risk, and proof needed. Pause only the affected mutation until the decision or authorization is resolved; reuse covering consent and continue independent authorized work.

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
   - Route to `review-codebase-architecture` when repeated refinement friction suggests broad architecture opportunities.
   - Route to `design-codebase-architecture` when a better design would change public interfaces, module ownership, dependency seams, file structure, migration strategy, or multiple callers.
   - Route to `tdd` when the desired cleanup needs behavior changes, new tests, regression coverage, or public-interface proof.
   - Route to `doc-sync` when public names, examples, commands, workflows, or docs-relevant tests changed or when drift is suspected.
   - Route to `code-security-review` when the refinement touches security-relevant code paths.

7. Verify and close the refinement:
   - Rerun focused checks that match the refined scope. Run broader nearby checks when the local proof is too narrow for the risk.
   - Review the final diff for accidental behavior changes, unrelated churn, public-interface changes, weakened tests, and docs drift.
   - Use `verification-before-completion` before saying behavior was preserved, checks pass, refinement is done, or the change is ready for review.
   - Return a compact refinement delta: result, changed paths, proof, material
     interface/docs/security impact, deferred work, and residual risk.
   - Omit empty fields and repeated paths/checks. Do not produce a competing
     task closeout.

## Output Contract

In integrated use, return only material fields from this delta:

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
```

After proposal mode, return only the reason for not editing, useful candidates,
proof needed, and next step. Make the proposal-only claim explicit.

```markdown
## Code Refinement Proposal

- Scope: <requested or inferred scope>
- Why not editing yet: <unresolved scope, inseparable user edits, inadequate proof, or an unauthorized interface change>
- Candidate refinements: <one bullet per candidate with benefit and risk>
- Proof needed: <tests/checks/manual verification before/after>
- Recommended next step: <approve narrowed edits, route to TDD, route to architecture, or skip>
- Closeout claim: <proposal-only claim, such as no files changed and behavior preservation not verified>
```

## Delegation

Main owns scope, worktree judgment, mode, edits, proof interpretation, and
communication. Delegate only bounded read-only diff, behavior-risk, mixed-work,
style, proof-strength, or churn review unless a larger workflow assigns writes.

Return paths, commands, candidate benefit/risk, drift or interface concerns,
mixed-change warnings, assumptions, confidence, status, and next action.
Resolve concerns or missing context before editing; use proposal mode or stop
on `BLOCKED`. Without delegation, review sequentially.

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
- Do not hide changed interfaces, skipped proof, failures, or residual risk.
- Omit empty or non-material fields unless omission would mislead.
- Do not claim code was refined after proposal mode; say proposal-only when no refinement edits were made.
- Do not replace `tdd`, `review-codebase-architecture`, `standards-and-spec-review`, `code-security-review`, `doc-sync`, or `verification-before-completion`.
- Do not include private notes, ignored scratch content, credentials, client data, sensitive personal context, secrets, or real user data in reports or examples.
- Do not require this source repo's root files, issue files, `.local` notes, or hidden chat history after installation. The skill may rely only on its own instructions, local support files, and target-project evidence.

## References

Linked support file, read at the workflow gate above: [Refinement Patterns](references/refinement-patterns.md).
