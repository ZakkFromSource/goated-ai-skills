# GOATED AI Skills Context

GOATED AI Skills is a public source library for reusable, installable AI skill folders. It should feel like a compact operating system for high-quality agent work, not a prompt dump.

## Domain Language

These definitions are normative for this source repo. If another public doc
uses these terms differently, treat that as documentation drift to resolve.
V1 terms describe the preserved historical release; V2 terms describe the
maintainer-accepted integrated stack.

### Project Boundaries

- **GOATED AI Skills** - the public source library of installable, framework-agnostic AI skill folders.
- **Source repo** - this public repository, used to publish, maintain, and document GOATED AI Skills. This repo is not a template that users must clone into every project.
- **Source repo maintenance** - work that changes this repository's docs, issues, skill folders, adapters, or maintainer artifacts.
- **Skill pack distribution** - Layer 0 of the product model: users clone, download, copy, install, or adapt skill folders from this repo into their own agent workflow.
- **Agent framework** - the tool or environment that discovers and runs skills, commands, prompts, or instructions, such as Codex, Claude Code, Hermes, OpenCode, or a generic tool-calling agent.
- **Installed skill** - a copied or installed skill folder inside a user's chosen agent framework. It must remain useful without loading this repo's root `AGENT.md`, `README.md`, or `CONTEXT.md`.
- **Installed skill stack** - the set of copied or installed GOATED skill folders available to an agent framework for one user or target project. The stack is routed by installed skill files, not by this source repo's root docs.
- **Target project** - a project where installed skills are used to do onboarding or delivery work. In public docs this usually means a user's downstream project; when this repo is the work target, source repo maintenance rules still win.

### V1 Workflow Model

- **Docs-first installation** - the V1 installation model: users manually copy, install, or adapt completed skill folders using documentation instead of installer automation.
- **Portable router** - an installed skill, currently `using-goated-ai-skills`, that classifies the task surface and points to the next GOATED skill or direct action without requiring runtime bootstrap, hooks, generated manifests, or source-repo root docs.
- **Human operator manual** - a public guide for people installing, adapting, or using the skill stack, such as `docs/how-to-use.md`. It summarizes routes and references but is not a runtime dependency for installed agents.
- **Target Project Onboarding** - preparing a target project for serious agent work by mapping sources, calibrating project context and standards, and routing the chosen agent framework to installed skills and durable project artifacts.
- **Target Project Delivery** - moving one target-project change from clarified intent through planning, architecture blueprinting when useful, implementation, verification, documentation, and handoff.
- **Public core workflow** - the portable V1 workflow set intended for public main, spanning onboarding and delivery without private project assumptions.
- **Tiny one-off task** - a small, obvious, low-risk request that does not need full onboarding or planning ceremony, such as a typo fix, one-line rename, or direct command the user already specified.

### V2 Integrated Stack Model

- **Integrated stack** - the recommended V2 installation mode: selected skill
  folders plus a shared policy, portable registry, registry schema, and
  human-readable state templates under `stack/`.
- **Shared policy** - universal installed-stack behavior distributed from
  `stack/AGENTS.md` and applied through a verified merge or explicit load from
  the target framework's active instructions.
- **Stack registry** - the versioned machine-readable catalog at
  `stack/goated-stack.yaml`; it owns cross-skill metadata but not specialist
  procedures.
- **Standalone fallback** - the compact activation, specialist procedure,
  evidence, safety, and result guidance that keeps an individually copied skill
  useful without the integrated policy or registry.
- **Work envelope** - compact logical task state shared across selected skills;
  it is not a mandatory tracked artifact.
- **Evidence entry** - a fresh, scoped reference to source or executable
  evidence that downstream skills can reuse without copying source content.
- **Onboarding artifact budget** - the selected set of onboarding artifacts
  justified by lightweight, standard, or full discovery; it is not a mandatory
  checklist.
- **Onboarding evidence bundle** - one set of provenance- and freshness-aware
  evidence entries reused across every selected onboarding artifact.

### Skill Anatomy

