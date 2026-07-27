# Context Matrix

## Purpose

Use this map to choose the smallest useful context before working in the GOATED AI Skills source repo. It routes future agents to first-read maintainer guidance, task-specific issue and skill sources, and deferred sources that should only be opened when the task needs them.

## First-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `AGENT.md` | Defines the maintainer contract for this source repo. | Before planning, editing, reviewing, or running automation in this repo. | Source-repo guidance wins over thin adapters unless a tool safety limit requires otherwise. |
| `CONTEXT.md` | Defines public-safe language, scope, and product concepts. | With `AGENT.md` for non-trivial repo work. | Keeps source repo, installed skills, and target projects separate. |
| `README.md` | Explains the public distribution model, root layout, preserved V1 baseline, and accepted V2 release. | At the start of source-repo orientation or docs changes. | Good high-level map before opening narrower files. |
| `docs/specs/2026-07-25-goated-ai-skills-v2.md` | V2 product and architecture contract. | Before changing V2 installation, routing, shared policy, registry, state, skills, or migration tickets. | Read only the sections relevant to the current ticket. |
| `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` | Approved selective-adoption contract for skill authoring, diagnosis, ticket slicing, merge conflicts, external research, invocation topology, and active domain modeling. | Before implementing or reviewing Tickets 015-024. | Phase A is accepted; Phase B concluded no-go; only domain-model implementation remains conditional on its named maintainer gate. Any invocation harness is a separate product track. |
| `tickets/*.md` | Active future delivery tickets and the preserved V2 ticket-order index. | Before implementing or reviewing a named slice. | Completed V2 tickets are archived under `tickets/archive/`. |
| `issues/prd-goated-ai-skills-v1-public-core.md` | Historical V1 product spec and acceptance reference. | When changing preserved V1 behavior or tracing why an existing skill exists. | V2 sources and accepted ADRs supersede conflicting active-development decisions. |
| `docs/agents/context-matrix.md` | This routing artifact. | At the start of future serious sessions after this file exists. | Refresh when repo structure, workflow, or evidence paths change. |
| `docs/agents/project-standards.md` | Durable standards profile for this repo. | At the start of future serious sessions after this file exists. | Use it to distinguish documented standards, inferred conventions, preferences, and unresolved questions. |

## Second-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |
| `docs/install.md` | Defines integrated and individual docs-first install and adaptation guidance. | Before changing install docs or copying/adapting skills into an agent framework. | Integrated registry paths resolve from the shared distribution root; runtime installer automation remains out of scope. |
| `docs/how-to-use.md` | Human operator manual for the installed GOATED skill stack. | Before changing usage-model docs, onboarding or delivery pipeline explanations, prompt starters, or skill-by-skill public reference material. | Complements install and migration guidance; keep it aligned with accepted V2. |
| `stack/` | V2 shared policy, registry, schema, logical-state templates, focused fixtures, and four release-level end-to-end fixtures. | Before changing integrated-stack behavior or cross-skill metadata. | `SKILL.md` files remain authoritative for specialist procedures; fixtures describe conformance expectations rather than live-agent proof. |
| `skills/README.md` | Defines skill schema, category rules, progressive disclosure, and delegation conventions. | Before creating or editing a skill folder. | Do not create skill folders from the index alone; use the approved issue. |
| `skills/agent-workflows/README.md` | Defines the agent-workflows category and implemented skills. | Before editing onboarding, session, Wayfinder, handoff, instruction-integration, or skill-creator workflows. | Keep workflows portable and compatibility caveats specific; archived issue `029` completed the creator rename. |
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
| `.local/goated/` | Ignored resumable envelopes and handoffs. | Only when the user points to existing state or resumable work requires it after ignore verification. | Public behavior must not depend on local state; OS temp remains the fallback. |
| OS temp `goated-handoffs/<project-name>/` | Fallback handoff notes outside the project workspace. | When project-local state is inappropriate or cannot be stored safely. | Resolve the absolute OS temp path through the active environment; temp files may be cleaned by the OS. |
| `.git/` | Git metadata. | Use through git commands only. | Do not treat it as normal context. |
| Installed skill copies outside this repo, such as `C:/Users/.../.codex/skills/*` | Runtime copies used by an agent framework. | When the user asks to test installed behavior or compare source and installed copies. | Verify against source if manual copies may have drifted. |

## Code Areas

