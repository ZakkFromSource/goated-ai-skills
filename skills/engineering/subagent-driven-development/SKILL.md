---
name: subagent-driven-development
description: Use when an implementation plan or scoped task can benefit from fresh implementer and reviewer agents while the main agent keeps ownership of integration and final claims.
metadata:
  goated-category: engineering
---

# Subagent-Driven Development

## Purpose

Use fresh implementer and reviewer agents for implementation tasks without losing main-agent ownership.

This skill is for scoped implementation work that has a plan, a clear task split, and reviewable evidence. It helps the main agent coordinate delegated work, inspect what came back, resolve conflicts, and make honest final claims. Subagents can accelerate work, but they do not own the product decision, integration judgment, or user communication.

Keep the GOATED quality bar visible during delegation: prefer vertical behavior slices, tests through public interfaces, and deep modules with small meaningful interfaces. Do not create shallow pass-through abstractions or horizontal layer batches just because they are easy to delegate.

## Inputs

- User request, approved issue, implementation plan, PRD slice, ticket, prototype verdict, or scoped behavior change.
- Target-project root, applicable project instructions, current working-tree state, and known safety constraints.
- Task list with dependencies, likely edit areas, public interfaces, test surfaces, commands, and documentation surfaces.
- User or project rules about subagents, write ownership, commits, branches, worktrees, review gates, or final closeout.
- Available subagent, review, command, and verification capabilities.

## Dependencies

Hard: None.

Soft:
- writing-plans before delegation when an approved issue or task needs an executable plan
- grill-with-docs when behavior, scope, intent, language, or review constraints are unclear
- prototype when risky implementation choices need disposable evidence before delegation
- plan-codebase-architecture when module, interface, dependency, or architecture strategy is unsettled
- tdd when delegated work changes behavior, public interfaces, regressions, or testable workflows
- code-refinement after delegated implementation as a run-or-explicit-skip gate for non-trivial code-producing work before review gates
- standards-and-spec-review for spec fit, acceptance coverage, and project standards after delegated work
- code-security-review when delegated work touches trust boundaries, auth, permissions, user data, persistence, execution, or unsafe config
- doc-sync after delegated behavior, interface, architecture, standard, config, test, or doc changes
- verification-before-completion before complete/correct/passing/review-ready/lifecycle-ready delegated-work claims

Fallback: If subagents, companion skills, commands, or review tools are unavailable, run implementation and review phases sequentially, mark unavailable evidence, and avoid unsupported completion claims.

## Workflow

1. Confirm delegation is appropriate:
   - Start from a scoped implementation plan or approved task. If the work is not clear enough to delegate, route to `writing-plans`, `grill-with-docs`, `prototype`, or `plan-codebase-architecture` first.
   - Split only tasks that can be owned independently. Avoid parallel implementation when write scopes overlap, task order is uncertain, or one task's result defines another task's interface.
   - Keep tightly coupled, architecture-sensitive, or high-risk integration work with the main agent unless a subagent has a sharply bounded role.

2. Prepare the task board:
   - List each task, owner, allowed write scope, dependencies, expected evidence, and review path.
   - Choose sequential order for dependent tasks and parallel dispatch only for genuinely independent scopes.
   - Name the single-agent fallback for each task: the main agent performs the same implement, spec review, quality review, final review, and verification steps sequentially.
   - Before dispatching an implementer, read [Implementer Prompt](references/implementer-prompt.md) and fill in the scoped context.

3. Dispatch a fresh implementer per task:
   - Give the implementer only the task, relevant context, allowed write scope, commands, constraints, and expected output it needs.
   - State that other agents or the main agent may be editing elsewhere, and the implementer must not revert unrelated changes.
   - Require the implementer to return `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED` with changed paths, commands run or skipped, test results, assumptions, and concerns.
   - Do not require subagents to commit, use a specific branch model, worktree tool, task command, or agent product unless the user or project explicitly requires it.

4. Handle implementer status:
   - `DONE`: inspect changed paths and evidence, then run spec review.
   - `DONE_WITH_CONCERNS`: inspect the concern before review or final claims; fix, re-dispatch, or carry explicit residual risk.
   - `NEEDS_CONTEXT`: provide the missing scope, source path, command, fixture, product decision, or project rule; re-dispatch or continue sequentially.
   - `BLOCKED`: narrow the task, change model or tooling, split the task, revise the plan, or stop and ask the user when the blocker is a real product decision.

