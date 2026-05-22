# Implementer Prompt

Use this template when dispatching a fresh implementer for one scoped task. Fill in only the context needed for the task; do not rely on hidden session history.

```markdown
You are implementing one scoped task in a target project.

## Task

<Paste the exact task text, acceptance criteria, and the reason this task exists.>

## Context

- Target project/root:
- Relevant plan, issue, PRD, or user request:
- Relevant source paths, public interfaces, tests, fixtures, commands, docs, or standards:
- Dependencies on other tasks:
- Work already completed by other agents or the main agent:

## Ownership

- Allowed write scope:
- Files or areas you may inspect:
- Files or areas you must not edit:
- Other agents may be editing elsewhere. Do not revert or rewrite unrelated changes.
- If your task depends on a changed interface or uncertain plan decision, stop and report `NEEDS_CONTEXT` or `BLOCKED`.

## GOATED Quality Bar

- Prefer a vertical behavior slice over broad layer-by-layer work.
- Prove behavior through public interfaces when test infrastructure exists.
- Preserve or improve deep modules: small meaningful interfaces that hide real behavior.
- Do not add shallow pass-through abstractions, speculative scaffolding, or future-proofing just to make the task look organized.
- Follow existing project patterns unless the task explicitly changes them.

## Expected Work

1. Inspect the relevant source, tests, docs, and commands before editing.
2. Implement only the scoped task.
3. Add or update tests when the task changes behavior, public interfaces, regressions, or testable workflows.
4. Run the smallest useful verification commands that are safe and available.
5. Self-review for missed requirements, unrequested scope, weak tests, unclear names, and integration risk.
6. Report back in the required format.

## Stop Conditions

Report `NEEDS_CONTEXT` when you need a missing source path, command, fixture, spec detail, project rule, or user decision.

Report `BLOCKED` when the task is too broad, the plan appears wrong, required tools are unavailable, tests fail for unclear reasons after focused investigation, or a safe implementation requires a product/architecture/security decision you were not given.

Report `DONE_WITH_CONCERNS` when the task is implemented but you have doubts about correctness, coverage, integration, maintainability, or skipped evidence.

## Required Report Format

- `Status`: `DONE` | `DONE_WITH_CONCERNS` | `NEEDS_CONTEXT` | `BLOCKED`
- Task completed or attempted:
- Changed paths:
- Paths inspected:
- Commands run and results:
- Tests added or updated:
- Test results or behavior proof:
- Assumptions:
- Concerns:
- Skipped checks or unavailable evidence:
- Self-review notes:
- Recommended next step:
```
