---
name: receiving-code-review
description: Use when review feedback must be classified as accepted, rejected, unclear, or requiring a user decision before implementation or response.
metadata:
  goated-category: engineering
---

# Receiving Code Review

## Purpose

Handle review feedback as technical input to evaluate, not orders to obey or social pressure to satisfy.

This skill is the controller for review feedback. It inventories comments, verifies them against the target project, decides which items are accepted, rejected, unclear, or non-actionable, then routes accepted work to the right implementation and proof workflow. It does not replace standards/spec review, security review, TDD, doc sync, or final verification.

The default posture is respectful skepticism: understand the reviewer, check
the source, then act or respond with evidence.

## Activation

Load this skill when feedback from a person, tool, PR, issue, or reviewer agent
needs technical classification. Do not load it for a general standards/spec or
security review when no feedback is being received.

Reuse fresh work-envelope evidence and existing review scope. Refresh only
evidence invalidated by the change or too weak for the feedback claim.

## Inputs

- Review feedback from a user, maintainer, teammate, reviewer agent, PR tool, CI bot, issue thread, patch review, or code comment.
- Review source and authority, including whether the feedback comes from the user, project maintainer, external reviewer, automated tool, or subagent.
- The reviewed diff, patch, changed files, commit range, PR, issue, implementation plan, acceptance criteria, or original request.
- Relevant source, tests, docs, standards, ADRs, project context, logs, rendered artifacts, or command output needed to evaluate the feedback.
- Review tool context, such as comment threads, requested-change status, inline anchors, or links, when available.
- User or project constraints about scope, urgency, risk tolerance, compatibility, and required response style.

## Dependencies

Hard: None.

Soft:
- grill-with-docs when feedback exposes unclear intent, scope, language, tradeoffs, or public behavior
- writing-plans when accepted feedback is non-trivial, multi-step, risky, or needs a route before edits
- tdd when accepted feedback changes behavior, public interfaces, regressions, or testable workflows
- code-refinement when accepted feedback is scoped cleanup, simplification, or behavior-preserving refactor work
- standards-and-spec-review when feedback concerns issue fit, acceptance, standards, unrequested scope, or spec interpretation
- code-security-review when feedback touches trust boundaries, auth, permissions, user data, persistence, execution, secrets, or security config
- subagent-driven-development when large or parallelizable feedback needs delegated implementation or review
- doc-sync when accepted feedback changes behavior, interfaces, architecture, standards, configuration, tests, or public docs
- verification-before-completion for complex, high-risk, delegated,
  multi-surface, or explicitly audited feedback closeout; otherwise verify the
  narrow claim directly with fresh evidence

Fallback: If companion skills, review tools, git history, tests, docs, or subagents are unavailable, inspect minimal source evidence, classify uncertainty, implement only safe accepted items, and downgrade unsupported claims.

## Workflow

1. Collect the full feedback set before editing:
   - Read every review item in scope before reacting.
   - Preserve the original review context, such as file, line, thread, severity, reviewer, and requested-change status.
   - Separate review facts from interpretation. A reviewer saying "this is wrong" is a claim to verify, not proof by itself.
   - Do not start edits until each item is at least understood well enough to classify or ask a focused clarification question.

2. Understand each item:
   - Restate the technical requirement in your own working notes: what behavior, code path, standard, risk, or expectation is the reviewer pointing at?
   - Identify whether the item is about correctness, security, spec fit, standards, tests, docs, architecture, style, maintainability, performance, or non-actionable commentary.
   - If the technical meaning or affected scope is unclear, classify it as
     `unclear`.
   - If the comment is technically clear but selecting an outcome requires
     product intent, risk acceptance, preference, or authority the agent does
     not own, classify it as `user decision`.
   - If unclear items may affect implementation order, shared interfaces, architecture, or correctness, stop and ask before editing related items.

3. Verify against project reality:
   - Inspect the relevant source, diff, tests, docs, specs, standards, or runtime evidence before accepting or rejecting the feedback.
   - Check whether the current implementation exists for compatibility, legacy behavior, platform support, project standards, security posture, or an earlier user decision.
   - For "implement properly", "make this robust", "add abstraction", or broad cleanup requests, verify actual usage and current scope before expanding work.
   - If you cannot verify an important claim with available evidence, say what is missing and route to clarification, investigation, or a narrower safe fix.

