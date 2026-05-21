# Context Matrix

## Purpose

Use this map to choose the smallest useful context before working in the GOATED AI Skills source repo. It routes future agents to first-read maintainer guidance, task-specific issue and skill sources, and deferred sources that should only be opened when the task needs them.

## First-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `AGENT.md` | Defines the maintainer contract for this source repo. | Before planning, editing, reviewing, or running automation in this repo. | Source-repo guidance wins over thin adapters unless a tool safety limit requires otherwise. |
| `CONTEXT.md` | Defines public-safe language, scope, and product concepts. | With `AGENT.md` for non-trivial repo work. | Keeps source repo, installed skills, and target projects separate. |
| `README.md` | Explains the public distribution model, root layout, V1 state, and current/planned workflows. | At the start of source-repo orientation or docs changes. | Good high-level map before opening narrower files. |
| `issues/prd-goated-ai-skills-v1-public-core.md` | Canonical V1 product spec and acceptance reference. | Before changing product model, skill schema, category structure, install guidance, or implementation issues. | Read relevant sections first; it is intentionally broad. |
| `docs/agents/context-matrix.md` | This routing artifact. | At the start of future serious sessions after this file exists. | Refresh when repo structure, workflow, or evidence paths change. |
| `docs/agents/project-standards.md` | Durable standards profile for this repo. | At the start of future serious sessions after this file exists. | Use it to distinguish documented standards, inferred conventions, preferences, and unresolved questions. |

## Second-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `docs/install.md` | Defines docs-first install and adaptation guidance. | Before changing install docs or copying/adapting skills into an agent framework. | V1 installer scripts are out of scope. |
| `skills/README.md` | Defines skill schema, category rules, progressive disclosure, and delegation conventions. | Before creating or editing a skill folder. | Do not create skill folders from the index alone; use the approved issue. |
| `skills/agent-workflows/README.md` | Defines the agent-workflows category and implemented WIP skills. | Before editing onboarding, session, handoff, instruction-integration, or skill-porting workflows. | Keep workflows portable and adapter notes small; issue `029` owns the future creator rename. |
| `skills/engineering/README.md` | Defines the engineering category and implemented WIP skills. | Before implementing or reviewing delivery, testing, review, docs, architecture, or refactor skills. | Future additions still require approved implementation issues. |
| `skills/productivity/README.md` | Defines the productivity category and implemented WIP skills. | Before implementing or reviewing productivity workflows. | Private or domain-specific workflows belong outside public main until sanitized. |
| `issues/archive/*.md` | Completed implementation handoffs and blocker history. | Before modifying an implemented skill or tracing why an existing artifact exists. | Read the specific archived issue tied to the artifact or blocker chain. |
| `issues/*.md` excluding `issues/archive/` and PRDs | Active future implementation handoffs. | Before implementing the specific planned skill or acceptance pass. | Read only the issue for the current task unless blockers require more. |
| `AGENTS.md` and `CLAUDE.md` | Thin framework adapter files. | Before changing agent-specific source-repo instructions. | They should route to `AGENT.md`, not duplicate the full workflow. |
| `docs/adr/README.md` | ADR storage policy. | Before adding or changing architectural decision records. | ADR 0001 records the accepted V1 runtime bootstrap and adapter automation decision. |
| `.gitignore` | Defines ignored local and scratch artifacts. | Before adding local/session artifacts or generated output paths. | `.local/` is intentionally ignored. |

## Only-If-Needed Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `skills/*/*/SKILL.md` | Actual installable workflow bodies. | Before editing, reviewing, installing, or adapting the named skill. | Do not bulk-read all skills when one skill is relevant. |
| `.out-of-scope/` | Public deferred ideas and future upgrades. | When deciding whether a requested idea belongs in V1 public core. | Sample only the relevant file; issue `030` owns the concrete triage deferral update. |
| `.local/` | Ignored private notes or scratch work. | Only when the user explicitly points to it or the active workflow requires private/local workspace context. | Public behavior must not depend on `.local/`. |
| OS temp `goated-handoffs/<project-name>/` | Temporary handoff notes written outside the project workspace. | Only when the user points to an existing handoff or the active workflow needs temporary handoff context. | Resolve the absolute OS temp path through the active environment; temp files may be cleaned by the OS. |
| `.git/` | Git metadata. | Use through git commands only. | Do not treat it as normal context. |
| Installed skill copies outside this repo, such as `C:/Users/.../.codex/skills/*` | Runtime copies used by an agent framework. | When the user asks to test installed behavior or compare source and installed copies. | Verify against source if manual copies may have drifted. |

## Code Areas

| Area | Paths | What lives there | Read before |
| --- | --- | --- | --- |
| Maintainer and adapter guidance | `AGENT.md`, `AGENTS.md`, `CLAUDE.md` | Source-repo rules and thin framework adapters. | Any repo planning, edits, review, or automation. |
| Public context and root docs | `CONTEXT.md`, `README.md` | Domain language, source repo boundary, root layout, V1 model, and public/private boundary. | Any public docs, product model, or skill-library work. |
| Install and decision docs | `docs/install.md`, `docs/adr/` | Docs-first installation model, deferred automation notes, and accepted ADRs. | Install/adaptation changes or accepted architecture decisions. |
| Agent context artifacts | `docs/agents/` | Durable routing and standards artifacts for agents working in this repo. | Serious future sessions after these artifacts exist. |
| Product and issue handoffs | `issues/`, `issues/archive/` | V1 PRD, active planned issues, and completed implementation issues. | Implementing a specific skill, tracing blockers, or validating V1 acceptance. |
| Skill library | `skills/` | Public category indexes and implemented installable skill folders. | Creating, editing, reviewing, or installing skills. |
| Local/private and deferred areas | `.local/`, OS temp `goated-handoffs/<project-name>/`, `.out-of-scope/` | Ignored private notes, temporary handoffs, and public deferred ideas. | Only when explicitly relevant; avoid `.local/` by default. |

