# Project Standards

## Purpose

Use this profile with `docs/agents/context-matrix.md` to apply GOATED AI Skills repo standards without rediscovering them. Treat documented standards as stronger than inferred conventions, and avoid promoting preferences into rules without source evidence.

## Documented Standards

| Standard | Enforcement | Source | Notes |
| --- | --- | --- | --- |
| Read `AGENT.md` before planning, editing, reviewing, or automation in this repo. | review-enforced | `AGENT.md`, `AGENTS.md`, `CLAUDE.md` | Thin adapters route contributors to the maintainer contract. |
| Read `CONTEXT.md` and the relevant PRD or issue before changing files in this repo. | review-enforced | `AGENT.md`, `docs/agents/context-matrix.md` | For non-trivial docs, product model, skill, or issue changes, load the narrow task-specific source after root context. |
| Preserve the distinction between source repo, installed skills, and target projects. | review-enforced | `AGENT.md`, `CONTEXT.md`, `README.md` | Do not make installed skills depend on root repo guidance. |
| Keep public main public-safe. | review-enforced | `AGENT.md`, `CONTEXT.md`, `README.md`, `issues/prd-goated-ai-skills-v1-public-core.md` | No private names, handles, credentials, client data, sensitive personal domains, or private workflow assumptions. |
| Use verified-ignored `.local/goated/` for resumable envelopes and handoffs; use OS temp `goated-handoffs/<project-name>/` when project-local state is inappropriate or unsafe. Do not make public behavior depend on either. | review-enforced | `.gitignore`, `CONTEXT.md`, `docs/install.md`, `stack/AGENTS.md`, `skills/agent-workflows/handoff/SKILL.md` | Verify ignore behavior before project-local writes. OS temp may be cleaned by the operating system. |
| Add new skill folders and `SKILL.md` files only for a specific approved implementation issue. | review-enforced | `AGENT.md`, `README.md`, `skills/README.md` | Category indexes alone are not approval to create a skill. |
| Recommend the docs-first V2 integrated stack while preserving individual installation; runtime automation remains out of scope. | review-enforced | `docs/install.md`, `stack/AGENTS.md`, `docs/adr/0002-v2-integrated-stack-foundation.md` | Integrated installs preserve a common distribution root for `stack/` and `skills/`. ADR 0001 remains historical and still excludes runtime bootstrap, hooks, installers, and automatic activation. |
| Keep individually installed skills usable through compact standalone fallbacks. | review-enforced | `AGENT.md`, `CONTEXT.md`, `README.md`, `skills/README.md`, `docs/install.md` | A copied skill can reference its own folder, not the shared registry or this repo's root files. |
| Use the lean skill schema for implemented `SKILL.md` files. | tooling-enforced | `skills/README.md`, `scripts/validate_skills.py`, `issues/prd-goated-ai-skills-v1-public-core.md`, implemented skill inventory | Required frontmatter includes top-level `name`, top-level `description`, and `metadata.goated-category`. The local validator checks mechanical schema, required sections, forbidden files, relative links, and narrow public-boundary leaks; description quality remains review-enforced. |
| Use only current public catalog categories unless a future public-safe category is intentionally added. | review-enforced | `CONTEXT.md`, `skills/README.md`, `README.md` | Current public categories are `agent-workflows`, `engineering`, and `productivity`. |
| Keep `SKILL.md` lean and move detailed examples, prompt templates, anti-pattern catalogs, rationalization tables, stack-specific notes, scripts, and reusable assets into directly linked support files. | review-enforced | `AGENT.md`, `CONTEXT.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-public-core.md` | The 300-line threshold is a soft review threshold, not an automated check. `references/`, `scripts/`, and `assets/` are first-class support files when they improve skill capability or keep the main workflow lean. |
| Make dependency behavior explicit. | review-enforced | `AGENT.md`, `skills/README.md` | Name hard dependencies, soft dependencies, and graceful fallbacks when relevant. |
| Keep root adapter files thin and routed to `AGENT.md`. | review-enforced | `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, `docs/install.md` | Do not paste full workflows into adapter files. |
| Use explicit discipline gates where workflow pressure makes shortcuts likely. | review-enforced | `CONTEXT.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-superpowers-absorption.md` | Discipline-heavy skills may use stop rules, proof gates, rationalization counters, red flags, or anti-pattern references. |
| Make workflows subagent-aware and single-agent-compatible. | review-enforced | `AGENT.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-public-core.md` | Subagents must return evidence; the main agent owns final judgment. Delegated workflows should use status enums such as `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED` when subagent results can change the controller's next action; simple evidence scans can use lighter evidence, assumption, uncertainty, and inspected-path requirements. |
| Use progressive disclosure instead of broad context loading. | review-enforced | `AGENT.md`, `skills/README.md`, `docs/agents/context-matrix.md` | Load root guidance, then relevant issue/category/skill sources only as needed. |
| Treat onboarding intensity as an artifact budget: create or refresh only artifacts with demonstrated retrieval, terminology, standards, architecture, routing, or continuity value. | review-enforced | `docs/specs/2026-07-25-goated-ai-skills-v2.md`, `stack/AGENTS.md`, onboarding skills and fixtures | Lightweight projects may stop after thin policy/routing. Existing artifacts are refreshed incrementally from one shared evidence bundle. |
| Store durable target-project facts in selected tracked artifacts; keep resumable state under verified-ignored `.local/goated/` with OS temp fallback. | review-enforced | `.gitignore`, `CONTEXT.md`, `docs/install.md`, `skills/agent-workflows/handoff/SKILL.md` | Context, source-map, and standards artifacts are optional and selected by demonstrated need. |

## Inferred Conventions

| Convention | Enforcement | Evidence | Confidence |
| --- | --- | --- | --- |
| Markdown is the primary artifact format. | review-enforced | Root docs, issue files, category READMEs, implemented skills, and `docs/agents/context-matrix.md` | High |
| Use ATX headings, concise paragraphs, bullet lists, and fenced code blocks for examples or directory layouts. | review-enforced | `README.md`, `docs/install.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-public-core.md` | High |
| Use kebab-case names for skill folders and implemented skill names. | review-enforced | Implemented skill folders under `skills/agent-workflows/`, `skills/engineering/`, and `skills/productivity/` | High |
| Implemented skills live at `skills/<category>/<skill-name>/SKILL.md`. | review-enforced | `skills/README.md`, implemented skill inventory across all three categories | High |
| Existing implemented skills use body `## Dependencies` sections with hard, soft, and fallback entries where relevant. | review-enforced | Implemented `SKILL.md` bodies across all three categories | High |
| Generic adapter maps are intentionally absent from implemented skill frontmatter. | review-enforced | Implemented `SKILL.md` frontmatter across all three categories; issue `059` schema decision | High |
| Skill bodies commonly include Purpose, Inputs, Workflow, Output Contract, Delegation, Guardrails, and References. | review-enforced | Implemented `SKILL.md` headings across all three categories | High |
| V2 ticket handoffs use numbered filenames and stable scope, acceptance, proof, blocker, route, and exclusion sections. | review-enforced | `tickets/*.md`, `tickets/goated-ai-skills-v2-order.md` | High |
| Completed implementation issues move under `issues/archive/` only after acceptance criteria are checked and any required user, maintainer, PR, or project-defined review is complete. | review-enforced | `CONTEXT.md`; archived issues `001` through `060`; no active numbered implementation handoffs currently | High |
| Docs-only changes still rely on manual markdown review outside validator-covered skill, registry, and fixture-contract checks. | review-enforced | Root `pyproject.toml`, `uv.lock`, `scripts/validate_skills.py`, and `tests/test_validate_skills.py`; no CI, formatter, or linter config is present. | High |

