---
name: using-goated-ai-skills
description: Use at the start of each new task before the first edit or command, when it is unclear which installed skill applies, or when scope changes mid-task; selects a proportionate route for delivery, onboarding, maintenance, installation, knowledge retrieval, research, prompt work, or a tiny direct task.
metadata:
  goated-category: agent-workflows
---

# Using GOATED AI Skills

## Purpose

Select one proportionate route, reuse shared evidence and consent, and revise
only affected route parts at controlled checkpoints.

Rerun routing for a stale envelope or material route signal. A finished skill
alone is not a reason to reload it. For an obvious tiny request, apply the
lightweight path silently apart from the one-line `goated-route: direct`.

## Inputs

- User request, instructions, constraints, and selected approval mode.
- Current project boundary and applicable project instructions.
- Existing work envelope, decisions, approvals, and evidence entries.
- Integrated registry metadata when installed, or the available skill list.
- Material route signals from skills.

## Dependencies

Hard: None.

Soft:
- shared integrated policy and registry for common behavior and skill metadata
- `session-start-progressive-disclosure` for orientation, on its gate below
- specialist skills selected as gates below
- `wayfinder` when uncertainty is branching and exceeds one focused session

Fallback: Without the shared policy or registry, use the compact profile, gate,
skill map, approval, evidence, checkpoint, and route-line rules in this file.

## Workflow

1. **Apply precedence and establish the boundary.**
   - Follow system, user, and applicable project instructions before GOATED
     defaults. Honor explicit use or skip requests unless unsafe.
   - Stop before writes only when an unresolved conflict, project boundary, or
     material user decision blocks safe progress.

2. **Initialize or reuse one work envelope.**
   - Always record goal, scope, action reach, and next action.
   - Populate a profile dimension only when it changes routing, approval,
     proof, or resumability. Add sensitivity, risks, gates, evidence,
     decisions, questions, or continuity state only when they carry decision
     value.
   - Derive workflow intensity: `lightweight` for local, clear, reversible work;
     `standard` for scoped cross-file or proof-bearing work; `full` for large,
     branching, resumable, delegated, restricted, architectural, security, or
     external-changing work.
   - Reuse a fresh envelope. Keep single-session state in conversation or
     framework state; use an ignored local artifact only for resumable work.

3. **Reuse evidence before discovery.**
   - Reuse an entry when its source, scope, freshness, depth, and
     confidence support the next claim.
   - Refresh only missing, stale, changed, contradictory, or too-shallow
     evidence. Prefer current source and executable proof for exact or
     high-risk claims.

4. **Select the route once.**
   - Classify only justified gates as required or conditional; record skips
     only when decision-relevant.
   - Choose the smallest correct, safe path:

| Gate | Select when | Skills |
| --- | --- | --- |
| Proportional orientation | Unfamiliar, cross-area, stale, or boundary-uncertain work, or a `standard` or `full` route from a brief | `session-start-progressive-disclosure` |
| Clarification or diagnosis | Intent or root cause materially blocks action | `grill-with-docs`; `diagnose` for failures |
| External research | External claims need cited sources, or their authority, freshness, conflicts, or gaps matter | `source-grounded-research` |
| Knowledge retrieval | Durable project knowledge must answer a question, especially when authority, freshness, conflict, or provenance matters | `knowledge-retrieval` |
| Wayfinder | Uncertainty branches across focused sessions and later decisions depend on earlier evidence | `wayfinder` |
| Spec, architecture, or tickets | Durable intent, module strategy, or multiple resumable slices must be settled | `write-a-spec`, `design-codebase-architecture`, `spec-to-tickets` |
| Writing plan | A `standard` or `full` task needs executable steps or implements a ticket | `writing-plans` |
| TDD or equivalent proof | Behavior, a public interface, or regression risk changes | `tdd` |
| Design principles | A module, interface, abstraction, error path, or configuration surface is designed, changed, or reviewed | `software-design-principles` |
| Standards/spec review | Diff size, risk, acceptance, scope, or convention uncertainty warrants specialist review | `standards-and-spec-review` |
| Security review | A trust boundary changes or auth, permissions, secrets, private data, persistence policy, execution, dependency, deployment, or another sensitive surface is affected | `code-security-review` |
| Documentation sync | Durable behavior, interfaces, configuration, architecture, or operator expectations may drift | `doc-sync` |
| Full verification | Work is complex, high-risk, delegated, multi-surface, or explicitly audited | `verification-before-completion` |
| Handoff | Work is resumable, interrupted, cross-session delegated, or unfinished | `handoff` |

   - Load code refinement only for observed debt or explicit cleanup.
   - Other specialists load on their own triggers: `documentation-writer` to
     write or substantially revise guides, manuals, or runbooks;
     `documentation-cleanup` to audit or tidy docs; `goated-prompt` to write
     prompts or prompt-writing guidance; `retrospective` after a merged wave of
     delegated tickets, or recurring friction; `prototype` for cheap evidence;
     `setup-scribe` for setup knowledge. Leave an uninstalled skill out of
     `requires:`.
   - Reject Wayfinder for merely large work, session-sized discussion, or
     implementation whose decisions are settled. Its chart requires approval
     covering destination, location, visible frontier, action reach, and
     initial write scope before any map write; envelope consent covering all
     five satisfies it.
   - Tiny work uses direct action and narrow proof without extra gates.

