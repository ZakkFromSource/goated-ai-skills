# Context Matrix

## Purpose

Use this map to choose the smallest useful context before working in the GOATED AI Skills source repo. It routes future agents to first-read maintainer guidance, task-specific issue and skill sources, and deferred sources that should only be opened when the task needs them.

## First-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `AGENT.md` | Defines the maintainer contract for this source repo. | Before planning, editing, reviewing, or running automation in this repo. | Source-repo guidance wins over thin adapters unless a tool safety limit requires otherwise. |
| `CONTEXT.md` | Defines public-safe language, scope, and product concepts. | With `AGENT.md` for non-trivial repo work. | Keeps source repo, installed skills, and target projects separate. |
| `README.md` | Explains the public distribution model, root layout, preserved V1 baseline, and active V2 direction. | At the start of source-repo orientation or docs changes. | Good high-level map before opening narrower files. |
| `docs/specs/2026-07-25-goated-ai-skills-v2.md` | Active V2 product and architecture contract. | Before changing V2 installation, routing, shared policy, registry, state, skills, or migration tickets. | Read only the sections relevant to the current ticket. |
| `tickets/*.md` | Active V2 implementation handoffs. | Before implementing or reviewing the named V2 slice. | Start with the current ticket and follow its explicit source links and blockers. |
| `issues/prd-goated-ai-skills-v1-public-core.md` | Historical V1 product spec and acceptance reference. | When changing preserved V1 behavior or tracing why an existing skill exists. | V2 sources and accepted ADRs supersede conflicting active-development decisions. |
| `docs/agents/context-matrix.md` | This routing artifact. | At the start of future serious sessions after this file exists. | Refresh when repo structure, workflow, or evidence paths change. |
| `docs/agents/project-standards.md` | Durable standards profile for this repo. | At the start of future serious sessions after this file exists. | Use it to distinguish documented standards, inferred conventions, preferences, and unresolved questions. |

## Second-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `docs/install.md` | Defines integrated and individual docs-first install and adaptation guidance. | Before changing install docs or copying/adapting skills into an agent framework. | Integrated registry paths resolve from the shared distribution root; runtime installer automation remains out of scope. |
| `docs/how-to-use.md` | Human operator manual for the installed GOATED skill stack. | Before changing usage-model docs, onboarding or delivery pipeline explanations, prompt starters, or skill-by-skill public reference material. | Complements install guidance; keep it aligned with the staged V2 migration and current implemented inventory. |
| `stack/` | V2 shared policy, registry, schema, logical-state templates, and portable routing fixtures. | Before changing integrated-stack behavior or cross-skill metadata. | `SKILL.md` files remain authoritative for specialist procedures; fixtures describe conformance expectations rather than live-agent proof. |
| `skills/README.md` | Defines skill schema, category rules, progressive disclosure, and delegation conventions. | Before creating or editing a skill folder. | Do not create skill folders from the index alone; use the approved issue. |
| `skills/agent-workflows/README.md` | Defines the agent-workflows category and implemented skills. | Before editing onboarding, session, handoff, instruction-integration, or skill-creator workflows. | Keep workflows portable and compatibility caveats specific; archived issue `029` completed the creator rename. |
| `skills/engineering/README.md` | Defines the engineering category and implemented skills. | Before implementing or reviewing delivery, testing, review, docs, architecture, or refactor skills. | Future additions still require approved implementation issues. |
| `skills/productivity/README.md` | Defines the productivity category and implemented skills. | Before implementing or reviewing productivity workflows. | Private or domain-specific workflows belong outside public main until sanitized. |
| `issues/archive/*.md` | Completed implementation handoffs and blocker history. | Before modifying an implemented skill or tracing why an existing artifact exists. | Read the specific archived issue tied to the artifact or blocker chain. |
| `issues/*.md` excluding `issues/archive/` and PRDs | Historical or deferred issue-format handoffs. | When a named legacy issue or preserved V1 artifact is relevant. | Active V2 implementation uses `tickets/`. |
| `AGENTS.md` and `CLAUDE.md` | Thin framework adapter files. | Before changing agent-specific source-repo instructions. | They should route to `AGENT.md`, not duplicate the full workflow. |
| `docs/adr/README.md` | ADR index and storage policy. | Before adding or changing architectural decision records. | ADR 0002 supersedes ADR 0001's installation-primary and self-containment decisions; ADR 0001's runtime-automation exclusions remain in force. |
| `.gitignore` | Defines ignored local and scratch artifacts. | Before adding local/session artifacts or generated output paths. | `.local/` is intentionally ignored. |