| Area | Paths | What lives there | Read before |
| --- | --- | --- | --- |
| Maintainer and adapter guidance | `AGENT.md`, `AGENTS.md`, `CLAUDE.md` | Source-repo rules and thin framework adapters. | Any repo planning, edits, review, or automation. |
| Public context and root docs | `CONTEXT.md`, `README.md` | Domain language, source repo boundary, root layout, preserved V1 model, accepted V2 model, and public/private boundary. | Any public docs, product model, or skill-library work. |
| Install and decision docs | `docs/install.md`, `docs/how-to-use.md`, `docs/adr/` | Integrated and individual installation, installed-stack usage guidance, deferred automation notes, and accepted ADRs. | Install/adaptation changes, usage-model changes, pipeline explanation changes, or accepted architecture decisions. |
| Integrated stack | `stack/AGENTS.md`, `stack/goated-stack.yaml`, `stack/schemas/`, `stack/templates/`, `stack/fixtures/` | Shared V2 behavior, portable catalog metadata, registry schema, logical-state templates, focused contracts, and release-level end-to-end expectations. | Integrated policy, registry, route-signal, shared-state, or fixture-contract changes. |
| Agent context artifacts | `docs/agents/` | Durable routing and standards artifacts for agents working in this repo. | Serious future sessions after these artifacts exist. |
| Product and ticket handoffs | `docs/specs/`, `tickets/`, `tickets/archive/`, `issues/`, `issues/archive/` | Accepted V2 spec and archived tickets plus historical V1 PRDs and issue handoffs. | Implementing a ticket, tracing acceptance history, or adding future slices. |
| Skill library | `skills/` | Public category indexes and implemented installable skill folders. | Creating, editing, reviewing, or installing skills. |
| Local/private and deferred areas | `.local/goated/`, `.local/`, OS temp `goated-handoffs/<project-name>/`, `.out-of-scope/` | Ignored resumable state, private notes, fallback temporary handoffs, and public deferred ideas. | Read local state only when explicitly relevant and verify ignore behavior before writing it. |

## Tests And Commands

| Command or path | Purpose | When to use | Evidence |
| --- | --- | --- | --- |
| `git rev-parse --show-toplevel` | Confirm the repository boundary. | When the current working directory or target project root is ambiguous. | Ran on 2026-05-21 and returned this repo root. |
| `rg --files` | Discover repo files without bulk-reading them. | At the start of mapping, source routing, or targeted scans. | Use targeted path and term scans when skill inventory, issue state, or docs surfaces change. |
| Issue and PRD scans with `rg -n` | Sample issue and PRD headings, blockers, current names, and implementation summaries. | When deciding which issue to open first or checking documentation drift. | Ran on 2026-05-21 for issue discovery and interim doc sync. |
| `git status --short` | Check local worktree state. | Before and after edits. | Ran on 2026-05-21 before interim doc-sync edits; output was empty. |
| `rg --files -g 'package.json' -g 'pyproject.toml' -g 'pubspec.yaml' -g 'Cargo.toml' -g 'Makefile' -g '*.sln' -g '*.csproj' -g '*.fsproj' -g 'go.mod' -g 'requirements.txt' -g '.github/workflows/*'` | Look for build, package, and CI entrypoints. | Before claiming build, lint, format, test, or CI commands exist. | Root `pyproject.toml`, `.github/workflows/validate.yml`, and `tests/` support validation; no formatter, linter, or build config is present. |
| `tests/test_validate_skills.py` | Registry, canonical-reference, adaptive-routing, onboarding, clarification, specification/ticket, architecture, implementation-planning, behavior-proof, merge-conflict, review/verification, Wayfinding, knowledge-retrieval, source-grounded-research, and Setup Scribe fixture validation behavior tests. | Before changing the registry, canonical names, fixture contracts, or validator behavior. | Added by Ticket 001 and extended by Tickets 002-012, 014, 018, and 019. |
| `scripts/validation/` | Focused validator implementation modules for shared primitives, skill packages, registry, routing, onboarding, planning, behavior proof, merge conflicts, research, operations, and reporting. | Before changing validator rules, concern ownership, dependency direction, result aggregation, or CLI presentation. | `scripts/validate_skills.py` remains the thin command, orchestration, and compatibility surface. |
| `tests/test_validator_compatibility.py` | Public import, direct concern-module, cross-concern orchestration, exact success/failure output, fixture-count, and exit-code compatibility proof. | Before moving validator behavior between modules or changing CLI/reporting behavior. | Keeps direct-script and imported-module execution equivalent during Ticket 013 and later maintenance. |
| `tests/test_validator_module_isolation.py` | Fresh-interpreter import isolation proof for every validator concern module. | Before adding or changing dependencies between validator concerns. | Fails when a concern import loads a module outside its documented dependency set. |
| `uv run python -m unittest discover -s tests -v` | Run validator behavior tests. | Before claiming registry or routing-fixture validation behavior passes. | Uses the standard library `unittest` runner. |
| `uv run python scripts/validate_skills.py` | Validate implemented skills, canonical architecture references, the integrated registry, routing, onboarding, clarification, specification/ticket, architecture, implementation-planning, behavior-proof, merge-conflict, review/verification, Wayfinding, knowledge-retrieval, source-grounded-research, and Setup Scribe fixtures, public-boundary checks, and report-only drift. | Before claiming skill, registry, canonical-name, or fixture changes are valid. | Uses `pyyaml` and `jsonschema` through `uv`. |
| Manual markdown review | Validate docs-only changes. | For docs changes outside validator-covered skill checks. | Pair with targeted script checks when a skill adds executable helpers. |

## Decisions And Context Packs