5. **Apply approval once for the current reach.**
   - Without a selected mode, use the risk-adaptive default: safe reads and
     diagnostics proceed; scoped reversible project writes may use one batch;
     destructive, credential, protected-branch, deployment, publication, and
     external-changing actions need explicit approval covering that action.
   - Honor `confirm-each-write`, `approve-batch`,
     `standing-session-consent`, or `draft-without-applying`.
   - Reuse consent while its scope and action reach cover the work; a
     material change to either needs a fresh decision before the expanded
     action.
   - Skills do not add approval gates to covered actions. For a necessary
     pause, cite the instruction and unresolved decision; continue independent
     authorized work.

6. **Execute through selected gates.**
   - Give each skill its envelope slice and fresh evidence.
   - Skills return internal deltas: result, evidence, changes, risks, route
     signals, and skipped checks. They never rebuild the route or give
     competing closeouts.
   - Keep routine routing internal. Report only decisions, blockers, approval
     needs, material scope or risk changes, or useful long-work progress.

7. **Re-evaluate only when allowed.**
   - Scheduled checkpoints are after clarification or diagnosis, after
     planning, after implementation, and before final completion.
   - A material signal such as `scope-changed`, `evidence-stale`,
     `security-impact`, `documentation-impact`, or `refinement-debt` may trigger
     an earlier checkpoint before affected work continues.
   - Change only gates the signal affects; record why. Do not restart
     discovery or activate a long pipeline.
   - After project changes, invalidate affected evidence and collect
     fresh proof. Preserve unaffected evidence and approvals.

8. **Close out once.**
   - Continue implementation through the agreed result, matching proof, and
     related fixes. Honor review-only scope and explicit checkpoints.
   - The main agent integrates skill deltas and produces one response with the
     outcome, important changes, fresh proof, skipped checks, and residual risk.

## Output Contract

Return one compact envelope update using Step 2's core fields. Add only
decision-relevant route changes, approval needs, evidence, or residual risk,
explaining changes that affect a user decision. Standalone use returns
the same route and closeout without shared files.

End routing with one route line, on its own line, outside code blocks:

- `goated-route: direct` for tiny work that needs no specialist skill;
- `goated-route: <lightweight|standard|full> | requires: <skill>, <skill>`
  when the listed specialist skills must load before the first write;
- `goated-route: continue` when a later prompt continues the current task and
  its route.

`doc-sync`, `standards-and-spec-review`, `verification-before-completion` and
`setup-scribe` are met at the closeout, not in `requires:`, unless the task is
that skill's own work, such as a review; `code-security-review` may be listed,
as it applies while writing.

Use lowercase keywords and installed skill names, list each skill once, and
add no trailing text. A checkpoint changing the required skills writes a new
route line; the last one wins. Write it in a message, call description, or
skill arguments the framework reads, by the first call it covers, or for a
write on an earlier call of its message.

## Delegation

The main agent owns the envelope, routing, consent interpretation, and
integration. Delegate only bounded work with non-overlapping ownership. Require
inspected paths, commands, evidence, assumptions, status, and envelope deltas;
review them before use. Without delegation, run the route sequentially.

## Guardrails

- Keep the envelope free of model, provider, cost, resource-tier, or Factory
  metrics.
- Lightweight work keeps the same proof, privacy, security, and scope control.
- Do not expose restricted data, credentials, private notes, or user content in
  tracked state or public output.
- When a selected skill is unavailable, use the closest safe direct procedure
  and state the missing capability or residual risk.
