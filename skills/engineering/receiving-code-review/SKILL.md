---
name: receiving-code-review
category: engineering
classification: portable
status: wip
description: Use when handling code review feedback, PR comments, reviewer suggestions, requested changes, or critique before deciding whether to clarify, push back, or implement.
triggers:
  - user asks to handle, address, apply, respond to, or work through code review feedback
  - a reviewer, maintainer, CI bot, teammate, or subagent provides comments, requested changes, or suggestions on a diff, PR, patch, issue, or implementation
  - review feedback is unclear, technically questionable, broad, conflicting, security-relevant, or likely to change behavior
  - an agent is about to implement review suggestions before verifying them against source, tests, specs, or project intent
  - accepted review feedback needs one-item-at-a-time implementation, verification, and closeout
outputs:
  - review feedback inventory with each item understood before editing
  - classification of each item as accepted, rejected with technical rationale, needs clarification, or non-actionable commentary
  - evidence used to accept, reject, clarify, defer, or route feedback
  - clarification questions or technical pushback when feedback is unclear, wrong, too broad, or conflicts with project intent
  - implementation route for accepted feedback, including direct fix, writing-plans, tdd, subagent-driven-development, standards-and-spec-review, code-security-review, or doc-sync
  - per-item fix summary with verification evidence, skipped checks, assumptions, and residual risk
  - closeout routed through verification-before-completion before any fixed, clean, done, or ready claim
depends_on:
  hard: []
  soft:
    - grill-with-docs when feedback exposes unclear intent, scope, project language, tradeoffs, or public behavior
    - writing-plans when accepted feedback is non-trivial, multi-step, risky, or needs an executable implementation route before edits
    - tdd when accepted feedback changes behavior, public interfaces, regressions, or testable workflows
    - standards-and-spec-review when feedback concerns issue fit, acceptance criteria, project standards, unrequested scope, or spec interpretation
    - code-security-review when feedback touches trust boundaries, auth, permissions, user data, persistence, unsafe execution, secrets, or security-sensitive configuration
    - subagent-driven-development when a large or parallelizable feedback set needs delegated implementation or review while the main agent keeps ownership
    - doc-sync when accepted feedback changes behavior, interfaces, architecture, standards, configuration, tests, or public docs
    - verification-before-completion before claiming feedback is fixed, resolved, clean, implemented, passing, ready, or complete
  fallback: If companion skills, review tools, git history, tests, docs, or subagents are unavailable, inspect the smallest relevant source evidence, classify uncertainty explicitly, implement only safe accepted items, and downgrade unsupported claims.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Receiving Code Review

## Purpose

Handle review feedback as technical input to evaluate, not orders to obey or social pressure to satisfy.

This skill is the controller for review feedback. It inventories comments, verifies them against the target project, decides which items are accepted, rejected, unclear, or non-actionable, then routes accepted work to the right implementation and proof workflow. It does not replace standards/spec review, security review, TDD, doc sync, or final verification.

The default posture is respectful skepticism: understand the reviewer, check the source, then act or respond with evidence.

## Inputs

- Review feedback from a user, maintainer, teammate, reviewer agent, PR tool, CI bot, issue thread, patch review, or code comment.
- Review source and authority, including whether the feedback comes from the user, project maintainer, external reviewer, automated tool, or subagent.
- The reviewed diff, patch, changed files, commit range, PR, issue, implementation plan, acceptance criteria, or original request.
- Relevant source, tests, docs, standards, ADRs, project context, logs, rendered artifacts, or command output needed to evaluate the feedback.
- Review tool context, such as comment threads, requested-change status, inline anchors, or links, when available.
- User or project constraints about scope, urgency, risk tolerance, compatibility, and required response style.

## Workflow

1. Collect the full feedback set before editing:
   - Read every review item in scope before reacting.
   - Preserve the original review context, such as file, line, thread, severity, reviewer, and requested-change status.
   - Separate review facts from interpretation. A reviewer saying "this is wrong" is a claim to verify, not proof by itself.
   - Do not start edits until each item is at least understood well enough to classify or ask a focused clarification question.

