---
name: context-matrix-map
category: agent-workflows
classification: portable
status: wip
description: Use when onboarding a project for durable agent work, creating a context/source map, or deciding what future agents should read first.
triggers:
  - user asks to onboard a project for durable or repeated agent work
  - user asks for a context map, repo map, source map, or future-agent read order
  - agent needs to create or refresh docs/agents/context-matrix.md
  - target-project delivery would benefit from a durable progressive-disclosure map
outputs:
  - tracked target-project docs/agents/context-matrix.md by default
  - first-read, second-read, and only-if-needed source tiers
  - source-grounded map of docs, code areas, tests, commands, ADRs, and context packs
  - explicit assumptions, gaps, and verification commands used
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before mapping a new or unfamiliar target project
    - project-context-calibration after this map when project language needs a durable context file
    - project-standards-calibration after this map when standards need a durable profile
    - verification-before-completion before claiming the context matrix is complete, evidence-backed, or ready for future agents
  fallback: If companion skills are unavailable, inspect the minimum relevant project files directly and state lower confidence.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Context Matrix Map

## Purpose

Create a durable, source-grounded map of a target project so future agents know where to look first, what to defer, and which sources are only useful for specialized work.

Use this skill during target-project onboarding or when a project lacks a reliable `docs/agents/context-matrix.md`. The result should route future context loading; it should not become a full architecture essay.

## Inputs

- User request or onboarding goal.
- Target-project root path.
- Existing agent instruction files, if present.
- Existing root `CONTEXT.md`, if present.
- Existing project docs, ADRs, issue or PRD folders, test layout, build metadata, and command definitions.
- Existing `docs/agents/` artifacts or context packs, if present.

## Workflow

1. Confirm the target-project boundary:
   - Identify the project root from the user's request, current directory, or repository metadata.
   - Keep installed-skill instructions separate from target-project artifacts.
   - If the root is ambiguous, inspect one local source such as `git rev-parse --show-toplevel`, a package manifest, or a README before asking the user.

2. Discover candidate sources without bulk-reading:
   - List top-level files and directories.
   - Search for likely instruction files, README files, docs indexes, ADRs, issue folders, PRDs, context packs, package manifests, build scripts, test folders, and config files.
   - Prefer fast file discovery commands and targeted file opens over recursive reading.
   - Do not open generated output, dependency folders, lockfiles, binary assets, or large data dumps unless they are the only source for a required fact.

3. Sample sources just enough to classify them:
   - Read short indexes, headings, manifests, command definitions, and nearby docs that explain project conventions.
   - For code areas, identify entrypoints, feature directories, shared libraries, data-access boundaries, and integration surfaces from filenames and shallow reads.
   - For tests, identify test frameworks, locations, naming patterns, and the smallest useful commands.
   - For ADRs and specs, record titles, paths, dates when available, and the decision or product area they govern.

4. Build the matrix using progressive-disclosure tiers:
   - **First-read**: sources future agents should read at the start of most serious sessions.
   - **Second-read**: sources to read after the task surface is known or before changing a relevant area.
   - **Only-if-needed**: deep references, large docs, historical specs, generated files, specialized commands, or narrow subsystems.
   - Put each source in the lowest-context tier that still keeps future agents safe.

5. Cover the required source types:
   - Docs and README files.
   - Existing project context files, such as root `CONTEXT.md`.
   - Code areas and important boundaries.
   - Tests and verification commands.
   - Build, run, lint, format, or release commands.
   - ADRs, PRDs, issues, or decision records.
   - Agent instructions and existing context packs under paths such as `docs/agents/`.

6. Write or update the default tracked artifact:
   - Use `docs/agents/context-matrix.md` unless the user requested another tracked path.
   - Create `docs/agents/` if needed.
   - Preserve useful existing project-specific facts when refreshing the file.
   - Mark uncertainty explicitly instead of filling gaps with speculation.

7. Stop when the map can route future reading:
   - Do not keep exploring to explain every module.
   - Defer architecture diagrams, standards profiles, security review, or detailed delivery planning to companion skills.
   - If the project is too large to map in one pass, write a partial matrix with clear gaps and recommended next scans.
   - Use `verification-before-completion` before claiming the matrix is complete, evidence-backed, or ready for future agents.

## Output Contract

Write `docs/agents/context-matrix.md` with this shape by default:

```markdown
# Context Matrix

## Purpose

One short paragraph describing how future agents should use this map.

## First-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |

## Second-Read Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |

## Only-If-Needed Sources

| Source | Why read it | When to read | Notes |
| --- | --- | --- | --- |

## Code Areas

| Area | Paths | What lives there | Read before |
| --- | --- | --- | --- |

## Tests And Commands

| Command or path | Purpose | When to use | Evidence |
| --- | --- | --- | --- |

## Decisions And Context Packs

| Source | Scope | Status | Notes |
| --- | --- | --- | --- |

## Gaps And Assumptions

- <unknown, stale, or inferred item>

## Last Updated

- Date: <YYYY-MM-DD>
- Updated by: <agent or user label>
- Evidence used: <brief list of commands and paths>
```

After writing the file, report:

- artifact path;
- key first-read sources;
- notable gaps or assumptions;
- verification or discovery commands used.

## Delegation

The main agent owns the target-project boundary, tiering judgment, final artifact, and user communication.

When subagents are available, use them only for bounded scans that can run independently, such as:

- finding docs, ADRs, and context packs;
- identifying code-area entrypoints from a shallow tree scan;
- identifying test frameworks and commands;
- summarizing one named folder or source family.

Require every subagent result to include:

- paths inspected;
- commands run;
- source docs or files used;
- explicit assumptions;
- confidence level or unresolved gaps.

If subagents are unavailable, perform the same scans sequentially with a narrower context budget. Do not treat unevidenced summaries as project facts.

## Guardrails

- Do not bulk-read the repository.
- Do not turn the context matrix into a broad architecture essay, exhaustive file inventory, onboarding tutorial, or handoff.
- Do not rank sources by personal preference; tier them by when future agents need them.
- Do not include private notes, ignored local scratch files, credentials, client data, or sensitive personal context unless the user explicitly requests a private artifact.
- Do not assume every project has GOATED artifacts, ADRs, tests, or agent instruction files.
- Do not claim commands work unless they were discovered from project files or actually run.
- Keep entries brief, evidence-based, and path-oriented.
- Prefer "unknown" or "not found in this pass" over guessing.

## References

No external references are required. This skill is self-contained after installation.
