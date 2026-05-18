---
name: project-context-calibration
category: agent-workflows
classification: portable
status: wip
description: Create or refresh a target project's root CONTEXT.md so future agents share project boundaries, domain language, durable artifact definitions, and reusable architecture vocabulary.
triggers:
  - user asks to onboard a project for durable or repeated agent work
  - user asks to create, refresh, calibrate, or curate a project context file
  - agent needs to create or update root CONTEXT.md inside a target project
  - future delivery work depends on shared project boundaries, terms, artifacts, or architecture vocabulary
outputs:
  - tracked target-project root CONTEXT.md by default
  - project boundaries and non-boundaries
  - domain language and durable artifact definitions
  - reusable architecture vocabulary for future agents
  - explicit gaps, assumptions, and evidence used
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before calibrating a new or unfamiliar target project
    - context-matrix-map when docs/agents/context-matrix.md exists or source discovery is needed
    - grill-with-docs when project language, boundaries, or artifact definitions require user decisions
    - project-standards-calibration after this context file when standards need a separate durable profile
    - agent-instructions-integrator after this context file when agent routing should reference root CONTEXT.md
  fallback: If companion skills or project docs are unavailable, inspect the minimum relevant local evidence directly and mark lower-confidence gaps in CONTEXT.md.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Project Context Calibration

## Purpose

Create or curate a durable target-project `CONTEXT.md` that gives future agents one shared vocabulary for the project.

Use this skill during target-project onboarding, before repeated delivery work, or when agents keep confusing project boundaries, domain terms, artifact meanings, or reusable architecture language. The file should orient future agents; it should not replace source maps, standards profiles, architecture diagrams, ADRs, PRDs, handoffs, or refactor plans.

## Inputs

- User request or onboarding goal.
- Target-project root path.
- Existing `docs/agents/context-matrix.md`, if present.
- Existing root `CONTEXT.md`, if refreshing.
- Existing `docs/agents/project-standards.md`, if present.
- Project README files, docs indexes, glossary or domain docs, ADRs, PRDs, issue templates, architecture notes, agent instructions, and public docs.
- Representative source or tests only when docs are missing, stale, or insufficient to ground important project language.
- User decisions about project terms, scope boundaries, and artifact meanings when local evidence cannot settle them.

## Workflow

1. Confirm the target-project boundary:
   - Identify the project root from the user request, current directory, or repository metadata.
   - Treat the `CONTEXT.md` being written as the target project's root context file.
   - Keep this source skill library, installed skill folders, and target-project artifacts distinct.
   - If the root is ambiguous, inspect one local source such as `git rev-parse --show-toplevel`, a package manifest, or a README before asking the user.

2. Use the context matrix when present:
   - If `docs/agents/context-matrix.md` exists, read it first and use its first-read and second-read sources to choose evidence.
   - If no context matrix exists, do a narrow discovery pass for README files, docs indexes, existing context or glossary docs, ADRs, PRDs, agent instructions, and project manifests.
   - Do not recreate the context matrix inside `CONTEXT.md`; use it only to find source-grounded context.

3. Inspect the existing context file when refreshing:
   - Read root `CONTEXT.md` before editing it.
   - Preserve accurate project-specific facts, terms, and artifact definitions.
   - Mark stale, conflicting, or weakly sourced content as a gap or assumption instead of silently deleting project knowledge.
   - Do not confuse the target project's root `CONTEXT.md` with this GOATED source repo's root `CONTEXT.md`.

4. Calibrate project boundaries:
   - Capture what the project is, what it is not, and which adjacent systems, packages, products, repositories, or domains are outside its scope.
   - Include public/private boundaries when they matter for future agents.
   - Prefer source-backed statements from docs, manifests, repo layout, ADRs, or user-confirmed decisions.
   - Ask only when a boundary is materially ambiguous and cannot be inferred from local evidence.

5. Calibrate domain language:
   - Collect terms future agents must use consistently, such as product concepts, actors, workflows, feature names, status labels, data concepts, and overloaded words.
   - Define terms from project evidence first and user clarification second.
   - Keep definitions short and operational: what the term means in this project and where the evidence came from.
   - Avoid broad glossary building when the terms do not affect agent work.