5. Review each task before moving on:
   - Run **spec review** first: compare the actual changed files to the requested task, acceptance criteria, and planned scope. Missing requirements and unrequested behavior must be resolved before quality review.
   - Run **quality review** second: inspect maintainability, behavior proof, tests through public interfaces, deep-module fit, integration risk, and local standards.
   - Use [Reviewer Prompt](references/reviewer-prompt.md) for spec, quality, and final review modes, or perform the same review sequentially when subagents are unavailable.
   - If a reviewer finds blocking issues, send a focused fix request to the implementer or fix sequentially, then re-review the affected mode.

6. Handle reviewer status:
   - `DONE`: integrate the review evidence after checking important findings, then continue.
   - `DONE_WITH_CONCERNS`: inspect concerns about evidence, scope, severity, or skipped checks before proceeding.
   - `NEEDS_CONTEXT`: provide the missing diff, spec, standards source, command output, or expected behavior, then re-dispatch or review sequentially.
   - `BLOCKED`: narrow the review scope, fix missing evidence, route to the right review skill, or stop before making completion claims.

7. Integrate deliberately:
   - The main agent inspects diffs, reconciles conflicts, validates that delegated changes work together, and resolves any disagreement between implementer and reviewer reports.
   - Run relevant focused commands or source checks after integration. Treat subagent reports as evidence leads until important evidence is inspected or reproduced.
   - Keep scope disciplined. If integration reveals a new product decision, architecture decision, or broader follow-up, stop or split it rather than quietly expanding the current task.

8. Run final review and closeout:
   - After all task-level reviews pass or residual risks are accepted, run a **final review** over the combined change for issue fit, standards, integration, docs, and security-sensitive paths when relevant.
   - Use `code-refinement` as a run-or-explicit-skip gate for non-trivial code-producing work, then `standards-and-spec-review`, `code-security-review`, and `doc-sync` according to the change surface.
   - Use `verification-before-completion` before claiming delegated work is complete, correct, passing, review-ready, documentation-synced, or ready for lifecycle movement.

## Output Contract

During or after delegated development, report:

- Task split: tasks, dependencies, write ownership, and sequential fallback.
- Delegated work: implementer status, changed paths, commands run or skipped, test results, assumptions, and concerns.
- Review evidence: spec review result, quality review result, final review result, findings fixed or accepted, and reviewer evidence inspected.
- Integration notes: conflicts, main-agent decisions, cross-task checks, and scope changes avoided or split out.
- GOATED quality notes: vertical slice preserved, public-interface proof used or skipped, deep-module impact, and shallow-abstraction risks.
- Closeout: verification evidence, docs/security/review routing, skipped checks, residual risk, and the final claim allowed by evidence.

## Delegation

Main owns task selection, write-scope boundaries, dispatch prompts, integration, conflict resolution, status decisions, final verification, and user communication.

Delegate only lifecycle work with clear ownership: fresh implementation, task or combined-change spec review, quality review, final review of issue fit/integration/docs/residual risk, or verification that gathers evidence without taking over the final claim.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths inspected or changed; commands run or skipped with results; tests or behavior proof when relevant; assumptions, concerns, skipped evidence, residual risk, confidence; and recommendation, not an unsupervised final claim.

Status handling lives in the workflow lifecycle: `DONE` triggers inspection and review; `DONE_WITH_CONCERNS` requires concern resolution; `NEEDS_CONTEXT` gets missing scope/source/command/evidence before re-dispatch or local continuation; `BLOCKED` narrows, splits, replans, changes tooling, or stops for a real product decision.

If subagents are unavailable, run the same work sequentially with a narrower context budget and keep the evidence, review, and verification gates.

## Guardrails

- Do not delegate implementation before the task, allowed write scope, expected evidence, and review path are clear.
- Do not dispatch parallel implementers to overlapping files, shared interfaces, or dependent tasks unless the dependency is already settled.
- Do not let implementers decide broad architecture, product scope, public contracts, migrations, or security posture unless the task explicitly delegates that decision and review covers it.
- Do not accept `DONE` as proof. Inspect or reproduce important evidence before relying on delegated work.
- Do not skip spec review, quality review, final review, or `verification-before-completion` because a subagent sounded confident.
- Do not require commits, branches, worktrees, issue movement, PRs, task-tool syntax, model names, or framework-specific commands unless the target project or user requires them.
- Do not copy source-repo instructions, local research paths, hidden chat history, or private scratch notes into installed-skill requirements.
- Do not include private names, credentials, client data, sensitive personal context, ignored scratch content, or real user data in prompts or reports.
- Do not make this skill depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local/`, or upstream inspiration after installation.

## References

Linked support files, use at the workflow gates above: [Implementer Prompt](references/implementer-prompt.md) and [Reviewer Prompt](references/reviewer-prompt.md).
