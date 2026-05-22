# Plan Review Checklist

Use this checklist before executing a non-trivial, risky, delegated, resumable, or local-file implementation plan.

## Source Grounding

- The plan names the approved issue, PRD slice, ticket, user request, or accepted artifact it implements.
- Current source, tests, docs, schemas, config, commands, or relevant artifacts were inspected before exact paths, commands, snippets, expected failures, or expected outputs were written.
- Exact paths and commands are based on the current target project, not hidden chat history or another repository's layout.
- Any uninspected but important source area is listed as skipped evidence with residual risk.

## Executability

- Each step has a clear action and expected evidence.
- Edit steps name the file, source area, interface, or artifact to change.
- Verification steps name the command, check, review, source read, rendered artifact, or manual evidence to inspect.
- Behavior changes include TDD red, green, refactor, and rerun checkpoints when test infrastructure exists or can be discovered.
- The plan includes stop conditions for missing evidence, unexpected failures, unsafe commands, unclear product choices, scope drift, and repeated verification failures.

## Scope And Route

- Durable issues remain concise; volatile local details stay in the just-in-time plan.
- The plan implements one focused vertical slice by default, or explains why a narrow foundation must come first.
- The plan avoids horizontal layer batches, broad setup, speculative scaffolding, and multi-behavior milestone steps.
- When architecture matters, the plan names the module, public interface, seam, or test surface involved and avoids shallow pass-through abstractions.
- The plan chooses one route: direct execution, `tdd`, or `subagent-driven-development` with fallback.
- Direct execution is limited to tiny, low-risk, docs-only, mechanical, or obvious work.
- Delegated work keeps the main agent responsible for orchestration, integration, review, and final claims.
- The plan avoids branch, worktree, commit, PR, issue tracker, or tool-specific requirements unless the target project or user request provides them.

## Review And Closeout

- Acceptance criteria or user-requested outcomes each have a planned proof path.
- Standards/spec review is included when issue fit, acceptance coverage, or project standards matter.
- Security review is included when trust boundaries, auth, permissions, user data, persistence, unsafe execution, or sensitive configuration may be affected.
- Doc sync is included when behavior, interfaces, architecture, standards, configuration, tests, or docs may change.
- Verification-before-completion is the final claim gate.
- Issue closure, archive moves, completion status edits, or similar lifecycle cleanup are absent unless acceptance evidence and any required review are explicitly planned first.

## Placeholder Sweep

Revise the plan before execution if it contains unsupported language such as:

- `TODO`
- `handle edge cases`
- `write tests`
- `finish implementation`
- `similar to above`
- `etc.`
- `make sure it works`
- broad instructions that do not name evidence

## Final Gate

Before execution, the plan should answer:

- What will change?
- Where will it change?
- How will behavior or correctness be proved?
- What should pause execution?
- What remains uncertain?
