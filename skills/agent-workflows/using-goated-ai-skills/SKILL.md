---
name: using-goated-ai-skills
description: Use when an installed GOATED stack should select or revise a proportionate route for delivery, onboarding, source maintenance, installation, durable-knowledge retrieval, prompt work, or a tiny direct task.
metadata:
  goated-category: agent-workflows
---

# Using GOATED AI Skills

## Purpose

Select one proportionate route for the task, reuse shared evidence and consent,
and revise only the affected route parts at controlled checkpoints.

Use this router when work begins, an existing work envelope needs refreshing,
or a material route signal appears. Do not load it again merely because one
selected skill finished. For an obvious tiny request, apply the lightweight
path silently.

## Inputs

- User request, instructions, constraints, and selected approval mode.
- Current project boundary and applicable project instructions.
- Existing work envelope, decisions, approvals, and evidence entries.
- Integrated registry metadata when installed, or the available skill list.
- Material route signals returned by skills.

## Dependencies

Hard: None.

Soft:
- shared integrated policy and registry for common behavior and skill metadata
- `session-start-progressive-disclosure` when the project, source area,
  boundary, or evidence is unfamiliar, cross-area, or stale
- specialist skills selected as gates below
- `wayfinder` when uncertainty is branching and exceeds one focused session

Fallback: Without the shared policy or registry, use the compact profile, gate,
approval, evidence, and checkpoint rules in this file. Never depend on the
GOATED source repository or hidden session files.

## Workflow

1. **Apply precedence and establish the boundary.**
   - Follow system, user, and applicable project instructions before GOATED
     defaults. Honor explicit use or skip requests unless unsafe.
   - Stop before writes only when an unresolved conflict, project boundary, or
     material user decision blocks safe progress.

2. **Initialize or reuse one work envelope.**
   - Record the goal and agreed scope.
   - Record every profile dimension: task size, intent maturity, domain,
     continuity, execution, data sensitivity, action reach, and applicable risk
     flags.
   - Derive workflow intensity: `lightweight` for local, clear, reversible work;
     `standard` for scoped cross-file or proof-bearing work; `full` for large,
     branching, resumable, delegated, restricted, architectural, security, or
     external-changing work.
   - Reuse a fresh envelope. Keep single-session state in conversation or
     framework state; use an ignored local artifact only for resumable work.

3. **Reuse evidence before discovery.**
   - Reuse an entry when its source, applicable scope, freshness, depth, and
     confidence support the next claim.
   - Refresh only missing, stale, changed, contradictory, or too-shallow
     evidence. Prefer current source and executable proof for exact or
     high-risk claims.

4. **Select the route once.**
   - Put justified gates in `required_gates` or `conditional_gates`. Record a
     skipped gate only when the omission explains a meaningful decision.
   - Choose the smallest path that preserves correctness and safety:

| Gate | Select when |
| --- | --- |
| Proportional orientation | Always; near-zero ceremony for fresh tiny work |
| Clarification or diagnosis | Intent or root cause materially blocks action |
| Knowledge retrieval | Durable project knowledge must answer a question, especially when authority, freshness, conflict, or provenance matters |
| Wayfinder | Uncertainty branches across focused sessions and later decisions depend on earlier evidence |
| Spec, architecture, or tickets | Durable intent, module strategy, or multiple resumable slices must be settled |
| Writing plan | A scoped task still needs executable steps |
| TDD or equivalent proof | Behavior, a public interface, or regression risk changes |
| Standards/spec review | Diff size, risk, acceptance, scope, or convention uncertainty warrants specialist review |
| Security review | A trust boundary changes or auth, permissions, secrets, private data, persistence policy, execution, dependency, deployment, or another sensitive surface is affected |
| Documentation sync | Durable behavior, interfaces, configuration, architecture, or operator expectations may drift |
| Full verification | Work is complex, high-risk, delegated, multi-surface, or explicitly audited |
| Handoff | Work is resumable, interrupted, cross-session delegated, or unfinished |

   - Full orientation loads only for unfamiliar, cross-area, stale, or
     boundary-uncertain work. Code refinement loads only for observed
     refinement debt or an explicit cleanup request.
   - Wayfinder is not a synonym for large work. Reject it for session-sized
     discussion and for implementation whose decisions are already settled.
     Its chart requires approval of destination, location, visible frontier,
     action reach, and initial write scope before any map write.
   - Tiny work uses direct action plus narrow proof. Do not silently turn it
     into clarification, planning, review, and handoff.