## Only-If-Needed Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `skills/*/*/SKILL.md` | Actual installable workflow bodies. | Before editing, reviewing, installing, or adapting the named skill. | Do not bulk-read all skills when one skill is relevant. |
| `.out-of-scope/` | Public deferred ideas and future upgrades. | When deciding whether a requested idea belongs in the active public scope. | Sample only the relevant file; archived issue `030` owns the concrete triage deferral update. |
| `.local/` | Ignored private notes or scratch work. | Only when the user explicitly points to it or the active workflow requires private/local workspace context. | Public behavior must not depend on `.local/`. |
| OS temp `goated-handoffs/<project-name>/` | Temporary handoff notes written outside the project workspace. | Only when the user points to an existing handoff or the active workflow needs temporary handoff context. | Resolve the absolute OS temp path through the active environment; temp files may be cleaned by the OS. |
| `.git/` | Git metadata. | Use through git commands only. | Do not treat it as normal context. |
| Installed skill copies outside this repo, such as `C:/Users/.../.codex/skills/*` | Runtime copies used by an agent framework. | When the user asks to test installed behavior or compare source and installed copies. | Verify against source if manual copies may have drifted. |

## Code Areas

| Area | Paths | What lives there | Read before |
| --- | --- | --- | --- |
| Maintainer and adapter guidance | `AGENT.md`, `AGENTS.md`, `CLAUDE.md` | Source-repo rules and thin framework adapters. | Any repo planning, edits, review, or automation. |
| Public context and root docs | `CONTEXT.md`, `README.md` | Domain language, source repo boundary, root layout, preserved V1 model, active V2 model, and public/private boundary. | Any public docs, product model, or skill-library work. |
| Install and decision docs | `docs/install.md`, `docs/how-to-use.md`, `docs/adr/` | Integrated and individual installation, installed-stack usage guidance, deferred automation notes, and accepted ADRs. | Install/adaptation changes, usage-model changes, pipeline explanation changes, or accepted architecture decisions. |
| Integrated stack | `stack/AGENTS.md`, `stack/goated-stack.yaml`, `stack/schemas/`, `stack/templates/`, `stack/fixtures/routing/` | Shared V2 behavior, portable catalog metadata, registry schema, logical-state templates, and routing expectations. | Integrated policy, registry, route-signal, shared-state, or routing-fixture changes. |
| Agent context artifacts | `docs/agents/` | Durable routing and standards artifacts for agents working in this repo. | Serious future sessions after these artifacts exist. |
| Product and ticket handoffs | `docs/specs/`, `tickets/`, `issues/`, `issues/archive/` | Active V2 specs/tickets plus historical V1 PRDs and issue handoffs. | Implementing a ticket, tracing blockers, validating acceptance history, or adding future slices. |
| Skill library | `skills/` | Public category indexes and implemented installable skill folders. | Creating, editing, reviewing, or installing skills. |
| Local/private and deferred areas | `.local/`, OS temp `goated-handoffs/<project-name>/`, `.out-of-scope/` | Ignored private notes, temporary handoffs, and public deferred ideas. | Only when explicitly relevant; avoid `.local/` by default. |

## Tests And Commands