- **Skill** - a reusable workflow packaged as a skill folder with a `SKILL.md` file and any local support files that materially improve its power, reuse, progressive disclosure, or installability.
- **Skill folder** - a directory under `skills/<category>/<skill-name>/` that is copied or adapted as one installable unit.
- **`SKILL.md`** - the primary workflow file for an installed skill. It should act as the router and operating procedure, not the whole knowledge base.
- **Skill description** - the discovery-only `description` field in `SKILL.md` frontmatter. It should say when to load the skill using user requests, task conditions, symptoms, or project context; workflow details belong in the body.
- **Support files** - local files inside a skill folder, such as `references/`, `scripts/`, or `assets/`. They are not discouraged; add them when they make the skill more capable, easier to use, easier to verify, or easier to install without bloating `SKILL.md`.
- **`references/`** - support files inside a skill folder for detailed examples, prompt templates, checklists, stack-specific notes, anti-pattern catalogs, rationalization tables, or longer decision guides. Use them when detail would help the skill but should not sit in the main workflow.
- **`scripts/`** - executable helpers inside a skill folder. Use them when a repeatable operation is safer, clearer, or more powerful as a maintained script than as prose instructions.
- **`assets/`** - reusable assets inside a skill folder. Use them when examples, templates, fixtures, images, or other packaged materials improve the installed skill.
- **Lean schema** - the standards-first `SKILL.md` convention for implemented skills: top-level `name`, top-level `description`, and `metadata.goated-category`, with behavior preserved in body sections such as Purpose, Inputs, Dependencies, Workflow, Output Contract, Delegation, Guardrails, and References.
- **Trigger** - a user request pattern, task condition, or project situation that tells an agent when to use a skill.
- **Output** - the artifact, decision, summary, change, or verification result a skill is expected to produce.
- **Dependency** - another skill, project artifact, command, source, or workflow step the current skill requires, prefers, or can gracefully work without. Skill bodies should distinguish hard dependencies, soft dependencies, and fallback behavior when relevant.
- **Skill compatibility note** - a small framework-specific or environment-specific caveat for using a skill in Codex, Claude Code, Hermes, OpenCode, or a generic agent environment. Add one only when a real per-skill constraint exists; do not recreate generic adapter maps.
- **Thin adapter** - a short target-project or framework instruction layer that points agents to installed skills and durable project artifacts without copying full skill bodies or treating one framework's filename convention as universal.
- **Category** - the public V1 skill grouping, represented by folder path and `metadata.goated-category`. Allowed V1 categories are `agent-workflows`, `engineering`, and `productivity`.
- **Classification** - a historical source-repo portability label. Implemented skills no longer use `classification` as top-level frontmatter; use body text, issue notes, or review reports to discuss portability when needed.
- **Status** - a historical source-repo maturity label. Implemented skills no longer use `status` as top-level frontmatter; record maturity or deprecation decisions in docs or scoped issues when needed.
- **Discipline-heavy skill** - a skill that asks agents to resist shortcuts, verify claims, follow a strict process, or stop under pressure. These skills may need stop rules, proof gates, rationalization counters, red flags, or anti-pattern references.
- **Delegated status enum** - explicit status values used by delegated workflows, such as `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`, with controller behavior defined for each value. Use them when a subagent result can change the controller's next action; simple evidence scans can keep lighter evidence, assumption, uncertainty, and inspected-path requirements.
- **Project reproducibility gate** - a conditional route, currently owned by `setup-scribe`, selected when durable project setup knowledge is missing, changed, stale, or ready for replay automation; it is not a mandatory closeout step.
- **Setup evidence state** - a material setup step classification of `verified`, `source-backed`, or `unverified`; it describes the evidence for that step rather than the recipe as a whole.

### Artifacts

- **Spec** - a scoped product or delivery contract. A PRD is one possible spec form.
- **Delivery ticket** - a portable dependency-aware work unit, normally stored under `tickets/`; a remote issue is one possible tracker representation.
- **Wayfinder** - an uncertainty-navigation workflow for branching work that
  exceeds one focused session. It advances decisions and evidence toward a
  named planning destination but never performs production implementation,
  migration execution, publication, or deployment.
- **Wayfinder map** - a durable low-resolution index of a destination,
  completion condition, standing constraints, settled-decision pointers,
  visible frontier, not-yet-specified fog, and out-of-scope work. Without a
  configured tracker, it lives at `docs/wayfinding/<effort-slug>/map.md`.
- **Wayfinder decision record** - a decision artifact, distinct from a delivery
  ticket, with type `grilling`, `research`, `prototype`, or `prerequisite`;
  independent `AFK` or `HITL` mode; status, blockers, question, evidence links,
  and resolution.
