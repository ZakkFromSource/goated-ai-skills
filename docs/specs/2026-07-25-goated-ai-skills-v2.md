# Spec: GOATED AI Skills V2

## Status

Ready for ticket breakdown, last updated 2026-07-25.

This spec intentionally supersedes conflicting V1 workflow and distribution
decisions. V1 remains a stable historical release; V2 becomes the active
development direction.

## Problem

GOATED AI Skills V1 provides strong, reusable disciplines for serious agent
work, but the complete stack has become more expensive to use than its compact
catalog suggests.

The main cost is cumulative ceremony:

- several skills can load during one normal delivery route;
- cross-cutting rules are repeated across skill dependencies, procedures,
  delegation sections, guardrails, and output contracts;
- downstream skills can rediscover the route and repeat project discovery;
- several skills can produce overlapping user-facing closeouts;
- specialist procedures such as `code-refinement` and
  `verification-before-completion` can be loaded when a narrower inline check
  would be sufficient;
- onboarding can create more governance artifacts than a small project needs;
- the current per-skill self-containment rule prevents the integrated stack
  from defining shared behaviour once;
- structural validation exists, but behavioural regressions in routing,
  proportionality, and instruction following are not represented by durable
  fixtures.

V2 must retain GOATED's rigor while making the normal path proportional,
coherent, and cheaper to load. It must remain useful as a standalone skill
stack while exposing stable conceptual seams that a future, separate
`goated-ai-factory` project can consume.

## Audience

- The maintainer, who currently develops and uses the stack.
- Users installing the complete GOATED stack into an agent framework.
- Users copying one GOATED skill without installing the complete stack.
- Future contributors or agents maintaining the public skill library.
- The future GOATED AI Factory, as a downstream consumer of stable V2
  concepts and registry data rather than a runtime dependency.

## Goals

- Reduce repeated instructions, discovery, routing, and closeout output.
- Make workflow depth adapt to task size, uncertainty, risk, continuity, and
  execution shape.
- Select gates centrally and re-evaluate them only at controlled checkpoints.
- Share compact evidence and decisions across selected skills.
- Preserve evidence-backed completion, scope control, privacy, approval, and
  readability standards without loading every specialist skill.
- Make integrated-stack installation the primary V2 experience.
- Keep individual skills safely and usefully operable when copied alone.
- Compress high-frequency skills without weakening behaviour.
- Add durable behavioural fixtures for routing and workflow conformance.
- Add Wayfinder for large, branching, multi-session decision work.
- Add lean knowledge retrieval for progressive, authority-aware use of durable
  project knowledge.
- Give the future Factory stable names and data concepts without implementing
  Factory orchestration here.

## Non-Goals

- Implementing the GOATED AI Factory.
- Adding Pi, Herdr, Hunk, Graphify, Ponytail, or another runtime dependency.
- Model selection, model tiering, provider routing, token pricing, runtime cost
  accounting, or model benchmarking.
- Worker sandboxes, worktrees, agent dashboards, persistent daemons, or
  executable multi-agent orchestration.
- Building a general workflow language or plugin system.
- Building semantic indexing, a vector database, or an Obsidian integration
  for `knowledge-retrieval`.
- Building a dedicated `evaluate-agent-skills` skill in the initial V2 scope.
  That may become a separate future ticket if real usage demonstrates a need.
- Adding dependency review, release readiness, performance investigation, data
  migration planning, research ledgers, or platform publishing skills during
  the initial V2 optimization.
- Renaming historical V1 specs, issues, or archived artifacts.
- Maintaining parallel active V1 and V2 implementations indefinitely.

## Product Principles

### Proportional rigor

Correctness, safety, and honest evidence remain mandatory. Ceremony, artifact
depth, and specialist procedure loading must be proportional to the work.

### One owner per concern

- The shared policy owns universal behaviour.
- The registry owns cross-skill orchestration metadata.
- The router owns initial route selection and checkpoint re-evaluation.
- Each skill owns only its specialized procedure.
- Durable project artifacts own settled project knowledge.
- The main agent owns final judgment and user communication.

### Reuse before rediscovery

