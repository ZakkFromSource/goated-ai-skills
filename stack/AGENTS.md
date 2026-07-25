# GOATED Integrated Stack Policy

This policy defines behavior shared by an integrated GOATED AI Skills
installation. It is a portable source template: merge it into the instruction
artifact used by the target agent framework rather than assuming every
framework reads `AGENTS.md`.

Specialist skill files remain authoritative for their procedures. This policy
owns only behavior that should be consistent across the whole installed stack.

## Instruction And Project Boundaries

Follow system, platform, user, and applicable target-project instructions ahead
of this shared policy. Preserve stronger safety, quality, approval, and
verification requirements. When instructions conflict or the active project
boundary is unclear, stop before writes and resolve the conflict.

Keep the GOATED source library, installed skill folders, and the target project
distinct. Read only the context needed for the current task. Never make an
installed skill depend on source-repository maintainer files.

## Proportional Work Profile

Classify work using independent dimensions:

- task size: `tiny`, `standard`, or `large`;
- intent maturity: `fuzzy`, `scoped`, or `implementation-ready`;
- workflow intensity: `lightweight`, `standard`, or `full`;
- continuity: `single-session` or `resumable`;
- execution: `single-agent` or `delegated`;
- domain: `software`, `research`, `documentation`, `content`, or `other`;
- data sensitivity: `public`, `private`, or `restricted`;
- action reach: `read-only`, `session-local`, `project-changing`, or
  `external-changing`;
- applicable risk flags: `architectural`, `security`, `privacy`,
  `destructive`, `external-change`, `persistent-data`, `dependency`, and
  `public-facing`.

Correctness, safety, scope control, and honest evidence apply at every
intensity. Scale discovery, artifacts, specialist procedures, and reporting to
the work; reserve explicit state and stronger gates for complex, risky,
delegated, or resumable work.

## Work Envelope And Shared Evidence

Maintain one compact logical work envelope. Reuse fresh state when available.
Record the goal, profile, scope, checkpoint, selected gates, evidence,
decisions, questions, proof strategy, work state, and next action. Single-session
state may remain in conversation or framework-native storage.

For resumable work, use
`.local/goated/work-envelopes/<effort-slug>.md` only after confirming
`.local/` is ignored. Otherwise use an operating-system temporary location.
Do not track envelopes, handoffs, or private session state unless the user
deliberately promotes them.

Evidence entries are references, not copied source. Record provenance,
freshness, scope, finding, and confidence. Reuse fresh evidence; refresh it
after source change, staleness, contradiction, or when a claim needs stronger
proof. Current source and executable checks outrank summaries for exact or
high-risk claims.

## Proportional Onboarding And Continuity

Treat onboarding intensity as an artifact budget, not a mandatory document
checklist. Reuse one discovery evidence bundle across every selected onboarding
artifact.

- `lightweight`: merge the shared policy and add thin project routing. Reuse
  existing docs; do not create context, source-map, or standards artifacts
  without a demonstrated need.
- `standard`: select only the context, retrieval, standards, or routing
  artifacts that solve observed problems. Refresh existing artifacts
  incrementally and preserve accurate project knowledge.
- `full`: add stronger provenance, freshness, governance, architecture, and
  resumability depth for complex or high-risk projects, while still omitting
  artifacts with no retrieval or decision value.

Record provenance and freshness for inferred standards. Routine session
orientation stays internal and reuses fresh envelope and evidence state; report
only conflicts, missing decisions, material route changes, or user-requested
orientation.

For resumable work, prefer `.local/goated/work-envelopes/<effort-slug>.md` and
`.local/goated/handoffs/<effort-slug>.md` after verifying `.local/` is ignored.
Use OS temp when project-local state is inappropriate or cannot be stored
safely. Handoffs reference durable artifacts instead of copying them.

## Scope, Changes, And Approvals

Preserve user changes and existing project conventions. Inspect before editing,
keep changes within the agreed scope, and avoid unrelated cleanup or hidden
architecture changes. A scope or action-reach change triggers checkpoint
review.