6. Calibrate durable artifact definitions:
   - Define durable project artifacts that future agents should recognize, such as `CONTEXT.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, PRDs, ADRs, issue handoffs, public docs, and local handoffs when the project uses them.
   - For each artifact, capture its purpose, default path or convention, whether it is tracked or local, and what it should not replace.
   - Keep standards and enforcement rules in `docs/agents/project-standards.md`, not in `CONTEXT.md`.

7. Calibrate reusable architecture vocabulary:
   - Capture stable architecture terms future agents need across tasks, such as feature, module, service, adapter, seam, layer, package, route, schema, or project-specific equivalents.
   - Ground terms in docs or representative source structure when possible.
   - Keep this to vocabulary and orientation. Do not draw diagrams, evaluate architecture quality, propose refactors, or invent new architectural decisions.
   - If architecture terms are contested or decision-heavy, record the gap and recommend an ADR or architecture-design-map follow-up.

8. Write or update the default tracked artifact:
   - Use root `CONTEXT.md` inside the target project unless the user explicitly requested another tracked path.
   - Preserve useful existing content while reshaping it into the output contract when needed.
   - Include gaps and assumptions instead of pretending weak evidence is settled.
   - Date the update and list the main evidence paths and commands used.

9. Stop when future agents share the same language:
   - Do not keep exploring to map every source file or explain every subsystem.
   - Defer source-routing gaps to `context-matrix-map`.
   - Defer standards, coding conventions, and enforcement levels to `project-standards-calibration`.
   - Defer diagrams and source-grounded architecture maps to `architecture-design-map`.
   - Defer refactor recommendations to architecture improvement or delivery-specific workflows.

## Output Contract

Write root `CONTEXT.md` with this shape by default:

```markdown
# Project Context

## Purpose

One short paragraph explaining how future agents should use this file.

## Project Boundaries

| Boundary | In scope | Out of scope | Evidence or notes |
| --- | --- | --- | --- |

## Domain Language

| Term | Meaning in this project | Evidence or notes |
| --- | --- | --- |

## Durable Artifacts

| Artifact | Default path | Purpose | Notes |
| --- | --- | --- | --- |

## Architecture Vocabulary

| Term | Meaning in this project | Evidence or notes |
| --- | --- | --- |

## Gaps And Assumptions

- <unknown, weakly sourced, stale, or user-confirmed assumption>

## Last Updated

- Date: <YYYY-MM-DD>
- Updated by: <agent or user label>
- Evidence used: <brief list of paths and commands>
```

After writing the file, report:

- artifact path;
- key project boundaries and terms captured;
- gaps or assumptions that still need the user;
- evidence paths and commands used;
- recommended next onboarding skill, if any.

## Delegation

The main agent owns the target-project boundary, final terminology, user questions, context-file edits, and user communication.

When subagents are available, use them only for bounded evidence scans, such as:

- terminology in docs, README files, glossary files, specs, PRDs, or issues;
- existing durable artifacts under root docs or `docs/agents/`;
- architecture-language terms in ADRs, architecture notes, package layout, or representative source files;
- contradictions between existing `CONTEXT.md` and current project evidence.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately skipped;
- exact source evidence found;
- explicit assumptions and confidence;
- candidate terms, artifact definitions, or contradictions, not final `CONTEXT.md` prose.

If subagents are unavailable, perform the same scans sequentially with a narrower context budget. Do not promote unevidenced summaries into project context.

## Guardrails

- Do not ask the user about discoverable facts before inspecting available project evidence.
- Do not treat this GOATED source repo's root `CONTEXT.md` as the target project's context unless this source repo is explicitly the target project.
- Do not make `CONTEXT.md` a source map, exhaustive glossary, onboarding tutorial, standards profile, architecture diagram, ADR, PRD, handoff, or refactor plan.
- Do not duplicate `docs/agents/context-matrix.md`; use it to find sources and leave source read-order there.
- Do not duplicate `docs/agents/project-standards.md`; leave standards, conventions, preferences, checks, and enforcement levels there.
- Do not invent architecture vocabulary, project boundaries, or artifact meanings without source evidence or user confirmation.
- Do not include ignored local scratch files, private notes, credentials, client data, or sensitive personal context unless the user explicitly requests a private artifact.
- Prefer "unknown", "not found in this pass", or an unresolved question over guessing.

## References

No external references are required. This skill is self-contained after installation.