Skills must consume fresh envelope and evidence entries before repeating
orientation. New discovery should be targeted and appended as a delta.

### Principles do not imply prompt payloads

A discipline may apply universally without loading its full specialist skill.
For example, every completion claim needs matching evidence, but only complex
verification work requires the full verification controller.

### Factory-ready, not Factory-dependent

V2 concepts should be stable enough for a later runtime to enforce, but the
standalone stack must work through instructions, Markdown artifacts, and
framework-native capabilities.

## Installation Model

V2 supports two installation modes.

### Integrated stack

This is the recommended mode.

It includes:

- the selected GOATED skill folders;
- a shared GOATED policy, distributed as `stack/AGENTS.md`;
- the machine-readable `stack/goated-stack.yaml` registry;
- the registry schema;
- human-readable work-envelope and evidence templates;
- thin framework adaptation guidance.

The integrated policy may be merged into the target framework's applicable
instruction artifact. `AGENTS.md` is the default Codex/Pi-compatible template,
not a claim that every framework uses that filename.

### Individual skill

A copied skill remains useful without the integrated stack. It retains:

- activation and non-activation guidance;
- its specialized procedure;
- task-specific evidence and safety constraints;
- a compact standalone fallback.

It does not repeat the entire GOATED philosophy, routing graph, delegation
policy, or global closeout contract.

## Integrated Stack Layout

The initial source layout is:

```text
stack/
  AGENTS.md
  goated-stack.yaml
  schemas/
    stack-registry.schema.json
  templates/
    work-envelope.md
    evidence-entry.md

skills/
  agent-workflows/
  engineering/
  productivity/
```

The initial V2 release must not add formal work-envelope or evidence-entry JSON
Schemas. Their Markdown contracts should be tested through use before their
shapes are frozen.

## Shared Core Policy

`stack/AGENTS.md` defines universal integrated-stack behaviour:

- instruction precedence and project-boundary handling;
- adaptive profile classification and proportionality;
- work-envelope and shared-evidence rules;
- preservation of user changes and scope control;
- risk-adaptive approvals and action reach;
- privacy, credential, destructive-action, and external-action safeguards;
- main-agent ownership and bounded delegation;
- evidence-backed claims and honest uncertainty;
- readable, locally understandable code expectations;
- progress communication and consolidated closeouts;
- controlled route re-evaluation at checkpoints.

It must not contain complete specialist procedures or project-specific rules.
Target-project adapters remain thin and preserve stronger project instructions.

## Adaptive Work Profile

The router records independent dimensions, then derives workflow intensity.

### Core dimensions

| Dimension | Values |
| --- | --- |
| Task size | `tiny`, `standard`, `large` |
| Intent maturity | `fuzzy`, `scoped`, `implementation-ready` |
| Workflow intensity | `lightweight`, `standard`, `full` |
| Continuity | `single-session`, `resumable` |
| Execution | `single-agent`, `delegated` |
| Domain | `software`, `research`, `documentation`, `content`, `other` |
| Data sensitivity | `public`, `private`, `restricted` |
| Action reach | `read-only`, `session-local`, `project-changing`, `external-changing` |

Risk is represented by flags rather than one mutually exclusive level. Initial
flags include:

- architectural;
- security;
- privacy;
- destructive;
- external-change;
- persistent-data;
- dependency;
- public-facing.

Model capability, provider, price, resource tier, and runtime cost do not belong
in the standalone V2 profile.

## Work Envelope

The work envelope is a logical state protocol, not a mandatory tracked file.

### Required core