## Tests And Commands

| Command or path | Purpose | When to use | Evidence |
| --- | --- | --- | --- |
| `git rev-parse --show-toplevel` | Confirm the repository boundary. | When the current working directory or target project root is ambiguous. | Ran on 2026-05-21 and returned this repo root. |
| `rg --files` | Discover repo files without bulk-reading them. | At the start of mapping, source routing, or targeted scans. | Ran on 2026-05-21; showed root docs, active/archived issues, docs, and 21 implemented skill folders. |
| Issue and PRD scans with `rg -n` | Sample issue and PRD headings, blockers, current names, and implementation summaries. | When deciding which issue to open first or checking documentation drift. | Ran on 2026-05-21 for issue discovery and interim doc sync. |
| `git status --short` | Check local worktree state. | Before and after edits. | Ran on 2026-05-21 before interim doc-sync edits; output was empty. |
| `rg --files -g 'package.json' -g 'pyproject.toml' -g 'pubspec.yaml' -g 'Cargo.toml' -g 'Makefile' -g '*.sln' -g '*.csproj' -g '*.fsproj' -g 'go.mod' -g 'requirements.txt'` | Look for build or package entrypoints. | Before claiming build, lint, format, or test commands exist. | Ran on 2026-05-21; no matches found. |
| `rg --files -g '*test*' -g '*spec*'` | Look for test/spec files or folders. | Before claiming test layout exists. | Ran on 2026-05-21; only markdown reference/issue files matched, not executable tests. |
| Manual markdown review | Validate docs-only changes. | For docs changes while no project test/build tooling is present. | Current repo appears markdown-only from this pass. |

## Decisions And Context Packs

| Source | Scope | Status | Notes |
| --- | --- | --- | --- |
| `issues/prd-goated-ai-skills-v1-public-core.md` | Public core product model, skill schema, V1 skill set, onboarding and delivery workflows. | Draft reference PRD. | Primary spec until superseded by accepted ADRs or updated PRDs. |
| `issues/archive/*.md` | Completed scaffold, skill implementation, and follow-up upgrade handoffs. | Archived. | As of 2026-05-21, issues `001` through `020`, `022` through `026`, `029`, and `033` through `036` are archived. Use the specific archived issue to understand why an existing artifact was created or upgraded. |
| `issues/*.md` excluding `issues/archive/` and PRDs | Planned future V1 implementation slices and final acceptance pass. | Active issue handoffs. | As of 2026-05-21, active handoffs are `021`, `027`, `028`, `030` through `032`, and `037` through `043`; read the current issue before implementing or reviewing that slice. |
| `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` | Accepted V1 runtime bootstrap and adapter automation decision. | Accepted ADR. | V1 allows narrow adapter notes only; runtime bootstrap, plugin manifests, hooks, installers, automatic loading, and adapter automation require future scoped work. |
| `docs/adr/README.md` | ADR placement and policy. | ADR index. | Read before adding or changing architectural decision records. |
| `docs/agents/context-matrix.md` | Future-agent read order for this repo. | Maintained routing artifact. | Refresh when repo structure, issue state, skill inventory, or source-evidence paths change. |
| `docs/agents/project-standards.md` | Future-agent standards profile for this repo. | Maintained standards artifact. | Refresh when documented standards, inferred conventions, commands, or issue state change. |

## Gaps And Assumptions

- This matrix maps the GOATED AI Skills source repo as the current target project; it does not describe a downstream project where skills have been installed.
- No package manifest, build script, lint command, formatter command, or test runner was found in the discovery pass.
- `.local/` was intentionally not read because it is ignored private/local workspace context.
- `.out-of-scope/` was sampled only for the future automation and validation deferral file; read it narrowly for scope or deferred-feature questions.
- Active issue bodies were sampled for interim doc-sync drift, but future work should still open the specific issue and blocker chain for the requested change.
- Installed Codex skill copies can drift from source after manual copying; compare file hashes when testing installation behavior.

## Last Updated

- Date: 2026-05-21
- Updated by: Codex
- Evidence used: installed `session-start-progressive-disclosure`, `context-matrix-map`, `project-standards-calibration`, and `doc-sync`; `AGENT.md`; `CONTEXT.md`; `README.md`; `docs/install.md`; `docs/agents/project-standards.md`; category READMEs under `skills/`; implemented skill inventory under `skills/`; `docs/adr/README.md`; `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`; `.gitignore`; `.out-of-scope/future-automation-and-validation.md`; V1 PRDs; active issues `021`, `027`, `028`, `030` through `032`, and `037` through `043`; archived issues `001` through `020`, `022` through `026`, `029`, and `033` through `036`; `rg --files`; targeted issue and stale-wording scans with `rg -n`; `git rev-parse --show-toplevel`; `git status --short`; manifest and test discovery `rg` commands.
