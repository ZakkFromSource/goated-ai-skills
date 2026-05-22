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
| Use OS temp `goated-handoffs/<project-name>/` for default handoffs and `.local/` for private planning or session-local workspace notes; do not make public behavior depend on either. | review-enforced | `.gitignore`, `AGENT.md`, `README.md`, `docs/install.md`, `skills/agent-workflows/handoff/SKILL.md` | Git ignores `.local/`; OS temp is outside the project workspace and may be cleaned by the OS. Public-safety still requires review judgment. |
| Add new skill folders and `SKILL.md` files only for a specific approved implementation issue. | review-enforced | `AGENT.md`, `README.md`, `skills/README.md` | Category indexes alone are not approval to create a skill. |
| Keep V1 installation docs-first; installer automation is out of scope for V1. | review-enforced | `docs/install.md`, `issues/prd-goated-ai-skills-v1-public-core.md`, `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` | Completed skill folders are copied, installed, or adapted manually. V1 allows narrow adapter notes only, not runtime bootstrap or automatic activation. |
| Keep installed skill folders self-contained after installation. | review-enforced | `AGENT.md`, `README.md`, `skills/README.md`, `docs/install.md` | A copied skill can reference its own folder, not this repo's root files. |
| Use the lean skill schema for implemented `SKILL.md` files. | review-enforced | `skills/README.md`, `issues/prd-goated-ai-skills-v1-public-core.md`, implemented skill inventory | Required frontmatter includes name, category, classification, status, description, triggers, outputs, depends_on, and adapters. `description` is discovery-only and should say when to load the skill, not summarize workflow. |
| Use only public V1 categories unless a future public-safe category is intentionally added. | review-enforced | `CONTEXT.md`, `skills/README.md`, `README.md` | Current public categories are `agent-workflows`, `engineering`, and `productivity`. |
| Keep `SKILL.md` lean and move detailed examples, prompt templates, anti-pattern catalogs, rationalization tables, stack-specific notes, scripts, and reusable assets into directly linked support files. | review-enforced | `AGENT.md`, `CONTEXT.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-public-core.md` | The 300-line threshold is a soft review threshold, not an automated check. `references/`, `scripts/`, and `assets/` are first-class support files when they improve skill capability or keep the main workflow lean. |
| Make dependency behavior explicit. | review-enforced | `AGENT.md`, `skills/README.md` | Name hard dependencies, soft dependencies, and graceful fallbacks when relevant. |
| Keep root adapter files thin and routed to `AGENT.md`. | review-enforced | `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, `docs/install.md` | Do not paste full workflows into adapter files. |
| Use explicit discipline gates where workflow pressure makes shortcuts likely. | review-enforced | `CONTEXT.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-superpowers-absorption.md` | Discipline-heavy skills may use stop rules, proof gates, rationalization counters, red flags, or anti-pattern references. |
| Make workflows subagent-aware and single-agent-compatible. | review-enforced | `AGENT.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-public-core.md` | Subagents must return evidence; the main agent owns final judgment. Delegated workflows should use status enums such as `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED` when subagent results can change the controller's next action; simple evidence scans can use lighter evidence, assumption, uncertainty, and inspected-path requirements. |
| Use progressive disclosure instead of broad context loading. | review-enforced | `AGENT.md`, `skills/README.md`, `docs/agents/context-matrix.md` | Load root guidance, then relevant issue/category/skill sources only as needed. |
| Store durable target-project context in tracked files such as root `CONTEXT.md` and agent artifacts under `docs/agents/`; keep default handoffs in OS temp and other session/private workspace artifacts ignored under `.local/`. | review-enforced | `.gitignore`, `AGENT.md`, `README.md`, `docs/install.md`, `skills/agent-workflows/handoff/SKILL.md` | `docs/agents/` and root Markdown files are tracked by default; `.local/` is ignored, while OS temp is outside the workspace. |

## Inferred Conventions

| Convention | Enforcement | Evidence | Confidence |
| --- | --- | --- | --- |
| Markdown is the primary artifact format. | review-enforced | Root docs, issue files, category READMEs, implemented skills, and `docs/agents/context-matrix.md` | High |
| Use ATX headings, concise paragraphs, bullet lists, and fenced code blocks for examples or directory layouts. | review-enforced | `README.md`, `docs/install.md`, `skills/README.md`, `issues/prd-goated-ai-skills-v1-public-core.md` | High |
| Use kebab-case names for skill folders and implemented skill names. | review-enforced | Implemented skill folders under `skills/agent-workflows/`, `skills/engineering/`, and `skills/productivity/` | High |
| Implemented skills live at `skills/<category>/<skill-name>/SKILL.md`. | review-enforced | `skills/README.md`, implemented skill inventory across all three categories | High |
| Existing implemented skills use structured `depends_on` with `hard`, `soft`, and `fallback` entries. | review-enforced | Implemented `SKILL.md` frontmatter across all three categories | High |
| Existing implemented skills use adapter maps for Codex, Claude Code, Hermes, OpenCode, and generic agents. | review-enforced | Implemented `SKILL.md` frontmatter across all three categories | High |
| Skill bodies commonly include Purpose, Inputs, Workflow, Output Contract, Delegation, Guardrails, and References. | review-enforced | Implemented `SKILL.md` headings across all three categories | High |
| Issue handoffs use numbered filenames and standard sections such as Parent PRD, Type, What to build, Acceptance criteria, Blocked by, and User stories addressed. | review-enforced | `issues/*.md`, `issues/archive/*.md` heading scan | High |
| Completed implementation issues move under `issues/archive/` only after acceptance criteria are checked and any required user, maintainer, PR, or project-defined review is complete. | review-enforced | `CONTEXT.md`; archived issues `001` through `020`, `022` through `027`, `029`, and `033` through `043`; active issue list retains `021`, `028`, and `030` through `032` | High |
| Docs-only changes currently rely on manual markdown review. | review-enforced | No manifest, CI, formatter, linter, or test config found in this pass | High |

## User-Confirmed Preferences

| Preference | Enforcement | Confirmed by | Notes |
| --- | --- | --- | --- |
| None captured as durable project preferences in this pass. | preference-only | Not applicable | The user permitted use of installed onboarding skills for this session, but that is not recorded here as a permanent repo standard. |

## Unresolved Questions

| Question | Why it matters | Current default | Needed before |
| --- | --- | --- | --- |
| Should the repo add markdown linting or formatting tools later? | Tooling would change which standards can be called tooling-enforced. | Manual markdown review only. | Adding automated docs checks, CI, or formatter expectations. |
| Should category README files list planned skills before implementation? | The PRD names this as an open question and it affects public docs shape. | List implemented skills only; avoid making planned issues look complete. | Expanding category indexes or generated catalog docs. |
| Should future generated indexes be public docs, local-only artifacts, or both? | Generated indexes could affect install docs and repo maintenance. | No generated indexes in V1. | Designing any generated index workflow. |
| Should installer automation live in this repo or framework-specific adapters later? | It affects V1 out-of-scope boundaries and future ownership. | No installer tooling in V1. | Starting installer automation work. |

## Commands And Checks

| Command | Purpose | Enforcement | Source |
| --- | --- | --- | --- |
| `.gitignore` patterns for `.local/`, `.scratch/`, `tmp/`, `temp/`, logs, and temp files | Keep local, scratch, and private workspace artifacts out of normal tracked work. | tooling-enforced | `.gitignore` |
| `git status --short` | Check worktree state before and after edits. | review-enforced | Used during context and standards creation. |
| `rg --files` | Discover source files without bulk-reading. | review-enforced | Used by `docs/agents/context-matrix.md` and this pass. |
| `rg -n` targeted scans | Find headings, schema references, and documented standards. | review-enforced | Used for issue and standards discovery. |
| Manifest/config discovery with `rg --files -g ...` | Check whether build, test, lint, format, or CI entrypoints exist. | review-enforced | No matches found in this pass. |
| Manual markdown review | Validate docs-only changes while no automated docs tooling exists. | review-enforced | Current practical default. |

## Enforcement Levels

- `tooling-enforced`: checked by named project tooling, CI, tests, schemas, hooks, generated checks, or Git ignore behavior.
- `review-enforced`: documented or strongly expected but requires human or agent review.
- `preference-only`: user-confirmed or locally preferred, with little or no project evidence.

## Last Updated

- Date: 2026-05-22
- Updated by: Codex
- Evidence used: installed `project-standards-calibration` and `doc-sync`; `docs/agents/context-matrix.md`; `AGENT.md`; `AGENTS.md`; `CLAUDE.md`; `CONTEXT.md`; `README.md`; `docs/install.md`; `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`; `skills/README.md`; category READMEs; implemented `SKILL.md` frontmatter across all three categories; `.gitignore`; `.out-of-scope/future-automation-and-validation.md`; V1 PRDs; active issues `021`, `028`, and `030` through `032`; archived issues `001` through `020`, `022` through `027`, `029`, and `033` through `043`; issue scans; manifest/config discovery; test/spec discovery; `git status --short`.