```yaml
schema_version:
goal:
profile:
  task_size:
  intent_maturity:
  workflow_intensity:
  domain:
  risk_flags: []
  continuity:
  execution:
data_sensitivity:
action_reach:
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

### Optional extensions

- fixed point;
- approvals;
- artifacts;
- delegated work;
- route signals;
- risks;
- changes;
- resume information.

Runtime cost, provider, model-ranking, and Factory metric fields are excluded.
Irrelevant optional fields and meaningless skipped gates must be omitted.

### Storage

- Single-session work uses compact conversation or framework-native state.
- Resumable work uses
  `.local/goated/work-envelopes/<effort-slug>.md` after confirming `.local/`
  is ignored.
- A handoff copies only active decisions and evidence references needed to
  resume.
- Nothing is tracked unless the user deliberately promotes it into a durable
  artifact.

## Shared Evidence

Evidence entries are compact references rather than copied source content.

Each entry records, when applicable:

- path or identifier;
- relevance;
- applicable scope;
- key finding or constraint;
- provenance;
- freshness marker such as commit, modification time, or retrieval date;
- confidence or unresolved uncertainty.

Downstream skills reuse evidence unless:

- required evidence has not been collected;
- the source changed;
- the entry is stale or too shallow for the intended claim;
- contradictory evidence appears.

Project changes invalidate affected entries at the post-implementation
checkpoint. Current source and executable evidence outrank summaries for exact
or high-risk claims.

## Central Routing And Checkpoints

`using-goated-ai-skills` remains the human- and agent-readable router.

It must:

1. classify the initial work profile;
2. initialize or reuse the work envelope;
3. select required, conditional, and meaningfully skipped gates;
4. continue without a visible route report unless the route, approval, or risk
   materially matters to the user;
5. re-evaluate the route only at controlled checkpoints.

Initial checkpoints are:

- after clarification or diagnosis;
- after planning;
- after implementation;
- before final completion.

Individual skills may emit signals such as changed scope, stale evidence,
security impact, documentation impact, or refinement debt. They must not
silently reconstruct or activate a long downstream pipeline.

## Delivery Gate Matrix

| Gate | Activation |
| --- | --- |
| Proportional orientation | Always, with near-zero ceremony when fresh evidence exists |
| Grill | Intent, criteria, terminology, or tradeoffs remain materially unclear |
| Wayfinder | Uncertainty is branching and exceeds one focused session |
| Write a spec | Product or delivery intent needs a durable contract |
| Architecture design | Module, interface, ownership, data flow, or dependency strategy must be settled |
| Spec to tickets | A settled spec needs multiple resumable vertical slices |
| Writing plan | A scoped ticket still needs executable implementation steps |
| TDD | Behaviour, public interfaces, or regression risk change and a practical test surface exists |
| Code refinement | Concrete refinement debt is observed |
| Standards/spec review | Scope fit, acceptance coverage, or project conventions remain meaningfully uncertain |
| Security review | A trust boundary or security-sensitive surface changes |
| Documentation sync | Durable behaviour, interfaces, configuration, architecture, or operator expectations change |
| Full verification controller | Work is complex, high-risk, delegated, multi-surface, or explicitly audited |
| Handoff | Work is resumable, interrupted, delegated across sessions, or unfinished |

Workflow intensity changes depth, not correctness:

- `lightweight` uses direct work and narrow proof;
- `standard` uses compact orientation, just-in-time planning, appropriate proof,
  and conditional closeout gates;
- `full` uses durable clarification and planning, explicit checkpoints,
  specialist review, and resumability.

## Onboarding Profiles

Onboarding profiles set an artifact budget and expected depth. They do not
mandate empty governance documents.

### Lightweight

- Intended for small projects, one-off work, or one agent.
- Merge the shared policy and add thin project routing.
- Reuse existing documentation.
- Create no separate context, standards, or source-map artifact without a
  demonstrated need.

### Standard

- Intended for repeated agent work, medium repositories, or several relevant
  source areas.
- Use one shared onboarding evidence bundle.
- Create only artifacts that solve demonstrated retrieval, terminology, or
  standards problems.
- Refresh existing context maps, project context, and standards incrementally
  instead of rebuilding them.
- Record provenance and freshness for inferred standards so observations do
  not silently harden into permanent rules.

### Full

- Intended for large, public, multi-agent, regulated, security-sensitive, or
  architecture-heavy projects.
- Use stronger provenance, freshness, governance, architecture, and
  resumability support.
- Still omit artifacts that add no decision or retrieval value.

An onboarding effort may be promoted when discovery reveals greater complexity
or risk. The reason is recorded in the envelope.

## Approval Policy

V2 uses a risk-adaptive default:

- reads and safe diagnostics proceed automatically;
- planned project writes may receive one batch approval;
- approved work proceeds within its agreed scope;
- destructive operations, credentials, external publication, deployment,
  protected-branch changes, and actions exceeding an agreed constraint require
  explicit approval;
- a scope or action-reach change invalidates prior approval where relevant.

The user or project may select:

- `confirm-each-write`;
- `approve-batch`;
- `standing-session-consent`;
- `draft-without-applying`.

An individual skill must not request the same approval again when current
consent already covers its write scope and action reach. It must request fresh
approval when either materially changes.

The policy describes expected behaviour. The host framework determines which
parts can be technically enforced.

## Output And Communication

Skills update the work envelope with deltas:

- result;
- new evidence;
- changes;
- new or resolved risks;
- route signals;
- skipped or unavailable checks.

The main agent produces one consolidated final task response. Intermediate
reports are reserved for decisions, blockers, material scope or risk changes,
and useful progress updates during long work.

Artifact-producing skills retain artifact-specific schemas. Review skills retain
structured findings. Empty fields are omitted unless omission would mislead.
Standalone invocation returns a compact local closeout.

## Skill Anatomy

V2 validation checks semantic responsibilities rather than requiring identical
headings.

Every skill must provide:

- purpose;
- activation and non-activation conditions;
- inputs;
- specialized procedure;
- observable result or artifact;
- route signals;
- task-specific guardrails;
- compact standalone fallback;
- references when needed.

Conditional content includes:

- real hard requirements or optional capabilities;
- delegation rules only when the skill defines delegated work;
- compatibility notes only for real framework differences;
- detailed schemas only when structure is the product.

Skills must not repeat the global policy, reconstruct the downstream route, or
produce a full closeout solely for template uniformity.

## Compression Policy

Soft word budgets are:

| Skill type | Target |
| --- | --- |
| Style toggle or simple router | 250-700 words |
| Focused operational skill | 700-1,200 words |
| Complex controller | 1,200-1,500 words |
| Shared core policy | 800-1,200 words |

Content above 1,500 words requires a decomposition or recorded justification.
The validator reports budget status but does not fail solely on a soft limit.

Tables, schemas, enums, and concise decision maps should communicate dense
information when they remain readable. Compression succeeds only when
behavioural fixtures show that intended behaviour was preserved.

Initial compression targets are:

- `using-goated-ai-skills`;
- `session-start-progressive-disclosure`;
- `verification-before-completion`;
- `caveman`;
- repeated cross-cutting sections throughout the stack.

## High-Frequency Skill Changes

### Session orientation

The shared policy owns proportional orientation. The full
`session-start-progressive-disclosure` skill loads only for unfamiliar,
cross-area, stale, or boundary-uncertain work. It initializes or refreshes the
envelope silently unless it finds a conflict, missing decision, or material
route change.

### Grilling

`grill-me` and `grill-with-docs` support:

- `focused`: one dependent or high-risk decision at a time;
- `rapid`: up to three tightly related questions;
- `recommend-and-proceed`: provisional defaults for reversible, low-risk
  choices;
- `deep-dive`: no preset question limit for major architecture, fuzzy products,
  and other decision-complete work.

Question budgets follow workflow intensity, except that deep-dive mode follows
the material decision tree until shared understanding is reached.

### TDD

Test-first remains the default for bug fixes, behavioural changes, public
interfaces, and regression prevention when a practical automated surface
exists.

The test type follows the smallest stable observable boundary: unit, property,
component, contract, integration, or end-to-end. Integration tests are not
preferred by default. Equivalent proof is allowed when automated TDD is
genuinely unsuitable, with the reason recorded in the envelope.

### Code refinement

`code-refinement` is removed from every default run-or-explicit-skip pipeline.

The full skill activates only for:

- an explicit cleanup request;
- substantially generated or agent-written code needing focused review;
- observed duplication, confusing names, excessive branching, unnecessary
  abstraction, shallow indirection, or difficult local reasoning;
- an accepted review finding requiring behaviour-preserving cleanup.

Normal readability review remains in the shared policy, and TDD retains its
local refactor-after-green step.

### Verification, reviews, and documentation

Universal consideration does not require universal specialist loading:

- narrow work verifies directly from the shared policy;
- full verification is conditional;
- documentation impact is always considered, but `doc-sync` loads only for
  plausible durable drift;
- standards/spec and security review load only for matching uncertainty or
  risk;
- readability does not automatically activate refinement.

### Direct transitions and narrow fast paths

- When the user asked to fix a bug, `diagnose` hands an established root cause
  directly into the proof and implementation route without treating the fix as
  a new authorization request. A material scope or action-reach change still
  requires checkpoint review.
- `doc-sync` returns through a compact no-durable-impact path when the changed
  facts do not require documentation edits.
- `commit-message` produces message text only unless the user separately asks
  to stage, commit, push, or generate operational commands.
- `goated-prompt` puts the finished prompt first and makes structural
  explanation optional.
- `caveman` controls response verbosity only. It does not weaken implementation
  design, evidence, safety, or required artifact detail.
- `subagent-driven-development` activates only after a concrete task board or
  scoped set of independently ownable work exists. Overlapping write scopes or
  unsettled shared interfaces remain sequential.

## Proportional Planning Artifacts

`write-a-spec` supports:

- `compact`: problem, goals, non-goals, requirements, acceptance criteria,
  constraints, and open questions;
- `full`: adds the stakeholder, architectural, rollout, migration, analytics,
  and risk depth justified by larger work.

`writing-plans` supports:

- `inline`: an ordered plan held in the envelope for focused work;
- `durable`: a tracked plan for resumable, delegated, architectural, or
  multi-surface work.

Existing project conventions win. Empty template sections are omitted. Compact
artifacts can be promoted without restarting discovery.

## Canonical V2 Vocabulary And Renames

| V1 name | V2 canonical name |
| --- | --- |
| `write-a-prd` | `write-a-spec` |
| `prd-to-issues` | `spec-to-tickets` |
| `plan-codebase-architecture` | `design-codebase-architecture` |
| `improve-codebase-architecture` | `review-codebase-architecture` |

The registry preserves old names as aliases that resolve to exactly one
canonical skill. Duplicate alias skill folders are not created.

A spec is a scoped product or delivery contract. A PRD is one possible spec
form. A ticket is a portable dependency-aware work unit. A remote issue is one
possible tracker representation of a ticket.

Default target-project paths, when no local convention exists, are:

- specs: `docs/specs/<YYYY-MM-DD>-<slug>.md`;
- delivery tickets: `tickets/NNN-<short-title>.md`;
- multi-ticket order:
  `tickets/<spec-slug>-order.md`.

## Continuity

Default V2 local continuity paths are:

```text
.local/goated/work-envelopes/<effort-slug>.md
.local/goated/handoffs/<effort-slug>.md
```

The workflow verifies that `.local/` is ignored before placing private or
session state there. OS temp is the fallback when the project should not be
modified or lacks a safe ignored workspace. Tracked handoffs require explicit
intent.

Handoffs reference existing specs, tickets, maps, evidence, and commits rather
than duplicating them.

## Wayfinder

`wayfinder` is a new `agent-workflows` skill for large, branching,
multi-session uncertainty.

### Activation

Use it when:

- the destination spans multiple focused sessions;
- later decisions depend materially on earlier answers;
- research, prototypes, human decisions, or prerequisites must be coordinated;
- the complete route cannot responsibly be specified yet.

Do not use it for session-sized discussion or large implementation whose
decisions are already settled.

The router may recommend Wayfinder, but chart creation requires approval of the
proposed destination, location, visible frontier, action reach, and initial
write scope.

### Boundaries

- Wayfinder resolves uncertainty and produces decisions.
- Research and disposable prototypes are allowed as decision evidence.
- Bounded prerequisites are allowed only when necessary to make a decision
  possible and approval permits them.
- Production implementation, migration execution, publishing, and deployment
  never occur inside Wayfinder.

### Portable artifacts

When no configured tracker is used:

```text
docs/wayfinding/<effort-slug>/
  map.md
  decisions/
    001-<decision-title>.md
