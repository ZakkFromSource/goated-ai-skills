---
name: writing-plans
category: engineering
classification: portable
status: wip
description: Use when an approved issue, scoped task, PRD slice, or implementation request needs a just-in-time executable plan before code, docs, or configuration changes.
triggers:
  - user asks for an implementation plan, execution plan, task plan, step-by-step plan, or plan before implementation
  - an approved local issue, PRD slice, ticket, or scoped task is ready to become exact implementation steps
  - a future agent needs enough source-grounded detail to implement without relying on hidden chat history
  - durable issue handoffs should stay concise while volatile commands, file paths, snippets, and expected evidence need just-in-time detail
  - implementation must be routed to TDD, delegated development, or direct execution based on size and risk
outputs:
  - source-grounded implementation plan written inline by default or under an ignored local path for long or resumable work
  - exact files or source areas to inspect or edit, commands to run, expected evidence, and stop conditions
  - slice shape: the smallest useful vertical behavior path, narrow foundation with rationale, or explicit non-vertical reason
  - module/interface focus when relevant: the deep module, public interface, seam, or test surface the slice protects
  - TDD steps when behavior, regressions, public interfaces, or testable implementation are involved
  - implementation route: direct execution, tdd, or subagent-driven-development with fallback
  - review, doc-sync, verification, and residual-risk closeout steps
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before planning work in an unfamiliar target project
    - grill-with-docs when scope, artifact policy, success criteria, or tradeoffs are unclear
    - prd-to-issues when a scoped PRD still needs durable issue handoffs before implementation planning
    - prototype when a risky implementation choice needs disposable evidence before exact steps are written
    - plan-codebase-architecture when module, interface, dependency, or architecture strategy is not settled enough to plan implementation
    - tdd when the implementation changes behavior, public interfaces, regressions, or testable workflows
    - subagent-driven-development for larger, riskier, or parallelizable implementation when available
    - standards-and-spec-review after implementation when issue fit, acceptance coverage, or project standards need review
    - code-security-review after implementation when trust boundaries, auth, user data, persistence, execution, or unsafe configuration may be affected
    - doc-sync after behavior, interfaces, architecture, standards, configuration, tests, or docs may have changed
    - verification-before-completion before claiming the plan, implementation route, or closeout is complete or ready
  fallback: If companion skills, project docs, runnable commands, subagents, or source evidence are unavailable, inspect the smallest relevant local evidence, keep the plan narrower, mark assumptions and residual risk, and avoid exact claims that cannot be verified.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Writing Plans

## Purpose

Turn approved work into an executable implementation plan immediately before implementation.

Use this skill after intent is scoped enough to act, but before editing. The plan should be fresh, source-grounded, and useful to a new agent or engineer without hidden session history. It should name exact paths, commands, evidence, stop conditions, and closeout gates only after inspecting the current project.

This skill keeps durable issues concise. Issues, PRDs, tickets, and roadmap notes should carry stable intent, acceptance criteria, blockers, and source links. Volatile details such as exact file paths, local commands, expected failures, implementation order, and verification evidence belong in a just-in-time plan.

## Inputs

- Approved issue, PRD slice, ticket, scoped user request, accepted architecture plan, prototype verdict, or review finding.
- Target-project root path and current working-tree state when available.
- Relevant project docs, local issue handoffs, standards, context artifacts, ADRs, source files, tests, schemas, commands, and previous verification evidence.
- User constraints about plan location, tracked versus local artifacts, implementation route, risk tolerance, subagent use, or required closeout.
- Known unavailable tools, skipped evidence, blockers, or decisions that must not be guessed.

## Workflow

1. Confirm the planning target:
   - Identify the exact issue, PRD slice, ticket, request, or approved artifact being converted into a plan.
   - Confirm it is ready for implementation planning. If the work is not scoped, route to `grill-with-docs`, `write-a-prd`, `prd-to-issues`, `prototype`, or `plan-codebase-architecture` instead of writing an assumption-heavy plan.
   - Check that the target is small enough to implement as one focused vertical slice. If it is broad, narrow the plan to the first user-verifiable tracer bullet and defer the rest, or route back to `prd-to-issues`.
   - Separate durable requirements from volatile execution details.

2. Choose the plan artifact:
   - Default to an inline plan in chat.
   - Use an ignored local path such as `.local/plans/YYYY-MM-DD-short-title.md` only when the plan is long, resumable, or useful for multi-step local coordination.
   - Create tracked plan files only when the user explicitly asks or the target project has a clear tracked-plan convention.
   - Do not hide required implementation context in ignored files if a future agent will need it; summarize any local plan in the chat or durable handoff when needed.

3. Inspect before writing exact steps:
   - Read the originating artifact and the smallest useful current source, test, docs, config, or schema evidence.
   - Discover likely edit paths, public interfaces, test surfaces, commands, and documentation surfaces from the project itself.
   - Do not write exact file paths, commands, snippets, expected failures, expected outputs, or review claims before this inspection.
   - If multiple plausible paths remain after inspection and the choice changes behavior or risk, ask the user or narrow the plan to the verified path.

4. Pick the execution route:
   - Use **direct execution** for tiny, low-risk, docs-only, mechanical, or obvious changes.
   - Use **`tdd`** for behavior changes, bug fixes, regressions, public interfaces, module seams, or any implementation that should be proven by tests.
   - Use **`subagent-driven-development`** for larger, risky, review-heavy, or parallelizable work when that skill and subagents are available.
   - If `subagent-driven-development` is unavailable, keep the plan single-agent-compatible and split work into sequential checkpoints with review gates.

