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
evidence: []
decisions: []
open_questions: []
proof_strategy:
work_state:
next:
```

Optional extensions may record a fixed point, approvals, artifacts, delegated
work, route signals, risks, changes, or resume information. Do not add runtime
cost, provider, model-ranking, or Factory metric fields.

Keep single-session state in conversation or framework-native state. For
resumable work, use
`.local/goated/work-envelopes/<effort-slug>.md` only after confirming
`.local/` is ignored. Use operating-system temporary storage otherwise.
Nothing becomes tracked without deliberate user intent.
