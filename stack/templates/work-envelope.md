# Work Envelope

Use this compact logical state protocol when the integrated stack needs shared
task state. It is not a mandatory tracked artifact. Omit irrelevant optional
fields and omit skipped gates when recording them would add no useful context.

```yaml
schema_version: 1.0.0
goal:
profile:
  task_size: # tiny | standard | large
  intent_maturity: # fuzzy | scoped | implementation-ready
  workflow_intensity: # lightweight | standard | full
  domain: # software | research | documentation | content | other
  risk_flags: [] # architectural, security, privacy, destructive,
                 # external-change, persistent-data, dependency, public-facing
  continuity: # single-session | resumable
  execution: # single-agent | delegated
data_sensitivity: # public | private | restricted
action_reach: # read-only | session-local | project-changing | external-changing
scope:
  included: []
  excluded: []
checkpoint:
route:
  required_gates: []
  conditional_gates: []
  skipped_gates: []
route_signals: []
evidence: []
decisions: []
open_questions: []
clarification: # optional
  mode: # focused | rapid | recommend-and-proceed | deep-dive
  question_budget: # non-negative integer; omit for deep-dive
  settled: []
  provisional: []
  deferred: []
  conflicting: []
  prototype_verdict:
approval:
  mode: # risk-adaptive-default | confirm-each-write | approve-batch |
        # standing-session-consent | draft-without-applying
  covered_scope: []
  covered_action_reach:
  consent_state: # valid | fresh-approval-required
proof_strategy:
changes: []
work_state:
next:
```

The `approval`, `route_signals`, and `changes` blocks are optional; omit them
when they add no decision value. The `clarification` block is also optional:
specialist grills update it and the existing evidence, decisions, open
questions, route, and next fields as a delta rather than emitting another full
closeout. Approval remains valid while its covered scope and action reach still
cover the work. A material change to either marks it
`fresh-approval-required` before the expanded action.

Other optional extensions may record a fixed point, artifacts, delegated work,
risks, or resume information. Do not add runtime cost, provider, model-ranking,
or Factory metric fields.

Keep single-session state in conversation or framework-native state. For
resumable work, use
`.local/goated/work-envelopes/<effort-slug>.md` only after confirming
`.local/` is ignored. Use operating-system temporary storage otherwise.
Nothing becomes tracked without deliberate user intent.