| Command or path | Purpose | When to use | Evidence |
| --- | --- | --- | --- |
| `git rev-parse --show-toplevel` | Confirm the repository boundary. | When the current working directory or target project root is ambiguous. | Ran on 2026-05-21 and returned this repo root. |
| `rg --files` | Discover repo files without bulk-reading them. | At the start of mapping, source routing, or targeted scans. | Use targeted path and term scans when skill inventory, issue state, or docs surfaces change. |
| Issue and PRD scans with `rg -n` | Sample issue and PRD headings, blockers, current names, and implementation summaries. | When deciding which issue to open first or checking documentation drift. | Ran on 2026-05-21 for issue discovery and interim doc sync. |
| `git status --short` | Check local worktree state. | Before and after edits. | Ran on 2026-05-21 before interim doc-sync edits; output was empty. |
| `rg --files -g 'package.json' -g 'pyproject.toml' -g 'pubspec.yaml' -g 'Cargo.toml' -g 'Makefile' -g '*.sln' -g '*.csproj' -g '*.fsproj' -g 'go.mod' -g 'requirements.txt'` | Look for build or package entrypoints. | Before claiming build, lint, format, or test commands exist. | Root `pyproject.toml` now exists for local validator tooling; no CI, formatter, linter, or test config is present. |
| `tests/test_validate_skills.py` | Registry and adaptive-routing fixture validation behavior tests. | Before changing the registry, routing fixture contract, or validator behavior. | Added by Ticket 001 and extended by Ticket 002. |
| `uv run python -m unittest discover -s tests -v` | Run validator behavior tests. | Before claiming registry or routing-fixture validation behavior passes. | Uses the standard library `unittest` runner. |
| `uv run python scripts/validate_skills.py` | Validate implemented skills, the integrated registry schema and cross-references, public-boundary checks, and report-only drift. | Before claiming skill or registry changes are valid. | Uses `pyyaml` and `jsonschema` through `uv`. |
| Manual markdown review | Validate docs-only changes. | For docs changes outside validator-covered skill checks. | Pair with targeted script checks when a skill adds executable helpers. |

## Decisions And Context Packs

| Source | Scope | Status | Notes |
| --- | --- | --- | --- |
| `issues/prd-goated-ai-skills-v1-public-core.md` | Public core product model, skill schema, V1 skill set, onboarding and delivery workflows. | Historical V1 reference. | Superseded for active development by the V2 spec and accepted ADRs. |
| `docs/specs/2026-07-25-goated-ai-skills-v2.md` | V2 integrated-stack product, routing, state, skill, and migration contract. | Ready for implementation. | Primary active-development spec. |
| `tickets/archive/001-establish-v2-integrated-stack-foundation.md` | Shared-policy, registry, schema, validation, baseline, and install foundation. | Completed and archived. | Foundation consumed by the remaining V2 tickets. |
| `issues/archive/*.md` | Completed scaffold, skill implementation, follow-up upgrade, doc-sync, and final acceptance handoffs. | Archived. | As of 2026-06-11, issues `001` through `060` are archived. Use the specific archived issue to understand why an existing artifact was created or upgraded. |
| `tickets/*.md` | Dependency-ordered V2 implementation slices. | Active. | Read the specific ticket and order file before implementing or reviewing a slice. |
| `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` | Accepted V1 runtime bootstrap and adapter automation decision. | Accepted ADR. | V1 allows narrow compatibility notes for real caveats only; runtime bootstrap, plugin manifests, hooks, installers, automatic loading, and adapter automation require future scoped work. |
| `docs/adr/0002-v2-integrated-stack-foundation.md` | V2 integrated and individual install modes plus narrowed standalone fallback. | Accepted ADR. | Supersedes the conflicting installation/self-containment portions of ADR 0001. |
| `docs/adr/README.md` | ADR index, placement, and policy. | ADR index. | Lists accepted ADRs and should be read before adding or changing architectural decision records. |
| `docs/agents/context-matrix.md` | Future-agent read order for this repo. | Maintained routing artifact. | Refresh when repo structure, issue state, skill inventory, or source-evidence paths change. |
| `docs/agents/project-standards.md` | Future-agent standards profile for this repo. | Maintained standards artifact. | Refresh when documented standards, inferred conventions, commands, or issue state change. |

## Gaps And Assumptions

- This matrix maps the GOATED AI Skills source repo as the current target project; it does not describe a downstream project where skills have been installed.
- Root `pyproject.toml`, `uv.lock`, and `tests/` support local validator tooling. No CI workflow, formatter, linter, or build script is present.
- `.local/` was intentionally not read because it is ignored private/local workspace context.
- `.out-of-scope/` was sampled only for the future automation and validation deferral file; read it narrowly for scope or deferred-feature questions.
- Archived issue `021` and issue `032` closeout evidence were sampled for doc-sync drift, but future work should still open the specific active issue and blocker chain for the requested change.
- Installed Codex skill copies can drift from source after manual copying; compare file hashes when testing installation behavior.

## Last Updated

- Date: 2026-07-25
- Updated by: Codex
- Evidence used: prior context-matrix evidence; V2 spec and Ticket 001; ADR
  0002; `stack/`; current validator tests and commands; targeted catalog,
  install, docs-drift, and issue-state scans.
