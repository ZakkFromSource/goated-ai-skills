---
name: subagent-driven-development
category: engineering
classification: portable
status: wip
description: Use when an implementation plan or scoped task can benefit from fresh implementer and reviewer agents while the main agent keeps ownership of integration and final claims.
triggers:
  - user asks to use subagents, parallel agents, delegated implementation, fresh implementers, or reviewer agents for implementation work
  - a scoped implementation plan has independent tasks that can be delegated with clear write ownership
  - larger, riskier, or review-heavy implementation needs evidence-backed subagent work
  - an agent needs a single-agent-compatible fallback for delegated development
  - completed delegated work needs spec review, quality review, final review, and verified closeout
outputs:
  - task split with owned write scopes, dependency order, and sequential fallback path
  - implementer dispatch prompts with scoped context, expected evidence, and allowed changes
  - delegated status handling for DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, and BLOCKED
  - spec review, quality review, and final review evidence before completion claims
  - main-agent integration notes, conflict decisions, verification summary, and residual risk
depends_on:
  hard: []
  soft:
    - writing-plans before delegated development when an approved issue or scoped task needs an executable plan
    - grill-with-docs when behavior, scope, product intent, project language, or review constraints are unclear
    - prototype when a risky implementation choice needs disposable evidence before delegation
    - plan-codebase-architecture when module, interface, dependency, or architecture strategy is unsettled
    - tdd when delegated work changes behavior, public interfaces, regressions, or testable workflows
    - standards-and-spec-review for spec fit, acceptance coverage, and project standards after delegated work
    - code-security-review when delegated work touches trust boundaries, auth, permissions, user data, persistence, execution, or unsafe configuration
    - doc-sync after behavior, interfaces, architecture, standards, configuration, tests, or docs may have changed
    - verification-before-completion before claiming delegated work is complete, correct, passing, review-ready, or ready for lifecycle movement
  fallback: If subagents, companion skills, runnable commands, or review tools are unavailable, run the same implementation and review phases sequentially with narrower scope, mark unavailable evidence, and avoid unsupported completion claims.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
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
   - Use [Reviewer Prompt](references/reviewer-prompt.md) for both review modes, or perform the same review sequentially when subagents are unavailable.
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
   - Use `standards-and-spec-review`, `code-security-review`, and `doc-sync` according to the change surface.
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

The main agent owns task selection, write-scope boundaries, dispatch prompts, integration, conflict resolution, status decisions, final verification, and user communication.

When subagents are available, use them for:

- fresh implementation of one clearly owned task;
- spec review of a task or combined change;
- quality review of a task or combined change;
- final review of issue fit, integration, docs, and residual risk;
- verification passes that can gather independent evidence without taking over the final claim.

Require every delegated result to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- paths inspected or changed;
- commands run or deliberately skipped, with results;
- test results or other behavior proof when relevant;
- assumptions, concerns, skipped evidence, residual risk, and confidence;
- recommendation for the main agent, not an unsupervised final claim.

If subagents are unavailable, perform the same work sequentially with a narrower context budget and keep the same evidence, review, and verification gates.

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

- [Implementer Prompt](references/implementer-prompt.md) - use before dispatching a fresh implementer for a scoped task.
- [Reviewer Prompt](references/reviewer-prompt.md) - use for spec, quality, and final review modes.