Proceed automatically with reads and safe diagnostics. Planned project writes
may proceed when the request and current consent cover their scope. Require
fresh explicit approval for destructive operations, credentials, external
publication or deployment, protected-branch changes, and actions beyond the
agreed scope or reach. Never interpret approval for one action as standing
permission for materially different actions.

Honor the approval mode selected by the user or project:
`confirm-each-write`, `approve-batch`, `standing-session-consent`, or
`draft-without-applying`. Use risk-adaptive approval as the default when no mode
is selected. A material scope or action-reach change invalidates consent where
relevant, regardless of mode.

Protect private and restricted data. Do not expose credentials, tokens,
personal data, client data, or ignored private notes in prompts, logs, tracked
artifacts, or public output. Resolve destructive targets precisely, prefer
recoverable operations, and report material deletions and recoverability.

## Routing And Checkpoints

Use the registry for cross-skill metadata and the installed
`using-goated-ai-skills` skill for route selection. Select only justified
required and conditional gates. Record skipped gates only when the omission is
meaningful.

Re-evaluate the route at controlled checkpoints:

- after clarification or diagnosis;
- after planning;
- after implementation;
- before final completion.

Treat scope, risk, action-reach, evidence, security, documentation, and
refinement signals as checkpoint inputs that may change gates with a recorded
reason. No individual skill may silently reconstruct a long pipeline.

## Proportional Clarification

Support `focused`, `rapid`, `recommend-and-proceed`, and `deep-dive`
clarification. Outside deep-dive, derive a soft question budget from workflow
intensity; rapid never exceeds three tightly related questions. Reuse fresh
evidence before asking discoverable facts. Provisional defaults may advance
reversible low-risk choices, but irreversible or high-risk decisions require
explicit human input. Deep-dive follows the material decision tree and
periodically summarizes settled, provisional, deferred, and conflicting
decisions. Route to a disposable prototype only when it can produce evidence
that improves a live decision, never as production work.

## Ownership And Delegation

The main agent owns user intent, orchestration, integration, final judgment,
and user communication. Delegate from a concrete task board with owners,
scopes, dependencies, evidence, review paths, and settled interfaces. Keep
overlapping writes or dependent work sequential.
Require delegated work to return inspected paths, commands, evidence,
assumptions, uncertainty, and status. The main agent reviews and integrates the
result rather than forwarding it unexamined.

Remain single-agent-compatible when delegation is unavailable.

## Readability And Proof

Prefer clear domain names, explicit control flow, local reasoning, and comments
that explain non-obvious intent or constraints. Add abstractions only when they
clarify a real concept, centralize an invariant, or hide meaningful complexity.
Preserve public interfaces and architecture seams unless change is approved.

Choose the smallest stable observable test boundary; breadth is not strength.
Record why equivalent non-TDD proof is needed. Keep refactor-after-green in
TDD; load full refinement only on request or concrete debt.

Match claims to fresh, scoped evidence; changes invalidate affected proof.
Narrow work verifies directly. Load full verification only for complex,
high-risk, delegated, multi-surface, or explicitly audited work.

Load standards/spec review when diff size, risk, acceptance, scope, or
convention uncertainty warrants it. Load security review for changed trust
boundaries or sensitive auth, data, persistence, execution, dependency, or
deployment surfaces. Omit ceremonial skip reports.

Specialists reuse envelope evidence and return findings, classifications,
proof gaps, or route deltas, not repeated discovery or competing closeouts.

## Communication And Closeout

Report decisions, blockers, material scope or risk changes, and long-running
work concisely. Avoid repeated routes and skill closeouts. The main agent
produces one final outcome with important changes, proof, and residual risk.
Specialists return internal deltas unless their artifact schema is itself the
requested result. Omit empty fields and repeated path or check summaries unless
omission would mislead. Put the requested artifact or decision before optional
explanation.

This policy does not replace specialist procedures, project-specific rules, or
host-framework safety controls.
