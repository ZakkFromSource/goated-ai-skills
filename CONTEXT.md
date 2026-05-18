# GOATED AI Skills Context

GOATED AI Skills is a public source library for reusable, installable AI skill folders. It should feel like a compact operating system for high-quality agent work, not a prompt dump.

## Domain Language

These definitions are normative for this source repo. If another public doc uses these terms differently, treat that as documentation drift to resolve. These definitions clarify the current V1 model; they do not introduce new product scope.

### Project Boundaries

- **GOATED AI Skills** - the public source library of installable, framework-agnostic AI skill folders.
- **Source repo** - this public repository, used to publish, maintain, and document GOATED AI Skills. This repo is not a template that users must clone into every project.
- **Source repo maintenance** - work that changes this repository's docs, issues, skill folders, adapters, or maintainer artifacts.
- **Skill pack distribution** - Layer 0 of the product model: users clone, download, copy, install, or adapt skill folders from this repo into their own agent workflow.
- **Agent framework** - the tool or environment that discovers and runs skills, commands, prompts, or instructions, such as Codex, Claude Code, Hermes, OpenCode, or a generic tool-calling agent.
- **Installed skill** - a copied or installed skill folder inside a user's chosen agent framework. It must remain useful without loading this repo's root `AGENT.md`, `README.md`, or `CONTEXT.md`.
- **Target project** - a project where installed skills are used to do onboarding or delivery work. In public docs this usually means a user's downstream project; when this repo is the work target, source repo maintenance rules still win.

### V1 Workflow Model

- **Docs-first installation** - the V1 installation model: users manually copy, install, or adapt completed skill folders using documentation instead of installer automation.
- **Target Project Onboarding** - preparing a target project for serious agent work by mapping sources, calibrating project context and standards, and routing the chosen agent framework to installed skills and durable project artifacts.
- **Target Project Delivery** - moving one target-project change from clarified intent through planning, implementation, verification, documentation, and handoff.
- **Public core workflow** - the portable V1 workflow set intended for public main, spanning onboarding and delivery without private project assumptions.
- **Tiny one-off task** - a small, obvious, low-risk request that does not need full onboarding or planning ceremony, such as a typo fix, one-line rename, or direct command the user already specified.

### Skill Anatomy

- **Skill** - a reusable workflow packaged as a skill folder with a `SKILL.md` file and any local support files that materially improve its power, reuse, progressive disclosure, or installability.
- **Skill folder** - a directory under `skills/<category>/<skill-name>/` that is copied or adapted as one installable unit.
- **`SKILL.md`** - the primary workflow file for an installed skill. It should act as the router and operating procedure, not the whole knowledge base.
- **Support files** - local files inside a skill folder, such as `references/`, `scripts/`, or `assets/`. They are not discouraged; add them when they make the skill more capable, easier to use, easier to verify, or easier to install without bloating `SKILL.md`.
- **`references/`** - support files inside a skill folder for detailed examples, templates, checklists, stack-specific notes, or longer decision guides. Use them when detail would help the skill but should not sit in the main workflow.
- **`scripts/`** - executable helpers inside a skill folder. Use them when a repeatable operation is safer, clearer, or more powerful as a maintained script than as prose instructions.
- **`assets/`** - reusable assets inside a skill folder. Use them when examples, templates, fixtures, images, or other packaged materials improve the installed skill.
- **Lean schema** - the required `SKILL.md` frontmatter and body convention for implemented skills: `name`, `category`, `classification`, `status`, `description`, `triggers`, `outputs`, `depends_on`, and `adapters`, with concise workflow sections such as Purpose, Inputs, Workflow, Output Contract, Delegation, Guardrails, and References.
- **Trigger** - a user request pattern, task condition, or project situation that tells an agent when to use a skill.
- **Output** - the artifact, decision, summary, change, or verification result a skill is expected to produce.
- **Dependency** - another skill, project artifact, command, source, or workflow step the current skill requires, prefers, or can gracefully work without. Skill frontmatter should distinguish hard dependencies, soft dependencies, and fallback behavior when relevant.
- **Skill adapter** - a small framework-specific note or compatibility marker for using a skill in Codex, Claude Code, Hermes, OpenCode, or a generic agent environment. In `SKILL.md` frontmatter this appears as `adapters`.
- **Category** - the public V1 skill grouping. Allowed V1 categories are `agent-workflows`, `engineering`, and `productivity`.
- **Classification** - the portability label for a skill: `portable` means safe for any compatible agent or project; `domain-specific` means reusable with a named public domain or project assumption; `private` means intended for private forks or private deployments, not public main.
- **Status** - the maturity label for a skill: `stable` means recommended for normal use; `wip` means experimental or still being sharpened; `deprecated` means kept for reference only.

### Artifacts

- **PRD** - a product requirements document that scopes a product or delivery outcome clearly enough to feed issue breakdown.
- **Issue handoff** - a local Markdown issue file under `issues/` that describes a planned implementation slice, acceptance criteria, blockers, and user stories for future agent work.
- **Archived issue** - a completed implementation issue moved under `issues/archive/` with acceptance criteria checked off.
- **ADR** - an architectural decision record stored under `docs/adr/` when a durable architecture decision needs to be recorded.
- **Context matrix** - a durable target-project artifact, normally `docs/agents/context-matrix.md`, that tells future agents what to read first, second, and only if needed.
- **Project context file** - a durable target-project artifact, normally root `CONTEXT.md`, that defines project boundaries, domain language, durable artifact meanings, and shared architecture vocabulary for that target project. This is distinct from this source repo's root `CONTEXT.md`.
- **Project standards profile** - a durable target-project artifact, normally `docs/agents/project-standards.md`, that separates documented standards, inferred conventions, user-confirmed preferences, unresolved questions, and enforcement levels.
- **Agent instruction artifact** - a file or configuration entry that tells a specific agent framework how to use installed skills and target-project artifacts.
- **Durable artifact** - tracked project knowledge that should survive across sessions, such as PRDs, ADRs, project context files, context matrices, standards profiles, and public docs.
- **Local/session artifact** - ignored, private, or temporary workspace context, such as `.local/handoffs/`, `.local/scratch/`, `.scratch/`, `tmp/`, or `temp/`.
- **Handoff** - a compact continuity note for a future agent or session. Handoffs should reference existing artifacts instead of duplicating PRDs, issues, ADRs, diffs, or commits.

### Operating Principles

- **Progressive disclosure** - loading the smallest useful context first, then deeper references only when the task requires them.
- **Support-file bias** - future agents should not default against `references/`, `scripts/`, or `assets/`. Keep `SKILL.md` lean, but create support files whenever they genuinely improve skill capability, reuse, verification, or installability.
- **Self-contained skill** - an installed skill folder that carries the workflow guidance and local references it needs after copying, without requiring this repo's root files at runtime.
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

## Public V1 Scope

V1 includes only active public categories:

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
- explicit about triggers, outputs, guardrails, dependencies, and delegation;
- portable unless classified otherwise;
- honest about what they cannot verify.
- opinionated about architecture where relevant: prefer deep modules, clear seams, strong locality, and tests through public interfaces over many shallow modules and tests tied to internals.