```

The map contains:

- destination;
- standing notes and constraints;
- decisions so far;
- current frontier;
- not yet specified;
- out of scope.

Decision tickets are separate from delivery tickets. They record:

- type: `grilling`, `research`, `prototype`, or `prerequisite`;
- mode: `AFK` or `HITL`;
- status;
- blockers;
- question;
- evidence or asset links;
- resolution.

### Lifecycle

Wayfinder:

1. names the destination and its completion condition;
2. charts only currently precise questions;
3. resolves one primary decision focus per invocation;
4. advances the frontier and promotes newly clarified fog;
5. hands settled evidence to the destination workflow without restarting
   discovery.

Map states are:

- `active`;
- `blocked`;
- `on-hold`;
- `destination-ready`;
- `completed`;
- `dropped`.

Blocked, on-hold, and dropped states record their reason and appropriate resume,
review, or replacement information. A map is completed only after its named
destination exists and is linked.

## Knowledge Retrieval

`knowledge-retrieval` is a lean, read-only skill that:

- searches project knowledge progressively;
- ranks results by authority, relevance, confidence, maturity, and freshness;
- distinguishes authoritative evidence, historical decisions, captured
  observations, inference, brainstorming, and stale material;
- adds retrieved paths and provenance to the shared evidence bundle;
- reports conflicts and stale notes;
- recommends later capture or nurturing without mutating knowledge.

Ordinary files are the default. Obsidian, connectors, semantic search, and
databases are optional capabilities, not dependencies. External web research is
outside this skill's responsibility.

## Behavioural Fixtures And Validation

Structural validation remains separate from behavioural conformance.

V2 adds portable, versioned fixtures that describe:

- user request and minimal project context;
- expected profile and workflow intensity;
- required, conditional, and skipped gates;
- expected route signals;
- prohibited behaviour;
- evidence and closeout expectations;
- output or loaded-context budget where useful.

Initial end-to-end scenarios are:

1. feature brief to planned, implemented, reviewed, and verified change;
2. bug report to diagnosis, root-cause fix, regression proof, and review;
3. product idea to scoped spec, architecture, and vertical slice;
4. existing codebase to proportional onboarding.

Focused fixtures include:

- tiny-task bypass;
- conflicting skill triggers;
- checkpoint risk escalation;
- restricted data;
- external-changing actions;
- conditional code refinement;
- individual-skill fallback without the shared policy;
- Wayfinder selection and rejection boundaries;
- Wayfinder state transitions and destination handoff.

The initial V2 scope includes fixtures, deterministic assertions where
practical, and documented manual or host-driven comparison. It does not include
a dedicated evaluation skill or general model benchmark platform.

## Registry

`stack/goated-stack.yaml` is the integrated stack's portable machine-readable
catalog.

It owns:

- canonical skill names and paths;
- aliases;
- workflow role or gate type;
- applicable domains;
- profile eligibility;
- accepted and emitted route signals;
- shared policy and envelope contract versions.

It must not duplicate full procedures, guardrails, or trigger prose from
skills. `SKILL.md` remains authoritative for how a skill performs its work.

The validator checks:

- registry schema;
- referenced skill existence;
- canonical-name uniqueness;
- alias resolution;
- signal definitions;
- category and path consistency;
- word-budget reporting;
- relevant fixture structure.

## Requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| V2-001 | Ship integrated and individual installation modes | Must |
| V2-002 | Add the shared GOATED policy and portable registry | Must |
| V2-003 | Centralize initial gate selection and checkpoint re-evaluation | Must |
| V2-004 | Add the compact work-envelope and shared-evidence conventions | Must |
| V2-005 | Add adaptive profiles, risk flags, data sensitivity, and action reach | Must |
| V2-006 | Replace repeated closeouts with internal deltas and one task closeout | Must |
| V2-007 | Add artifact-budget onboarding profiles | Must |
| V2-008 | Remove mandatory code-refinement activation | Must |
| V2-009 | Separate universal disciplines from specialist skill loading | Must |
| V2-010 | Compress high-frequency skills under soft budgets without behavioural loss | Must |
| V2-011 | Adopt semantic, non-boilerplate skill anatomy | Must |
| V2-012 | Rename the four canonical skills and provide registry aliases | Must |
| V2-013 | Adopt spec, ticket, continuity, envelope, and Wayfinder artifact conventions | Must |
| V2-014 | Add Wayfinder | Must |
| V2-015 | Add lean knowledge retrieval | Must |
| V2-016 | Add portable behavioural fixtures without a dedicated evaluation skill | Must |
| V2-017 | Update validator, docs, context, standards, and installation guidance | Must |
| V2-018 | Preserve V1 history and provide concise migration guidance | Should |
| V2-019 | Add a V2 ADR superseding conflicting V1 installation assumptions | Must |
| V2-020 | Support configurable approval modes with risk-adaptive defaults | Must |
| V2-021 | Apply the accepted direct-transition and narrow-fast-path refinements | Should |

## Acceptance Criteria

### Integrated stack

- [ ] `stack/AGENTS.md` contains the shared V2 policy without specialist
      workflow duplication.
- [ ] `stack/goated-stack.yaml` validates against one registry schema.
- [ ] Every canonical skill and alias resolves consistently.
- [ ] Integrated installation instructions explain how to merge the shared
      policy without overwriting stronger project rules.
- [ ] An individual copied skill remains safely usable without the registry.

### Routing and proportionality

- [ ] The router produces or updates the compact profile, route, and evidence
      state without mandatory visible ceremony.
- [ ] Checkpoint signals can add, remove, or preserve gates with recorded
      reasons.
- [ ] Tiny work bypasses full onboarding and specialist pipelines.
- [ ] Standard and full workflows select only justified gates.
- [ ] No individual skill independently reconstructs the entire downstream
      route.
- [ ] Existing approval covers downstream writes until scope or action reach
      materially changes.

### Shared state and discovery

- [ ] Work-envelope and evidence templates implement the required contracts
      without formal JSON Schemas.
- [ ] Fresh evidence is reused across sequential skills.
- [ ] A source change can invalidate affected evidence.
- [ ] Resumable state defaults to ignored project-local paths with an OS-temp
      fallback.

### Skill contracts

- [ ] `code-refinement` activates only from explicit request or observed debt.
- [ ] TDD selects the smallest stable proof surface rather than preferring
      integration tests.
- [ ] Grill workflows support focused, rapid, recommend-and-proceed, and
      deep-dive modes.
- [ ] Session orientation is conditional and normally silent.
- [ ] Verification, security, standards, and documentation specialist skills
      activate only from matching scope, risk, or uncertainty.
- [ ] Empty boilerplate sections and repeated global rules are removed.
- [ ] Diagnosis can continue into an already-requested fix without a redundant
      authorization pause.
- [ ] Documentation sync has a compact no-durable-impact result.
- [ ] Commit messages default to message-only output.
- [ ] Prompt crafting puts the finished prompt first.
- [ ] Caveman changes response verbosity without weakening implementation.
- [ ] Delegated development requires a concrete non-overlapping task board.

### Artifacts and new skills

- [ ] Specs and delivery tickets use the new vocabulary and fallback paths.
- [ ] Canonical renames are reflected across skills, docs, registry, and
      fixtures.
- [ ] Wayfinder passes its selection, rejection, state, fog/frontier,
      no-execution, and handoff scenarios.
- [ ] Knowledge retrieval remains read-only, progressive, authority-aware, and
      provider-neutral.

### Compression and conformance

- [ ] The validator reports soft word-budget status.
- [ ] High-frequency integrated routes load materially less instruction text
      than their V1 equivalents.
- [ ] Behavioural fixtures cover the four approved end-to-end scenarios and
      focused routing risks.
- [ ] Compression comparisons identify any lost safety, routing, evidence, or
      completion behaviour before V2 is accepted.
- [ ] No dedicated `evaluate-agent-skills` skill is required for initial V2
      acceptance.

### Documentation and migration

- [ ] A V2 ADR explicitly supersedes conflicting parts of ADR 0001.
- [ ] `AGENT.md`, `CONTEXT.md`, root docs, category indexes, install guidance,
      and operator guidance describe V2 consistently.
- [ ] Historical V1 specs and archived issues remain intact.
- [ ] A concise migration guide covers install mode, renamed skills, aliases,
      artifact paths, and removed mandatory gates.

## Implementation Notes

- Preserve V1 before breaking implementation begins, using a lightweight tag or
  equivalent snapshot.
- Implement vertical slices rather than rewriting every skill before any
  behaviour can be checked.
- Establish fixtures and baseline observations before aggressively compressing
  high-frequency skills.
- Add the shared policy, registry, router, envelope, and evidence conventions
  before migrating dependent skills.
- Prefer generated or validator-checked alias resolution over duplicate skill
  folders.
- Keep exact wording, enum expansion, and file-by-file migration steps in
  implementation tickets and plans.
- Do not add Factory-only fields merely because the future runtime may need
  them; the Factory can extend the portable core later.

## Testing And Verification

- Run the existing skill validator throughout migration.
- Extend validator coverage for the registry, aliases, signals, semantic skill
  requirements, fixture structure, and soft word-budget reporting.
- Record V1 baseline instruction sizes for representative routes.
- Compare compressed V2 routes against the behavioural fixtures.
- Test integrated-stack and individual-skill installation scenarios.
- Test Markdown work-envelope and evidence reuse across at least one multi-skill
  workflow.
- Test resumable local state only in an ignored path.
- Manually review public docs for terminology and V1/V2 boundary drift.
- Run targeted link, renamed-reference, and stale-pipeline scans before
  acceptance.

## Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Shared policy becomes another large prompt | Recreates context cost centrally | Enforce a soft budget and keep specialist procedures out |
| Registry and prose drift | Wrong routing or broken aliases | Make ownership boundaries explicit and validate cross-references |
| Envelope becomes mandatory ceremony | Small tasks become slower | Keep it logical and compact; omit irrelevant fields |
| Compression removes behaviour | Safety or rigor regresses | Establish fixtures and baselines before accepting compression |
| Too many profile fields confuse routing | Classification overhead replaces pipeline overhead | Keep values small and remove Factory-only metadata |
| Individual fallback becomes unsafe or bloated | Standalone mode is weak or duplicates V1 | Retain only task-critical fallback behaviour |
| Wayfinder is used for every large task | Planning becomes a ticket maze | Require branching uncertainty, not implementation size alone |
| Local Wayfinder concurrency is treated as enforced | Conflicting claims or edits | Describe local claims as advisory and use tracker/runtime enforcement only when available |
| Renames create stale references | Broken routing and docs | Registry aliases, targeted scans, and concise migration guidance |
| Formal schemas freeze immature concepts | Premature compatibility burden | Validate only the registry initially |
| V2 absorbs Factory scope | Standalone stack becomes infrastructure-heavy | Enforce explicit non-goals and portable seams |

## Open Questions

No unresolved product decision currently blocks ticket breakdown.

Implementation tickets may refine:

- exact registry field names and route-signal vocabulary;
- the smallest useful standalone fallback capsule;
- the precise fixture serialization and host-driven comparison method;
- whether real usage later justifies formal envelope/evidence schemas;
- whether a future dedicated `evaluate-agent-skills` skill earns its place.

These decisions must preserve the contracts and non-goals in this spec.

## Source Evidence

- `AGENT.md` — current source-repo maintainer contract.
- `CONTEXT.md` — V1 product vocabulary and portability model.
- `README.md` — current distribution, workflow, catalog, and attribution.
- `docs/install.md` — current docs-first installation behaviour.
- `docs/how-to-use.md` — current onboarding and delivery pipelines.
- `docs/agents/context-matrix.md` — source routing for this repository.
- `docs/agents/project-standards.md` — documented and inferred repository
  standards.
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` — V1 decision
  that V2 must explicitly supersede where conflicting.
- `issues/prd-goated-ai-skills-v1-public-core.md` — current V1 product contract.
- Current implemented skills and targeted scans for repeated routing,
  self-containment, handoff, naming, and code-refinement rules.
- User-provided GOATED AI Skills upgrade analysis and the decisions settled
  through the V2 `grill-with-docs` session on 2026-07-24 and 2026-07-25.
- User-provided Wayfinder source used only as inspiration for a from-scratch
  GOATED workflow; broader project inspiration attribution already exists in
  the repository README.
