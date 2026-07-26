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
| Keep descriptive architecture mapping, prescriptive architecture design, and review-only architecture assessment as separate routes. Use the smallest useful representation instead of defaulting to Mermaid. | review-enforced | `docs/specs/2026-07-25-goated-ai-skills-v2.md`, architecture skill bodies, `stack/fixtures/architecture-planning/`, `scripts/validate_skills.py` | Canonical V2 skills are `architecture-design-map`, `design-codebase-architecture`, and `review-codebase-architecture`; old design/review names remain registry aliases only. Fixtures and validator checks enforce the mechanical route contract. |
| Use inline implementation plans for focused single-session work and durable tracked plans for resumable, delegated, architectural, or multi-surface work. Promote by reusing fresh evidence and settled decisions. | review-enforced | `docs/specs/2026-07-25-goated-ai-skills-v2.md`, `skills/engineering/writing-plans/SKILL.md`, `stack/fixtures/architecture-planning/` | Each plan emits one justified next-step signal rather than duplicating the downstream pipeline. Fixtures and validator checks enforce the mechanical mode and promotion contract. |
| Slice delivery tickets vertically by default; use expand-migrate-contract only for broad mechanical changes that cannot land as independently green vertical slices. | tooling-and-review-enforced | `docs/specs/2026-07-26-selective-upstream-skill-adoption.md`, `skills/engineering/spec-to-tickets/`, `stack/fixtures/planning/`, `scripts/validate_skills.py` | Migration batches use evidence-backed blast-radius boundaries, contract waits for every batch and proves no old caller remains, and multi-ticket order output reports the computed ready frontier. Integration branches require evidence that batches cannot stay green independently. |
| Prove behavior at the smallest stable observable boundary; record why equivalent non-TDD proof is needed; activate full refinement only by explicit request or concrete debt; and parallelize delegated implementation only from a concrete non-overlapping task board with settled interfaces. | tooling-and-review-enforced | `docs/specs/2026-07-25-goated-ai-skills-v2.md`, diagnosis/TDD/refinement/delegation skill bodies, `stack/fixtures/behavior-proof/`, `scripts/validate_skills.py` | Unit, property, component, contract, integration, and end-to-end surfaces are all valid when they are the smallest stable boundary. Local refactor-after-green remains inside TDD. |
| Keep fresh claim-scoped evidence universal while loading full verification, standards/spec review, and security review only for matching complexity, risk, uncertainty, delegation, audit, trust-boundary, or sensitive-surface conditions. | tooling-and-review-enforced | `docs/specs/2026-07-25-goated-ai-skills-v2.md`, `stack/AGENTS.md`, review/verification skill bodies, `stack/fixtures/review-verification/`, `scripts/validate_skills.py` | Narrow work verifies directly. Specialists reuse envelope evidence and return findings, classifications, proof gaps, or route deltas to one consolidated closeout. |
| Use Wayfinder only for branching uncertainty that exceeds one focused session. Approve the destination, location, visible frontier, action reach, and initial write scope before chart creation; keep production execution outside the map. | review-enforced | `docs/specs/2026-07-25-goated-ai-skills-v2.md`, `skills/agent-workflows/wayfinder/SKILL.md`, `stack/fixtures/wayfinding/` | Session-sized discussion and already-specified large implementation route elsewhere. Local maps use `docs/wayfinding/<effort-slug>/` when no configured tracker is used; decision type and `AFK`/`HITL` mode are independent. |
| Retrieve durable project knowledge progressively and read-only; rank it for the exact claim and report stale or conflicting sources instead of mutating or silently merging them. | tooling-and-review-enforced | `skills/productivity/knowledge-retrieval/SKILL.md`, `stack/fixtures/knowledge-retrieval/`, `scripts/validate_skills.py` | Ordinary files are the portable fallback. Note nurturing belongs to a separate `learning-capture` run; external web research is out of scope. |
| Research current external questions against a question-specific source hierarchy; prefer primary sources, preserve claim-scoped provenance and freshness, distinguish findings from inference and uncertainty, and keep durable capture optional. | tooling-and-review-enforced | `docs/specs/2026-07-26-selective-upstream-skill-adoption.md`, `skills/engineering/source-grounded-research/`, `stack/fixtures/source-grounded-research/`, `scripts/validate_skills.py` | Inline read-only output is complete. Durable capture reuses a project-owned convention or the external-doc lookup-note convention; local project retrieval remains with `knowledge-retrieval`. |
| Preserve project setup through one ordered current recipe with per-step evidence states; reference declarative sources, select the gate only on reproducibility impact, and separate automation creation from execution. | tooling-and-review-enforced | `skills/productivity/setup-scribe/SKILL.md`, `stack/fixtures/setup-scribe/`, `stack/goated-stack.yaml`, `scripts/validate_skills.py` | Scribe is project-first and Bash-first. Machine-wide, external, sensitive, or unsafe actions retain approval and security gates. |
| Resolve active Git conflicts from operation-aware, two-sided intent evidence; preserve compatible intent, surface incompatible decisions, allow safe stop or abort, and keep lifecycle authority separate from skill loading. | tooling-and-review-enforced | `docs/specs/2026-07-26-selective-upstream-skill-adoption.md`, `skills/engineering/resolving-merge-conflicts/`, `stack/fixtures/merge-conflicts/`, `scripts/validate_skills.py` | Applies to in-progress merges, rebases, cherry-picks, and reverts. Static fixtures enforce the portable contract; live RED/GREEN pressure evaluation supplies behavioral evidence. |

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
| Docs-only changes still require manual markdown review outside validator-covered skill, registry, and fixture-contract checks; GitHub Actions runs the repository acceptance commands but no formatter or linter is configured. | review-enforced | Root `pyproject.toml`, `uv.lock`, `.github/workflows/validate.yml`, `scripts/validate_skills.py`, and `tests/`. | High |

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
| Should installer automation live in this repo or framework-specific adapters later? | It affects the current out-of-scope boundary and future ownership. | No installer tooling in V2. | Starting installer automation work. |

