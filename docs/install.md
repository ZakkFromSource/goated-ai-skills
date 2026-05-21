# Install And Adapt GOATED AI Skills

GOATED AI Skills is distributed as a public source library of skill folders. V1 installation is docs-first: copy, install, or adapt the skill folders into the agent framework you already use.

Only completed skill folders are installable. Local implementation issue handoffs define the order for creating the remaining V1 skills. This document defines the intended installation model for V1.

## Three Layers

Layer 0: Skill Pack Distribution

- Clone, download, copy, or install skill folders from this repo.
- Put them where your chosen agent framework discovers skills, commands, prompts, or workflow files.
- Do not treat this repo as a template that must be cloned into every target project.

Layer 1: Target Project Onboarding

- Run the installed onboarding skills inside a project before durable, cross-file, PRD-level, architectural, or repeated work.
- Use onboarding to create durable target-project artifacts such as root `CONTEXT.md`, `docs/agents/context-matrix.md`, `docs/agents/project-standards.md`, and `docs/agents/architecture-plan.md` when a project-wide architecture blueprint is useful.
- Use the OS temp directory for handoffs by default, under `goated-handoffs/<project-name>/`.
- Use ignored `.local/` in the target project for private scratch notes and other temporary workspace artifacts.

Layer 2: Target Project Delivery

- Use the installed delivery skills inside the target project for PRDs, architecture plans, issues, prototypes, TDD, review, security checks, docs, commit messages, and handoffs.

## Generic Install Pattern

1. Choose the skill folders you want from `skills/`.
2. Copy those folders into your agent framework's skill or workflow location.
3. Keep each skill folder intact, including its `SKILL.md` and any `references/`, `scripts/`, or `assets/`.
4. If your agent framework needs a routing file, add a short instruction that tells it when to use the installed skills.
5. Do not require the copied skills to load this repo's root `AGENT.md`, `README.md`, or `CONTEXT.md`.

Installed skills should be self-contained. They may reference files inside their own skill folder, but should not depend on this source repo at runtime.

Use `using-goated-ai-skills` as the portable router when an installed stack needs to choose the right GOATED workflow. It is docs-first guidance for skill selection, not runtime bootstrap, hook installation, automatic loading, or adapter manifest generation.

## Codex Notes

For Codex-style skill systems, copy skill folders into the configured skills directory or project skill location supported by your environment. Keep the folder name and `SKILL.md` together.

If the environment supports repo instructions, use a thin adapter that routes Codex to the installed skills and target-project artifacts. Do not paste the full GOATED workflow into every target project.

## Claude Code Notes

For Claude Code-style workflows, adapt each skill into the supported command, skill, or instruction format for that environment. If a project instruction file is used, keep it short and route to the installed skills.

Use `agent-instructions-integrator` to help create the correct target-project routing instructions.

## Hermes Notes

For Hermes-style workflows, copy or adapt GOATED skill folders into the Hermes skill/workflow location. Preserve the skill body and references so each skill remains self-contained.

If Hermes uses a central skill registry or index, add the installed skills there without making them depend on this source repo.

## OpenCode Notes

For OpenCode-style workflows, place copied or adapted skills wherever OpenCode expects reusable agent instructions. If the framework uses a single instruction file, keep it as a router to installed skills rather than a duplicate of every skill body.

## Target Project Artifacts

Installed skills should use these defaults around a target project:

```text
CONTEXT.md                         tracked durable project context and language
docs/agents/context-matrix.md      tracked durable context map
docs/agents/project-standards.md   tracked durable standards profile
docs/agents/architecture-plan.md   tracked project-wide architecture blueprint when useful
docs/architecture/                 tracked feature-specific architecture blueprints when useful
<os-temp>/goated-handoffs/<project-name>/ temporary handoff notes
.local/scratch/                    ignored temporary notes or experiments
```

Durable project facts should be tracked. Temporary handoffs should live outside the workspace in OS temp unless the user explicitly requests a tracked handoff. Session-private workspace artifacts should be ignored.

## Out Of Scope For V1

- Installer scripts.
- Automatic framework detection.
- Generated skill indexes.
- Compatibility testing across every agent framework.
- Adapter repair automation.