4. Classify every item:
   - `accepted`: evidence supports the feedback, and the requested change is in scope or explicitly approved.
   - `rejected with technical rationale`: evidence shows the suggestion is wrong, harmful, obsolete, out of scope, duplicative, incompatible, or conflicts with accepted project intent.
   - `unclear`: the technical requirement, evidence, or affected scope is not understood well enough to judge.
   - `user decision`: the options are understood, but authority or product intent is required before choosing.
   - Preserve non-actionable commentary in the inventory only when context
     matters; do not manufacture a fifth action status or hide rejected,
     unclear, or user-decision items inside a generic "handled" bucket.

5. Choose the route for accepted or disputed work:
   - Use `code-security-review` for exploitable risk, trust boundaries, auth, permissions, secrets, user data, persistence, unsafe execution, or security-sensitive config.
   - Use `standards-and-spec-review` when the question is whether the implementation fits the issue, acceptance criteria, project standards, or allowed scope.
   - Use `tdd` when the fix changes observable behavior, a public interface, or a regression-prone workflow that should have behavior proof.
   - Use `code-refinement` when the accepted item is scoped cleanup, simplification, or refactoring that should preserve behavior.
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
   - For unclear items, ask for the missing technical fact.
   - For user-decision items, present the decision, recommendation, and tradeoff.
   - Acknowledge non-actionable commentary only as needed and do not invent work.
   - When using hosted review tools, reply in the original review context or thread when the tool supports it; do not require one specific host or command.

9. Close through verification:
   - Run or inspect the evidence that matches the fixed items: tests, builds, diffs, source reads, docs checks, rendered artifacts, CI, manual checks, or reviewer-thread state.
   - Match fixed, resolved, implemented, passing, or complete claims to fresh
     evidence. Load `verification-before-completion` only when the closeout is
     complex, high-risk, delegated, multi-surface, or explicitly audited.
   - If any feedback remains unclear, rejected, awaiting a user decision,
     deferred, unverified, or blocked, keep the claim narrow.
   - Update the envelope with classifications, findings, evidence changes, and
     route deltas. Leave one consolidated closeout to the controlling agent.

## Output Contract

Return the smallest useful feedback delta. A sentence or short list is enough
for one obvious item. Use a table for multiple or mixed classifications:

```markdown
| Item | Status | Evidence | Route or action |
| --- | --- | --- | --- |
| <comment id or summary> | <accepted | rejected with technical rationale | unclear | user decision> | <fresh source evidence or missing evidence> | <fix, push back, clarify, decide, or route> |
```

Include only material work performed, changed evidence, skipped checks,
residual risk, and route signals. Do not repeat the full work envelope,
standards/security reports, or a separate completion summary.

## Delegation

Main owns feedback classification, technical judgment, scope control, final responses, and completion claims.

Delegate only bounded review work: inventory a large thread, verify one reviewer claim, implement one accepted item with clear ownership, run focused standards/spec/security/docs/verification review, or check whether an acceptance/rejection is evidence-backed.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; feedback inspected or changed; paths/diffs/docs/threads/artifacts/commands inspected; classification evidence; changes made; tests/checks run or skipped; assumptions, concerns, residual risk; and recommendation, not final response.

Status handling: `DONE` gets evidence inspection before integration; `DONE_WITH_CONCERNS` requires concern resolution before editing/responding; `NEEDS_CONTEXT` gets missing review scope, source, spec, command, or decision; `BLOCKED` narrows the work, asks the user, or reports the blocker without claiming resolution.

If subagents are unavailable, run the same intake, classification, implementation, review, and verification sequentially with a narrower context budget.

## Guardrails

- Do not implement feedback before understanding the item well enough to classify it.
- Do not treat reviewer confidence, tool output, or social pressure as technical proof.
- Do not agree performatively or imply correctness before checking the source.
- Do not reject feedback defensively; reject only with technical evidence or explicit scope rationale.
- Do not partially implement a multi-item review while unresolved items could change the shared design, interface, or correctness path.
- Do not collapse accepted, rejected, unclear, and user-decision feedback into one "done" bucket.
- Do not broaden accepted feedback into unrelated refactors, horizontal layers, speculative cleanup, or shallow abstractions.
- Do not claim security confidence from normal tests or standards review; route security-relevant feedback to `code-security-review`.
- Do not claim behavior is fixed without behavior proof when `tdd` or an equivalent public-interface check is feasible.
- Do not claim review feedback is complete until `verification-before-completion` supports the exact claim.
- Do not require a specific git host, review tool, CI provider, subagent product, branch model, or command syntax.
- Do not include private notes, ignored scratch content, credentials, client data, sensitive personal context, secrets, or real user data in review responses.
- Do not make installed use depend on this source repo's root files, issue files, `.local/` research, upstream sources, or hidden chat history.

## References

No external references are required. This skill is self-contained after installation.