- **Fresh-agent-ready ticket** - a local delivery ticket containing enough linked context, first reads, acceptance criteria, proof expectations, blockers, and exclusions for a future agent to start without hidden chat history, ignored notes, or unlinked upstream context.
- **PRD** - the V1 term for a product requirements document; historical V1 PRDs remain unchanged.
- **Issue handoff** - the V1 term for a local implementation slice under `issues/`; historical V1 issue handoffs remain unchanged.
- **AFK ticket** - a delivery ticket that can proceed without a required human decision, design review, credential, external access, or approval gate.
- **HITL ticket** - a delivery ticket that requires human-in-the-loop input before or during implementation, such as a product decision, design review, credential, external access, or approval.
- **Archived issue** - a completed implementation issue moved under `issues/archive/` after acceptance criteria are checked and any required user, maintainer, PR, or project-defined review is complete.
- **ADR** - an architectural decision record stored under `docs/adr/` when a durable architecture decision needs to be recorded.
- **Context matrix** - a durable target-project artifact, normally `docs/agents/context-matrix.md`, that tells future agents what to read first, second, and only if needed.
- **Project context file** - a durable target-project artifact, normally root `CONTEXT.md`, that defines project boundaries, domain language, durable artifact meanings, and shared architecture vocabulary for that target project. This is distinct from this source repo's root `CONTEXT.md`.
- **Project standards profile** - a durable target-project artifact, normally `docs/agents/project-standards.md`, that separates documented standards, inferred conventions, user-confirmed preferences, unresolved questions, and enforcement levels.
- **Architecture map** - a descriptive, source-grounded account of current modules, callers, flows, ownership, dependencies, or runtime topology. It does not prescribe changes or rank improvements.
- **Architecture plan** - a durable target-project artifact, normally `docs/agents/architecture-plan.md` for project-wide setup or `docs/architecture/<slug>-architecture-plan.md` for feature-specific work, that turns clarified intent into planned modules, interfaces, dependency seams, test surfaces, and implementation slice order.
- **Architecture review** - a review-only assessment of current architecture quality and improvement opportunities. It may route an accepted finding to architecture design, but does not itself produce the replacement blueprint.
- **Implementation plan** - an ordered, source-grounded execution route produced just in time. Inline mode stays in the work envelope for focused single-session work; durable mode is tracked for resumable, delegated, architectural, or multi-surface work. Promotion reuses fresh discovery, evidence, and settled decisions.
- **Setup recipe** - one ordered, tracked, current project-first guide for recreating a working environment. It owns prerequisites, sequencing, manual actions, verification, gaps, and links while manifests and configuration retain ownership of their detailed facts.
- **Agent instruction artifact** - a file or configuration entry that tells a specific agent framework how to use installed skills and target-project artifacts.
- **Durable artifact** - tracked project knowledge that should survive across sessions, such as specs, Wayfinder maps and decision records, ADRs, project context files, context matrices, standards profiles, architecture plans, and public docs.
- **Knowledge retrieval** - progressive read-only search of scoped durable
  project artifacts that ranks evidence for a claim by relevance, authority,
  freshness, confidence, and maturity; it reports stale or conflicting
  knowledge and never performs implicit note nurturing.
- **Source-grounded research** - read-only investigation of a current external
  question against a question-specific source hierarchy, with claim-scoped
  provenance, freshness, confidence, and uncertainty; durable Markdown capture
  is optional and reuses an existing project-owned convention.
- **Local/session artifact** - ignored, private, or temporary context, such as
  `.local/goated/`, `.local/scratch/`, OS temp
  `goated-handoffs/<project-name>/`, `.scratch/`, `tmp/`, or `temp/`.
- **Handoff** - a compact continuity note for a future agent or session.
  Resumable work defaults to verified-ignored
  `.local/goated/handoffs/<effort-slug>.md`; OS temp is the fallback when
  project-local state is inappropriate. Handoffs reference existing artifacts
  instead of duplicating PRDs, tickets, ADRs, diffs, or commits.

### Operating Principles

- **Progressive disclosure** - loading the smallest useful context first, then deeper references only when the task requires them.
- **Support-file bias** - future agents should not default against `references/`, `scripts/`, or `assets/`. Keep `SKILL.md` lean, but create support files whenever they genuinely improve skill capability, reuse, verification, or installability.
- **Self-contained skill** - in V1, a folder carrying its complete workflow
  guidance; in V2 individual mode, a folder retaining a compact standalone
  fallback without requiring the shared registry or this repo's root files.
- **Public-safe** - suitable for public main because it contains no private project names, handles, credentials, client data, sensitive personal domains, or private workflow assumptions.
- **Public core** - portable skills and docs safe for public use across compatible agents and target projects.
- **Private adaptation** - a private, domain-specific, or organization-specific extension that follows GOATED conventions outside public main.
- **Private fork/private deployment** - a non-public copy or installation of this skill library where private or domain-specific skills may live until deliberately sanitized for public contribution.
- **Subagent-aware** - written so bounded parts of the work can be delegated to subagents when available, with evidence returned to the main agent.
- **Single-agent-compatible** - still usable when no subagents are available; the main agent performs the same workflow sequentially with a narrower context budget.

### Architecture Design Language