2. Understand each item:
   - Restate the technical requirement in your own working notes: what behavior, code path, standard, risk, or expectation is the reviewer pointing at?
   - Identify whether the item is about correctness, security, spec fit, standards, tests, docs, architecture, style, maintainability, performance, or non-actionable commentary.
   - If the requirement, affected scope, or expected outcome is unclear, classify it as `needs clarification`.
   - If unclear items may affect implementation order, shared interfaces, architecture, or correctness, stop and ask before editing related items.

3. Verify against project reality:
   - Inspect the relevant source, diff, tests, docs, specs, standards, or runtime evidence before accepting or rejecting the feedback.
   - Check whether the current implementation exists for compatibility, legacy behavior, platform support, project standards, security posture, or an earlier user decision.
   - For "implement properly", "make this robust", "add abstraction", or broad cleanup requests, verify actual usage and current scope before expanding work.
   - If you cannot verify an important claim with available evidence, say what is missing and route to clarification, investigation, or a narrower safe fix.

4. Classify every item:
   - `accepted`: evidence supports the feedback, and the requested change is in scope or explicitly approved.
   - `rejected with technical rationale`: evidence shows the suggestion is wrong, harmful, obsolete, out of scope, duplicative, incompatible, or conflicts with accepted project intent.
   - `needs clarification`: the item is ambiguous, missing context, has multiple plausible fixes, or requires a user or maintainer decision.
   - `non-actionable commentary`: the item is observation, praise, preference, or context that does not require code, docs, tests, or a response beyond acknowledgement when appropriate.
   - Keep these statuses distinct. Do not hide rejected or unclear feedback inside a generic "handled" summary.

5. Choose the route for accepted or disputed work:
   - Use `code-security-review` for exploitable risk, trust boundaries, auth, permissions, secrets, user data, persistence, unsafe execution, or security-sensitive config.
   - Use `standards-and-spec-review` when the question is whether the implementation fits the issue, acceptance criteria, project standards, or allowed scope.
   - Use `tdd` when the fix changes observable behavior, a public interface, or a regression-prone workflow that should have behavior proof.
   - Use `writing-plans` before broad, risky, or multi-step feedback implementation.
   - Use `subagent-driven-development` when independent accepted items can be delegated with clear write ownership and review evidence.
   - Use `doc-sync` when accepted feedback changes docs, public behavior, architecture, standards, configuration, tests, or user-facing workflows.

6. Implement accepted feedback one item at a time when practical:
   - Prefer the smallest vertical slice that fixes and proves the reviewed behavior.
   - Fix high-risk blockers first, especially correctness, security, data loss, broken builds, and failed acceptance.
   - Then handle simple mechanical fixes, followed by more complex refactors or behavior changes.
   - Verify each fix before moving to the next item. If items are tightly coupled and must be fixed together, name that coupling and verify the grouped behavior explicitly.
   - Keep rejected, unclear, deferred, and non-actionable items out of the edit batch.

7. Preserve GOATED design discipline:
   - Push back on horizontal batches, broad cleanup, speculative scaffolding, or "proper abstraction" requests unless source evidence shows they improve the current task.
   - Evaluate abstraction suggestions through the deep-module lens: a useful abstraction should expose a small meaningful interface that hides real behavior and improves locality.
   - Reject shallow pass-through layers, test-only hooks, and future-proofing that widen interfaces without reducing real complexity.
   - Prefer tests through public interfaces and vertical behavior proof over implementation-detail tests created only to satisfy a review comment.

8. Respond with evidence, not performance:
   - For accepted items, state the technical fix and verification evidence.
   - For rejected items, give the shortest accurate technical rationale and cite the source, test, spec, or constraint that supports it.
   - For unclear items, ask the specific question that would change the implementation.
   - For non-actionable commentary, acknowledge only as needed and do not invent work.
   - When using hosted review tools, reply in the original review context or thread when the tool supports it; do not require one specific host or command.