| Source | Scope | Status | Notes |
| --- | --- | --- | --- |
| `issues/prd-goated-ai-skills-v1-public-core.md` | Public core product model, skill schema, V1 skill set, onboarding and delivery workflows. | Historical V1 reference. | Superseded for active development by the V2 spec and accepted ADRs. |
| `docs/specs/2026-07-25-goated-ai-skills-v2.md` | V2 integrated-stack product, routing, state, skill, and migration contract. | Implemented and accepted. | Primary V2 contract. |
| `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` | Selective upstream-inspired refinements, new specialists, and evidence-gated invocation/domain decisions. | Approved; Phase A accepted, Phase B no-go, and Phase C ticket ready. | Parent contract for Tickets 015-024; explicitly excludes wholesale stack merging, work-management, guided learning, and installer tooling. |
| `tickets/archive/013-*.md`, `tickets/archive/015-*.md` through `tickets/archive/022-*.md`, active `tickets/023-*.md` and `tickets/024-*.md`, and `tickets/selective-upstream-skill-adoption-order.md` | Accepted validator refactor and high-confidence adoption, the completed invocation investigation and no-go disposition, plus active-domain-modeling evaluation slices. | Ticket 013 and Phase A are accepted; Ticket 021 concluded with no-go, Ticket 022 closed without implementation, and Tickets 023-024 remain planned. | Ticket 024 requires an explicit maintainer go decision. A future custom invocation harness requires a separate approved scope. |
| `docs/high-confidence-adoption-acceptance-report.md` | Cross-slice conformance, proof, documentation, context-cost, public-boundary, residual-risk, and maintainer-decision record for Tickets 015 through 020. | Accepted with residual risk. | Records the exact accepted risks and the decision to refresh Ticket 013 before its implementation slice. |
| `tickets/archive/001-establish-v2-integrated-stack-foundation.md` | Shared-policy, registry, schema, validation, baseline, and install foundation. | Completed and archived. | Foundation consumed by the remaining V2 tickets. |
| `issues/archive/*.md` | Completed scaffold, skill implementation, follow-up upgrade, doc-sync, and final acceptance handoffs. | Archived. | As of 2026-06-11, issues `001` through `060` are archived. Use the specific archived issue to understand why an existing artifact was created or upgraded. |
| `tickets/archive/001-*.md` through `tickets/archive/012-*.md` | Completed dependency-ordered V2 implementation and acceptance slices. | Completed and archived. | Read the specific ticket when tracing why a V2 artifact or behavior exists. |
| `docs/migration-v1-to-v2.md` | Concise install, rename, artifact-path, and adaptive-gate migration guide. | Accepted V2 guide. | Read when upgrading a V1 installation. |
| `docs/v2-acceptance-report.md` | Validator, fixture, comparison, documentation-review, residual-risk, and maintainer-acceptance evidence. | Accepted release evidence. | Read before changing V2 release status or planning Factory follow-up. |
| `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` | Accepted V1 runtime bootstrap and adapter automation decision. | Accepted ADR. | V1 allows narrow compatibility notes for real caveats only; runtime bootstrap, plugin manifests, hooks, installers, automatic loading, and adapter automation require future scoped work. |
| `docs/adr/0002-v2-integrated-stack-foundation.md` | V2 integrated and individual install modes plus narrowed standalone fallback. | Accepted ADR. | Supersedes the conflicting installation/self-containment portions of ADR 0001. |
| `docs/adr/README.md` | ADR index, placement, and policy. | ADR index. | Lists accepted ADRs and should be read before adding or changing architectural decision records. |
| `docs/agents/context-matrix.md` | Future-agent read order for this repo. | Maintained routing artifact. | Refresh when repo structure, issue state, skill inventory, or source-evidence paths change. |
| `docs/agents/project-standards.md` | Future-agent standards profile for this repo. | Maintained standards artifact. | Refresh when documented standards, inferred conventions, commands, or issue state change. |

## Gaps And Assumptions

- This matrix maps the GOATED AI Skills source repo as the current target project; it does not describe a downstream project where skills have been installed.
- Root `pyproject.toml`, `uv.lock`, `.github/workflows/validate.yml`, and
  `tests/` support local and CI validator tooling. No formatter, linter, or
  build script is present.
- `.local/` was intentionally not read because it is ignored private/local workspace context.
- `.out-of-scope/` was sampled only for the future automation and validation deferral file; read it narrowly for scope or deferred-feature questions.
- Archived issue `021` and issue `032` closeout evidence were sampled for doc-sync drift, but future work should still open the specific active issue and blocker chain for the requested change.
- Installed Codex skill copies can drift from source after manual copying; compare file hashes when testing installation behavior.

## Last Updated

- Date: 2026-07-27
- Updated by: Codex
- Evidence used: prior context-matrix evidence; V2 spec and Tickets 001-012 and
  014; selective-adoption spec, Tickets 015-024, the invocation no-go decision
  and report, and their order file;
  ADR 0002; `stack/`, including routing, onboarding, clarification,
  specification/ticket, architecture, implementation-planning, behavior-proof,
  review/verification, merge-conflict, Wayfinding, knowledge-retrieval,
  source-grounded-research, Setup Scribe, and end-to-end
  fixtures; V1/V2 context comparison tooling; migration and acceptance docs;
  current validator tests and commands; targeted catalog, install, docs-drift,
  and ticket-state scans.