These definitions guide architecture-related skills and target-project setup. GOATED AI Skills should bias future projects toward deep modules instead of many shallow modules, while still requiring source-grounded evidence before proposing refactors.

- **Deep-module bias** - the default architecture preference: build and refactor toward modules with small, meaningful interfaces that hide substantial behavior, rather than spreading behavior across many thin pass-through modules.
- **Module** - anything with an interface and an implementation, at any scale: function, class, package, feature slice, subsystem, or tier-spanning flow.
- **Interface** - everything a caller or test must know to use a module correctly, including types, methods, invariants, ordering constraints, error modes, configuration, and relevant performance expectations.
- **Implementation** - the code and internal structure behind a module's interface.
- **Depth** - the leverage provided by a module's interface: how much useful behavior callers can exercise per unit of interface they must understand.
- **Deep module** - a module where a small interface gives access to substantial, cohesive behavior and hides implementation complexity.
- **Shallow module** - a module whose interface is nearly as complex as its implementation, often passing complexity through to callers instead of hiding it.
- **Deepening** - refactoring one or more shallow or tightly coupled modules into a deeper module with a clearer interface, better locality, and a stronger test surface.
- **Architecture blueprinting** - planning modules, interfaces, dependency seams, data/state ownership, test surfaces, and implementation slices before code is written, using source evidence and clarified intent instead of speculative file trees.
- **Seam** - the place where a module's interface lives and where behavior can vary without editing the caller. Use `seam` for this architecture concept instead of the overloaded word `boundary`.
- **Architecture adapter** - a concrete implementation that satisfies an interface at a seam, usually for a production dependency, test stand-in, or external service.
- **Port** - an interface introduced at a real seam so a deep module can own the logic while production and test architecture adapters provide different dependency behavior.
- **Leverage** - what callers gain from depth: more capability and behavior per interface fact they must learn.
- **Locality** - what maintainers gain from depth: change, bugs, knowledge, and verification concentrate in one module instead of scattering across callers.
- **Deletion test** - a check for whether a module earns its place: if deleting the module makes its complexity reappear across callers, it was hiding useful behavior; if the complexity simply disappears, it was likely shallow pass-through.
- **Interface-as-test-surface** - tests should exercise observable behavior through the module's interface. Tests that must reach past the interface usually indicate the module shape or seam placement needs attention.
- **Internal seam** - a seam used inside a deep module's implementation, often for private composition or focused internal tests. It should not leak through the external interface just because tests use it.
- **External seam** - the seam exposed to callers and tests as the module's interface.
- **In-process dependency** - pure computation or in-memory state with no I/O; usually deepenable directly without adapters.
- **Local-substitutable dependency** - a dependency with a faithful local test stand-in, such as an in-memory filesystem or local database substitute.
- **Remote-owned dependency** - a networked dependency the project or organization controls; prefer a port with production and in-memory/test adapters when deepening across it.
- **True external dependency** - a third-party service outside the project's control; inject it through a port and use a mock or fake adapter in tests.
- **Real seam rule** - introduce ports and architecture adapters only when behavior genuinely varies across the seam, usually because at least production and test adapters both exist. A seam with only one adapter is often unnecessary indirection.
- **Replace-don't-layer testing** - after deepening, prefer tests at the new module interface and delete obsolete tests that only describe the old shallow internals.
- **Alternative interface design** - when a deepening candidate matters, compare meaningfully different interface designs before choosing: for example a minimal interface, a flexible interface, a caller-optimized interface, or a ports-and-adapters design.

## Public Catalog Scope

The preserved V1 catalog and initial V2 registry include only these public
categories:

- `agent-workflows`
- `engineering`
- `productivity`

Do not add private project names, sensitive personal domains, client context, handles, or private personal workflows to public main unless they are sanitized into genuinely portable public skills.

## Quality Bar

Skills should be:

- installable into different agent frameworks;
- self-contained after installation;
- specific enough to change agent behavior;
- concise enough to avoid context bloat;
- willing to use `references/`, `scripts/`, or `assets/` when they make the skill stronger without overloading `SKILL.md`;
- clear that `description` is for discovery, while trigger patterns and workflow details live in the body;
- explicit about trigger patterns, output contracts, guardrails, dependencies, and delegation;
- willing to use stop rules, proof gates, rationalization counters, red flags, or anti-pattern references when discipline-heavy behavior needs them;
- clear about delegated status values and next controller actions when subagent results can change the workflow;
- portable unless classified otherwise;
- honest about what they cannot verify;
- opinionated about architecture where relevant: prefer deep modules, clear seams, strong locality, and tests through public interfaces over many shallow modules and tests tied to internals.