9. Close through verification:
   - Run or inspect the evidence that matches the fixed items: tests, builds, diffs, source reads, docs checks, rendered artifacts, CI, manual checks, or reviewer-thread state.
   - Use `verification-before-completion` before claiming feedback is fixed, resolved, clean, ready, implemented, passing, or complete.
   - If any feedback remains unclear, rejected, deferred, unverified, or blocked, say so plainly and keep the final claim narrow.

## Output Contract

Return a compact review-feedback report shaped like this:

```markdown
## Review Feedback Handling

- Scope: <review source, diff/PR/issue/patch, changed files, or supplied comments>
- Feedback inventory: <count and short summary of items>
- Evidence inspected: <source, tests, docs, diffs, commands, threads, or assumptions>

## Feedback Status

| Item | Status | Evidence | Route or action |
| --- | --- | --- | --- |
| <comment id or summary> | <accepted | rejected with technical rationale | needs clarification | non-actionable commentary> | <source evidence or missing evidence> | <fix, ask, push back, route, or no action> |

## Work Performed

- <accepted item fixed, paths touched, and verification evidence>

## Responses Needed

- Clarification: <questions, or "None">
- Technical pushback: <rejected items and rationale, or "None">
- Deferred or non-actionable: <items and reason, or "None">

## Verification

- Evidence: <commands, source reads, diffs, docs, rendered artifacts, CI, or manual checks>
- Skipped checks: <checks skipped with reasons, or "None">
- Residual risk: <remaining uncertainty, or "Low">
- Completion claim: <claim allowed by verification-before-completion>
```

For tiny feedback sets, a shorter response is acceptable only if it still separates accepted, rejected, unclear, and non-actionable items when those statuses exist.

## Delegation

The main agent owns feedback classification, technical judgment, scope control, final responses, and completion claims.

When subagents are available, use them for bounded work such as:

- inventorying a large review thread;
- verifying one reviewer claim against a source area;
- implementing one accepted item with clear write ownership;
- running a focused standards/spec, security, docs, or verification pass;
- checking whether a proposed rejection or acceptance is evidence-backed.

Require delegated results to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- feedback items inspected or changed;
- paths, diffs, docs, threads, artifacts, or commands inspected;
- classification recommendations with evidence;
- changes made, tests or checks run, skipped checks, assumptions, concerns, and residual risk;
- recommendation for the main agent, not an unsupervised final response.

Handle delegated status this way: `DONE` means inspect the evidence and integrate it; `DONE_WITH_CONCERNS` means resolve concerns before editing or responding; `NEEDS_CONTEXT` means provide missing review scope, source, spec, command, or decision; `BLOCKED` means narrow the work, ask the user, or report the blocker without claiming resolution.

If subagents are unavailable, run the same intake, classification, implementation, review, and verification steps sequentially with a narrower context budget.

## Guardrails

- Do not implement feedback before understanding the item well enough to classify it.
- Do not treat reviewer confidence, tool output, or social pressure as technical proof.
- Do not agree performatively or imply correctness before checking the source.
- Do not reject feedback defensively; reject only with technical evidence or explicit scope rationale.
- Do not partially implement a multi-item review while unresolved items could change the shared design, interface, or correctness path.
- Do not collapse accepted, rejected, unclear, and non-actionable feedback into one "done" bucket.
- Do not broaden accepted feedback into unrelated refactors, horizontal layers, speculative cleanup, or shallow abstractions.
- Do not claim security confidence from normal tests or standards review; route security-relevant feedback to `code-security-review`.
- Do not claim behavior is fixed without behavior proof when `tdd` or an equivalent public-interface check is feasible.
- Do not claim review feedback is complete until `verification-before-completion` supports the exact claim.
- Do not require a specific git host, review tool, CI provider, subagent product, branch model, or command syntax.
- Do not include private notes, ignored scratch content, credentials, client data, sensitive personal context, secrets, or real user data in review responses.
- Do not make installed use depend on this source repo's root files, issue files, `.local/` research, upstream sources, or hidden chat history.

## References

No external references are required. This skill is self-contained after installation.