## Commands And Checks

| Command | Purpose | Enforcement | Source |
| --- | --- | --- | --- |
| `.gitignore` patterns for `.local/`, `.scratch/`, `tmp/`, `temp/`, logs, and temp files | Keep local, scratch, and private workspace artifacts out of normal tracked work. | tooling-enforced | `.gitignore` |
| `git status --short` | Check worktree state before and after edits. | review-enforced | Used during context and standards creation. |
| `rg --files` | Discover source files without bulk-reading. | review-enforced | Used by `docs/agents/context-matrix.md` and this pass. |
| `rg -n` targeted scans | Find headings, schema references, and documented standards. | review-enforced | Used for issue and standards discovery. |
| Manifest/config discovery with `rg --files -g ...` | Check whether build, test, lint, format, or CI entrypoints exist. | review-enforced | Root `pyproject.toml`, `uv.lock`, `.github/workflows/validate.yml`, and `tests/` support local and CI validation; no formatter or linter config is present. |
| `uv run python -m unittest discover -s tests -v` | Exercise registry, canonical-reference, focused-fixture, end-to-end fixture, and V1/V2 context-comparison behavior. | tooling-enforced | Added by Ticket 001 and extended through Tickets 012, 014, 018, and 019. |
| `uv run python scripts/validate_skills.py` | Validate implemented skills, links, canonical references, registry and aliases, signals, focused and end-to-end fixture contracts, public-boundary checks, word budgets, and report-only drift. | tooling-enforced | Extended by Tickets 001-012, 014, 018, and 019; uses `pyyaml` and `jsonschema` through `uv`. |
| `uv run python scripts/compare_v1_v2_context.py` | Compare four representative V2 route-specific instruction sets with the preserved `v1-baseline` tag and report shared-policy cost separately. | tooling-enforced | Ticket 012 release-conformance proof. |
| Manual markdown review | Validate docs-only changes while no automated docs tooling exists. | review-enforced | Current practical default. |

## Enforcement Levels

- `tooling-enforced`: checked by named project tooling, CI, tests, schemas, hooks, generated checks, or Git ignore behavior.
- `review-enforced`: documented or strongly expected but requires human or agent review.
- `preference-only`: user-confirmed or locally preferred, with little or no project evidence.

## Last Updated

- Date: 2026-07-26
- Updated by: Codex
- Evidence used: prior standards evidence; V2 spec and Tickets 001-012 and 014;
  ADR
  0002; `stack/`, including routing, onboarding, clarification,
  specification/ticket, architecture, implementation-planning, behavior-proof,
  review/verification, merge-conflict, Wayfinding, knowledge-retrieval,
  source-grounded-research, Setup Scribe, and end-to-end
  fixtures; context-comparison tooling; local validator and tests; migration
  and acceptance docs; targeted catalog, docs-drift, and ticket-state scans.