5. Write executable steps:
   - Name exact files or source areas to inspect or edit, and why each matters.
   - When behavior is involved, start with the smallest end-to-end behavior path that can be proved through a public interface.
   - Avoid layer-by-layer batches such as schema-only, API-only, UI-only, or tests-only work unless they are narrow foundations with a named dependent slice and concrete verification.
   - When module shape matters, name the deep module, public interface, seam, or test surface the plan is preserving or improving.
   - Name the command or manual check for each meaningful proof step, plus the evidence expected from it.
   - For TDD work, include red, green, refactor, and rerun checkpoints rather than a single bulk test phase.
   - Include review steps: standards/spec review, security review when relevant, documentation sync, and final verification.
   - Include stop conditions for missing source evidence, unexpected test results, broad scope drift, unsafe commands, unclear product choices, or repeated verification failures.
   - Keep steps ordered so each one produces evidence needed by the next.

6. Review the plan before execution:
   - Read [Plan Review Checklist](references/plan-review-checklist.md) for non-trivial, risky, delegated, or resumable plans.
   - Check that every acceptance criterion has a planned proof path.
   - Remove placeholders, vague verbs, stale assumptions, and broad "do the rest" language.
   - Make the plan no more detailed than the work needs. Tiny tasks can use a short inline checklist.

7. Execute or hand off:
   - If the user asked for implementation and the plan is ready, proceed through the chosen route.
   - If the user asked only for a plan, stop after the plan and state assumptions, skipped inspection, and residual risk.
   - If another agent or future session will execute it, include enough source links, current-state evidence, commands, and stop conditions to avoid depending on hidden chat history.

## Output Contract

For most work, return a compact plan shaped like this:

```markdown
## Implementation Plan

- Plan target: <issue, PRD slice, ticket, or request>
- Plan location: <inline | .local/plans/... | tracked path requested by user>
- Source inspected: <paths, commands, docs, tests, schemas, and skipped evidence if any>
- Execution route: <direct execution | tdd | subagent-driven-development | sequential fallback>
- Slice shape: <smallest vertical behavior path | narrow foundation with rationale | not vertical because...>
- Module/interface focus: <public interface, deep module, seam, test surface, or "not architecture-relevant">
- Assumptions: <verified assumptions or "None">
- Stop conditions: <conditions that should pause execution>

### Steps

1. <Inspect/edit/run step with exact path or command and expected evidence>
2. <Next step>
3. <Review/doc-sync/verification closeout step>

### Residual Risk

- <skipped evidence, unavailable commands, unclear product choices, or "Low">
```

For tiny tasks, a shorter inline checklist is acceptable if it still names the target, route, evidence, and closeout.

For local plan files, include the same sections in the file and summarize the plan location, route, assumptions, and next step in chat.

## Delegation

The main agent owns the planning target, artifact policy, execution route, final plan quality, and user communication.

When subagents are available, use them for bounded evidence or review passes, such as:

- finding likely edit paths, public interfaces, test surfaces, or commands for one source area;
- checking whether a proposed plan covers all acceptance criteria;
- reviewing a plan for placeholders, stale assumptions, unsafe commands, or missing evidence;
- identifying documentation, standards, security, or verification surfaces for closeout;
- stress-testing whether work should route to direct execution, `tdd`, or delegated development.

Require delegated planning results to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- paths, docs, commands, tests, schemas, or artifacts inspected;
- exact evidence found and skipped evidence with reasons;
- assumptions, residual risk, and confidence;
- recommended plan changes, not unsupervised final publication.

Handle delegated status this way: `DONE` means integrate evidence into the plan; `DONE_WITH_CONCERNS` means inspect concerns before execution; `NEEDS_CONTEXT` means provide the missing artifact, scope, source path, command, or user decision and re-dispatch or verify locally; `BLOCKED` means narrow the plan, route to clarification, or stop before implementation.

If subagents are unavailable, perform the same checks sequentially with a smaller context budget.

## Guardrails

- Do not write exact file paths, commands, snippets, expected outputs, or expected failures before current source inspection.
- Do not turn durable issues into stale implementation transcripts. Keep stable intent in issues and volatile execution detail in just-in-time plans.
- Do not create tracked plan files unless the user explicitly asks or the target project convention requires them.
- Do not rely on ignored `.local/` plans as the only place a future agent can recover important context.
- Do not turn a broad issue or PRD slice into a broad implementation plan. Narrow to the first user-verifiable vertical slice or route back to issue breakdown.
- Do not plan horizontal layer batches, broad setup, speculative scaffolding, or multi-behavior milestones unless a narrow foundation is required, named, and verifiable.
- Do not create shallow pass-through abstractions when a deeper module, smaller public interface, or clearer test surface would keep behavior local.
- Do not use placeholders such as `TODO`, "handle edge cases", "write tests", "etc.", "similar to above", or "finish implementation" as executable steps.
- Do not skip TDD planning for behavior changes just because the edit looks small.
- Do not route to subagents in a way that makes the main agent lose ownership of integration, review, or final claims.
- Do not prescribe branch, worktree, commit, PR, issue tracker, or agent-tool mechanics unless the target project or user request provides them.
- Do not include private notes, credentials, client data, sensitive personal context, ignored scratch content, or real user data in tracked plans.
- Do not require this source repo's root files, issue files, `.local/` research, or chat history after installation. The skill may rely only on its own files and target-project evidence.

## References

- [Plan Review Checklist](references/plan-review-checklist.md) - read before executing non-trivial, risky, delegated, resumable, or local-file plans.