## User-Confirmed Preferences

| Preference | Enforcement | Confirmed by | Notes |
| --- | --- | --- | --- |
| None captured as durable project preferences in this pass. | preference-only | Not applicable | The user permitted use of installed onboarding skills for this session, but that is not recorded here as a permanent repo standard. |

## Unresolved Questions

| Question | Why it matters | Current default | Needed before |
| --- | --- | --- | --- |
| Should the repo add markdown linting or formatting tools later? | Tooling would change which docs standards can be called tooling-enforced. | Manual markdown review, plus `scripts/validate_skills.py` for skill schema checks. | Adding automated docs checks, CI, or formatter expectations. |
| Should category README files list planned skills before implementation? | Planned-skill catalog entries can make incomplete work look installable. | List implemented skills only; avoid making planned issues look complete. | Expanding category indexes or generated catalog docs. |
| Should future generated indexes be public docs, local-only artifacts, or both? | Generated indexes could affect install docs and repo maintenance. | The hand-maintained V2 registry is the current catalog; no generated indexes. | Designing any generated index workflow. |
| Should installer automation live in this repo or framework-specific adapters later? | It affects the current out-of-scope boundary and future ownership. | No installer tooling in the V2 foundation. | Starting installer automation work. |

## Commands And Checks

| Command | Purpose | Enforcement | Source |
| --- | --- | --- | --- |
| `.gitignore` patterns for `.local/`, `.scratch/`, `tmp/`, `temp/`, logs, and temp files | Keep local, scratch, and private workspace artifacts out of normal tracked work. | tooling-enforced | `.gitignore` |
| `git status --short` | Check worktree state before and after edits. | review-enforced | Used during context and standards creation. |
| `rg --files` | Discover source files without bulk-reading. | review-enforced | Used by `docs/agents/context-matrix.md` and this pass. |
| `rg -n` targeted scans | Find headings, schema references, and documented standards. | review-enforced | Used for issue and standards discovery. |
| Manifest/config discovery with `rg --files -g ...` | Check whether build, test, lint, format, or CI entrypoints exist. | review-enforced | Root `pyproject.toml`, `uv.lock`, and `tests/` support local validation; no CI, formatter, or linter config is present. |
| `uv run python -m unittest discover -s tests -v` | Exercise registry, adaptive-routing, onboarding, and clarification fixture validation behavior. | tooling-enforced | Added by Ticket 001 and extended by Tickets 002-004. |
| `uv run python scripts/validate_skills.py` | Validate implemented skills, the integrated registry, routing, onboarding, and clarification fixture contracts, public-boundary checks, and report-only drift. | tooling-enforced | Extended by Tickets 001-004; uses `pyyaml` and `jsonschema` through `uv`. |
| Manual markdown review | Validate docs-only changes while no automated docs tooling exists. | review-enforced | Current practical default. |

## Enforcement Levels

- `tooling-enforced`: checked by named project tooling, CI, tests, schemas, hooks, generated checks, or Git ignore behavior.
- `review-enforced`: documented or strongly expected but requires human or agent review.
- `preference-only`: user-confirmed or locally preferred, with little or no project evidence.

## Last Updated

- Date: 2026-07-25
- Updated by: Codex
- Evidence used: prior standards evidence; V2 spec and Tickets 001-004; ADR
  0002; `stack/`, including routing, onboarding, and clarification fixtures; local validator
  tooling and tests; targeted catalog, docs-drift, and ticket-state scans;
  fresh validator and unit-test output.
