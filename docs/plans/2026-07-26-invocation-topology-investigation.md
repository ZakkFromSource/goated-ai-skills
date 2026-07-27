# Invocation Topology Investigation Plan

## Plan Target

- Ticket: `tickets/archive/021-investigate-invocation-topology.md`.
- Parent spec:
  `docs/specs/2026-07-26-selective-upstream-skill-adoption.md`, requirement R6
  and acceptance criterion AC6.
- Mode: durable tracked plan because the work is delegated, spans current host
  research and a real consumer experiment, and ends at a maintainer decision
  gate.
- Execution route: source-grounded research plus a disposable
  logic/state/data/API prototype, followed by standards/spec review and full
  verification.

## Source Inspected

- Maintainer and product contracts: `AGENT.md`, `CONTEXT.md`, `README.md`,
  `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, and
  `stack/AGENTS.md`.
- Approved delivery artifacts: the ticket and parent spec above, archived
  Ticket 019, and
  `tickets/archive/022-implement-invocation-topology.md`.
- Existing installation and automation decisions: `docs/install.md`,
  `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`,
  `docs/adr/0002-v2-integrated-stack-foundation.md`,
  `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`, and
  `issues/archive/043-research-skill-trigger-eval-harnesses.md`.
- Current catalog and routing surfaces: `stack/goated-stack.yaml`,
  `stack/schemas/stack-registry.schema.json`,
  `skills/agent-workflows/using-goated-ai-skills/SKILL.md`,
  `skills/agent-workflows/agent-instructions-integrator/SKILL.md`, and
  `scripts/validate_skills.py`.
- Current Codex documentation: the dated Codex manual's skill discovery,
  progressive-disclosure, explicit/implicit invocation, local skill location,
  disable, and `agents/openai.yaml` policy sections. Claude Code and generic
  Agent Skills primary-source reads are delegated and must be reviewed before
  synthesis.

## Research And Prototype Contract

- Research question: which parts of the neutral candidate semantics
  `autonomous`, `router-only`, `manual-only`, and `reference-only` can Codex,
  Claude Code, and a generic Agent Skills host enforce today?
- Decision use: determine whether Ticket 022 should add production metadata,
  which product surface would consume it, and which host should be the first
  supported consumer.
- Currency: host claims must use current primary documentation or current
  source retrieved on 2026-07-26.
- Prototype question: can a thin Codex installation adapter faithfully
  translate all four neutral semantics into observed current-host behavior,
  and which distinctions fail closed?
- Prototype branch: logic/state/data/API.
- Prototype shape: an ignored local translation harness plus short-lived
  repository-scoped Codex probe skills. The report will preserve inputs,
  commands, observations, and cleanup state; no prototype runtime, plugin,
  generated manifest, or installer will become a production artifact.

## Slice Shape And Interface Focus

This slice produces one dated decision report at
`docs/invocation-topology-decision-report.md`. The report is the stable
interface between investigation Ticket 021 and any separately approved
implementation Ticket 022. It will keep neutral semantics separate from host
adapters and will assess catalog visibility, implicit selection, explicit
selection, router reachability, and context cost independently.

The disposable experiment may use `.local/scratch/` after verified ignore
coverage. Any temporary `.agents/skills/` probes must be marked as prototypes
and removed after their observed runs.

## Assumptions

- The current GOATED registry is catalog data only; it has no invocation
  consumer and must remain unchanged in this ticket.
- Current host documentation can establish supported configuration behavior,
  but only an observed host run can supply runtime/model evidence.
- A failed or unavailable host run is a capability limit, not permission to
  replace runtime evidence with a static fixture.
- The maintainer, not the investigation, owns the final `go`, `revise`, or
  `no-go` decision and first-consumer selection.

## Stop Conditions

- Stop before any production registry, schema, validator, installed skill,
  plugin package, marketplace, installer, or runtime-bootstrap change.
- Pause if a real-host experiment requires credentials, global installation,
  publication, protected configuration, or another action reach not already
  covered by the ticket.
- Preserve disagreements when current primary sources do not settle a host
  mapping; do not infer cross-framework support.
- Stop or narrow the probe if Codex cannot isolate the prototype from normal
  project behavior, if model output could expose private context, or if
  repeated runs cannot distinguish the tested behaviors.
- Do not mark Ticket 021 complete until the maintainer records the required
  decision.

## Steps

1. Build a dated claim matrix from current GOATED source and current official
   Codex, Claude Code, and Agent Skills sources. Record source, applicable
   scope, freshness, finding, confidence, inference, and unavailable evidence.
2. Define each neutral semantic and its safe fallback. Map the five independent
   dimensions—catalog visibility, implicit selection, explicit selection,
   router reachability, and context cost—before translating any host-specific
   fields.
3. Create the ignored Codex adapter harness and probe inputs. Have the adapter
   emit faithful mappings only and explicit unsupported results where Codex
   lacks a caller-aware or non-invokable skill mechanism.
4. Run supported and unsupported probes in a fresh real Codex consumer where
   available. Record the exact prompt, detected skill form, host/app version,
   output, retries, limitations, and whether each observation is documentation,
   deterministic adapter output, or probabilistic model behavior.
5. Write `docs/invocation-topology-decision-report.md` with the neutral
   contract, source matrix, host mappings, experiment record, product-ownership
   analysis, recommendation, residual risk, and an explicit maintainer
   decision gate.
6. Remove short-lived discovered skill probes or leave only an ignored
   prototype handoff when maintainer inspection is still required. Report the
   cleanup trigger and owner.
7. Review the report against R6, AC6, every Ticket 021 acceptance criterion,
   current ADR boundaries, public safety, citation scope, and the distinction
   between fixtures, adapter checks, and runtime/model evidence.
8. Run focused prototype checks, `uv run python scripts/validate_skills.py`,
   `uv run python -m unittest discover -s tests -v`, `git diff --check`, a
   targeted stale-claim scan, manual Markdown/link review, and
   `git status --short`. Report failures, skipped checks, and residual risk
   exactly, then present the maintainer decision gate.

## Acceptance Coverage

Steps 1-2 cover neutral definitions, fallbacks, current primary-source host
mappings, and the five required invocation dimensions. Steps 3-4 provide one
real consumer experiment while keeping deterministic translation, static
fixtures, and model behavior distinct. Step 5 identifies the correct future
product surface and preserves unsupported behavior. Steps 6-8 cover
disposability, reproducibility, public boundaries, verification, and the
required maintainer decision.

## Residual Risk

- Model selection remains probabilistic even when a host configuration is
  deterministic; observed runs can demonstrate behavior but cannot prove every
  future model/session outcome.
- Codex access is available in the current desktop session, but packaged CLI
  execution may be unavailable from the shell. The experiment will record the
  exact usable consumer surface and any resulting gap.
- Claude Code may be documentable but unavailable for a local observed run;
  that host must remain source-backed rather than runtime-verified unless
  access is discovered.

## Completion Result

The investigation completed on 2026-07-27 with a maintainer **NO-GO**. The
Codex experiment verified the supported implicit/manual distinction, but the
maintainer determined that permanent registry and adapter complexity would
weaken GOATED's deliberately simple Codex workflow. No production metadata or
consumer was accepted. Ticket 022 closed without implementation, and any
future custom invocation harness requires a separate spec and approval.