5. **Apply approval once for the current reach.**
   - With no selected mode, use the risk-adaptive default: safe reads and
     diagnostics proceed; scoped reversible project writes may use one batch;
     destructive, credential, protected-branch, deployment, publication, and
     external-changing actions need explicit approval.
   - Honor `confirm-each-write`, `approve-batch`,
     `standing-session-consent`, or `draft-without-applying`.
   - Reuse consent while its scope and action reach still cover the work. A
     material change to either invalidates consent where relevant and requires
     a fresh decision before the expanded action.

6. **Execute through selected gates.**
   - Give each skill the relevant envelope slice and fresh evidence instead of
     asking it to rediscover the task.
   - Skills return internal deltas: result, evidence, changes, risks, route
     signals, and skipped checks. They do not reconstruct the downstream route
     or produce competing task closeouts.
   - Do not narrate routine routing. Report only decisions, blockers, approval
     needs, material scope or risk changes, or useful long-work progress.

7. **Re-evaluate only when allowed.**
   - Scheduled checkpoints are after clarification or diagnosis, after
     planning, after implementation, and before final completion.
   - A material signal such as `scope-changed`, `evidence-stale`,
     `security-impact`, `documentation-impact`, or `refinement-debt` may trigger
     an earlier checkpoint before affected work continues.
   - Compare the signal with the envelope, change only affected gates, and
     record the reason. Do not restart discovery or activate a long pipeline.
   - After project changes, invalidate affected pre-change evidence and collect
     fresh proof. Preserve unaffected evidence and approvals.

8. **Close out once.**
   - The main agent integrates skill deltas and produces one response with the
     outcome, important changes, fresh proof, skipped checks, and residual risk.

## Output Contract

Update or initialize a compact work envelope containing:

- agreed profile, sensitivity, action reach, risk flags, and scope;
- current checkpoint and selected required, conditional, and meaningful
  skipped gates;
- approval mode and covered scope/reach;
- reusable evidence and invalidated entries;
- proof strategy, route signals, decisions, work state, and next action.

Routine routing stays internal. When route visibility materially helps the
user, report only the chosen intensity, gates that affect their decisions,
approval needs, and the reason for any route change.

Standalone invocation returns the same compact route decision and local
closeout without assuming integrated policy, registry, or source-repo access.

## Delegation

The main agent owns the envelope, routing, consent interpretation, integration,
and user communication. Delegate only bounded work with non-overlapping
ownership. Require inspected paths, commands, evidence, assumptions,
uncertainty, status, and envelope deltas; review them before use.

Remain single-agent-compatible when delegation is unavailable.

## Guardrails

- Do not override user or project instructions with routing defaults.
- Do not add model, provider, cost, resource-tier, or Factory metrics.
- Do not treat the envelope as a mandatory tracked artifact.
- Do not repeat approvals, discovery, tests, or closeouts when fresh coverage
  already exists.
- Do not let one specialist silently select the remaining pipeline.
- Do not weaken proof, privacy, security, or scope control for lightweight work.
- Do not expose restricted data, credentials, private notes, or user content in
  tracked state or public output.
- Do not require unavailable skills; use the closest safe direct procedure and
  state the missing capability or residual risk.

## References

No external reference is required. Integrated installations may supply shared
policy and registry metadata; this file retains the standalone fallback.
