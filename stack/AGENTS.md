# GOATED Integrated Stack Policy

Apply this shared policy through the framework's active instructions: merge it
or explicitly load its installed file once when GOATED applies. A link alone
does not load instructions.

Specialists own their task procedures; this policy owns common behavior.
Procedural defaults do not override instruction precedence or covering consent.

## Instruction And Project Boundaries

Follow system, platform, user, and applicable target-project instructions ahead
of skill defaults. Preserve their explicit safety, quality, approval, and proof
requirements. Resolve conflicts by precedence; ask only when a material
decision or unclear boundary still prevents safe progress.

Keep the GOATED source library, installed skill folders, and the target project
distinct. Read only the context needed for the current task. Never make an
installed skill depend on source-repository maintainer files.

## Proportional Work Profile

Classify only dimensions that affect routing, approval, proof, or resumability:

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

Maintain one compact envelope: goal, scope, action reach, and next action.
Add other state only when decision-relevant. Single-session state may remain
in conversation or framework storage.

For resumable work, use `.local/goated/work-envelopes/<effort-slug>.md` and
`.local/goated/handoffs/<effort-slug>.md` only after confirming
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

- `lightweight`: apply shared policy and thin project routing. Reuse
  existing docs; do not create context, source-map, or standards artifacts
  without a demonstrated need.
- `standard`: select only the context, retrieval, standards, or routing
  artifacts that solve observed problems. Refresh existing artifacts
  incrementally and preserve accurate project knowledge.
- `full`: add stronger provenance, freshness, governance, architecture, and
  resumability depth for complex or high-risk projects, while still omitting
  artifacts with no retrieval or decision value.

Record provenance and freshness for inferred standards. Reuse fresh orientation;
report it only for material decisions, conflicts, or a user request.
Handoffs reference durable artifacts instead of copying them.

## Scope, Changes, And Approvals

Preserve user changes and existing project conventions. Inspect before editing,
keep changes within the agreed scope, and avoid unrelated cleanup or hidden
architecture changes. A scope or action-reach change triggers checkpoint
review.

Proceed automatically with reads and safe diagnostics. Planned project writes
may proceed when the request and current consent cover their scope. Require
explicit approval covering destructive operations, credentials, external
publication or deployment, protected-branch changes, and expanded scope or reach.
Reuse it only while it covers the same action. Prepare authorized, reviewable
work before requesting approval for a remaining action.

Honor the selected approval mode: `confirm-each-write`, `approve-batch`,
`standing-session-consent`, or `draft-without-applying`; default to
risk-adaptive approval. A material scope or reach change invalidates consent
in every mode.

Protect private and restricted data. Do not expose credentials, tokens,
personal data, client data, or ignored private notes in prompts, logs, tracked
artifacts, or public output. Resolve destructive targets precisely, prefer
recoverable operations, and report material deletions and recoverability.

## Routing And Checkpoints

Use the registry for cross-skill metadata and the installed
`using-goated-ai-skills` skill for route selection; it ends routing with a
`goated-route:` line. Select only justified required and conditional gates.

When a framework hold names an inapplicable skill, write
`goated-skip: <skill>: <reason>` where the router's output contract places
the route line, with an action-specific reason. To drop a route's skill,
re-route. Omit ceremonial skip reports.

Re-evaluate the route at controlled checkpoints:

- after clarification or diagnosis;
- after planning;
- after implementation;
- before final completion.

Treat scope, risk, action-reach, evidence, security, documentation, reproducibility,
and refinement signals as checkpoint inputs. Select `setup-scribe` only when
project setup knowledge is missing, changed, stale, or automation-ready. Record
material gate changes; no skill may silently reconstruct a pipeline.

## Proportional Clarification

Support `focused`, `rapid`, `recommend-and-proceed`, and `deep-dive`
clarification. Outside deep-dive, workflow intensity sets a soft question
budget; rapid never exceeds three tightly related questions. Reuse fresh
evidence before asking discoverable facts. Provisional defaults may advance
reversible low-risk choices; irreversible or high-risk decisions require
explicit human input. Deep-dive follows the material decision tree,
periodically summarizing settled, provisional, deferred, and conflicting
decisions. Route to a disposable prototype only when its evidence can improve
a live decision, never as production work.

## Ownership And Delegation

The main agent owns user intent, orchestration, integration, final judgment,
and user communication. Delegate from a concrete task board: owners, scopes,
dependencies, evidence, review paths, settled interfaces. Sequence
overlapping writes and dependent work.
Require delegated work to return inspected paths, commands, evidence,
assumptions, uncertainty, and status; review and integrate it, never forward
it unexamined.

Without delegation, remain single-agent-compatible.

## Readability And Proof

Keep code easy to understand and change; dependencies and obscurity threaten
that. Give each fact one owner, prefer deep modules to thin layers, name
precisely, comment what code cannot say, and never hide errors. Preserve public
interfaces and architecture seams unless change is approved. For design work,
load installed `software-design-principles`.

Choose the smallest stable observable test boundary and complete required
checks. Repeat or broaden checks for new changes, failures, or unresolved risk.
Record why equivalent non-TDD proof is needed. Keep refactor-after-green in TDD;
load full refinement only on request or concrete debt.

Match claims to fresh, scoped evidence; changes invalidate affected proof.
Narrow work verifies directly. Load full verification only for complex,
high-risk, delegated, multi-surface, or explicitly audited work.

Load standards/spec review when diff size, risk, acceptance, scope, or
convention uncertainty warrants it. Load security review for changed trust
boundaries or sensitive auth, data, persistence, execution, dependency, or
deployment surfaces.

## Communication And Closeout

Report decisions, blockers, material scope or risk changes, and long-running
work concisely. Avoid repeated routes and skill closeouts. The main agent
produces one final outcome with important changes, proof, and residual risk.
Specialists reuse envelope evidence and return internal deltas, not repeated
discovery or closeouts, unless their artifact is itself the requested result,
as a started agent's report is: it ends with its brief's report fields as
labelled lines, `Status` first. Omit empty fields and repeated path or check
summaries unless omission would mislead. Put the requested artifact or
decision before optional explanation.

Continue implementation through the requested behavior, verification, and fixes
caused by the change. Respect a review-only request or an explicit review
checkpoint. If a skill causes a pause, cite its exact instruction and explain
the unresolved decision or authorization.
