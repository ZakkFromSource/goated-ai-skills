---
name: agent-instructions-integrator
category: agent-workflows
classification: portable
status: wip
description: Use when integrating installed GOATED skills into a target project, creating or updating agent instructions, or routing agents to durable project artifacts.
triggers:
  - user asks to integrate installed GOATED skills into a target project
  - user asks to create, update, or repair agent instructions for a project
  - target-project onboarding needs routing to context and standards artifacts
  - an agent framework needs a thin adapter to installed skill folders
outputs:
  - selected target-project instruction artifact or configuration
  - installed skill routing notes
  - target-project artifact routing notes
  - unresolved framework assumptions or follow-up questions
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before integrating an unfamiliar target project
    - context-matrix-map when routing should reference docs/agents/context-matrix.md
    - project-context-calibration when routing should reference root CONTEXT.md
    - project-standards-calibration when routing should reference docs/agents/project-standards.md
  fallback: If companion skills or target-project artifacts are unavailable, create a minimal framework-specific router and state what could not be verified.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Agent Instructions Integrator

## Purpose

Add a thin target-project routing layer that tells the user's chosen agent framework when to use installed GOATED skills and durable project artifacts.

Use this skill after core onboarding artifacts exist, or when a target project needs a small instruction adapter. The adapter should route to installed skills; it should not copy full skill bodies or turn one framework's filename convention into a universal rule.

## Inputs

- User request and chosen agent framework, if already known.
- Target-project root path.
- Installed GOATED skill location, registry, or framework-specific skill discovery path, if known.
- Existing target-project agent instruction files, command files, skill registries, or framework config.
- Existing root `CONTEXT.md`, if present.
- Existing `docs/agents/context-matrix.md` and `docs/agents/project-standards.md`, if present.
- Framework docs or user-provided framework conventions, when local evidence is insufficient.

## Workflow

1. Confirm target-project boundary:
   - Identify the project root from the user's request, current directory, or repository metadata.
   - Keep this source library, installed skill folders, and target-project instruction artifacts distinct.
   - Do not edit anything until the target project and intended framework are clear enough.

2. Detect or accept the chosen framework before editing:
   - Prefer an explicit user choice when provided.
   - Otherwise inspect shallow local evidence: existing instruction files, framework config, skill registries, command folders, README notes, or tool-specific project metadata.
   - Consider Codex, Claude Code, Hermes, OpenCode, and generic agent-framework routing.
   - If two frameworks are plausible, ask which one should own the target-project adapter before changing files.

3. Select the instruction artifact or configuration:
   - For Codex-style workflows, use the configured repo instruction artifact when present; create a thin adapter only when the user's environment expects one.
   - For Claude Code-style workflows, use the supported project instruction, command, or skill routing artifact for that project.
   - For Hermes-style workflows, use the configured skill registry, workflow index, or project instruction entrypoint when present.
   - For OpenCode-style workflows, use the configured reusable instruction location or the project's existing single instruction file if that is how the project is set up.
   - For generic agents, use the user-selected instruction artifact; if none exists, propose a tracked docs router such as `docs/agents/agent-routing.md` and tell the user how to connect it to their framework.

4. Inspect before patching:
   - Read the selected artifact and nearby routing docs before editing.
   - Preserve existing project rules, safety notes, and framework-specific syntax.
   - Prefer adding or updating a small named routing section over rewriting the whole file.
   - If the file contains conflicting guidance, surface the conflict before deciding how to merge it.

5. Route to installed skills:
   - Point agents to the installed skill location or framework registry when known.
   - Name the relevant installed GOATED skills instead of pasting their full contents.
   - Include the onboarding route in brief: context matrix, standards profile, instruction routing, optional handoff.
   - Include the delivery route only as a compact pointer to the installed delivery skills, not a full workflow dump.

6. Route to target-project artifacts:
   - Tell future agents to read root `CONTEXT.md` when it exists for project language, boundaries, and durable artifact definitions.
   - Tell future agents to read `docs/agents/context-matrix.md` when it exists for source discovery.
   - Tell future agents to read `docs/agents/project-standards.md` when standards affect the work.
   - Tell future agents to use ignored `.local/` paths only for session-private notes, handoffs, or scratch artifacts when the project uses them.
   - State lower confidence if these artifacts are missing or not yet calibrated.

7. Verify the adapter:
   - Re-read the edited artifact.
   - Check that it names the selected framework, selected artifact, installed skill routing, target-project artifact routing, and unresolved assumptions.
   - Check that it does not paste full GOATED skill bodies or treat any one filename as universal.

## Output Contract

Update the selected target-project instruction artifact or configuration with a concise routing section. Use this shape when the framework syntax allows plain Markdown:

```markdown
## GOATED Skill Routing

- Framework: <Codex | Claude Code | Hermes | OpenCode | generic agent | other confirmed framework>
- Installed skills: <path, registry, or "installed in framework; exact path not verified">
- Start serious project work with `session-start-progressive-disclosure`.
- Use root `CONTEXT.md` for project language and boundaries when present.
- Use `docs/agents/context-matrix.md` for source discovery when present.
- Use `docs/agents/project-standards.md` for project standards when present.
- Use installed GOATED skills by name; do not copy skill bodies into this file.
- Unresolved assumptions: <none or concise list>
```

After editing, report:

- selected framework;
- selected instruction artifact or configuration;
- installed skill routing added or changed;
- target-project artifact routing added or changed;
- unresolved framework assumptions;
- files changed.

If no safe artifact can be selected, do not edit. Return the same report shape with the candidate artifacts and the one user decision needed.

## Delegation

The main agent owns framework selection, edit strategy, final patch, and user communication.

When subagents are available, use them only for bounded evidence scans, such as:

- finding existing framework instruction artifacts;
- checking whether `docs/agents/` artifacts exist;
- summarizing one candidate instruction file;
- identifying installed skill registry paths from local config.

Require every subagent result to include:

- paths inspected;
- commands run;
- framework signals found;
- explicit assumptions and confidence;
- recommended artifact candidates, not direct edits.

If subagents are unavailable, perform the same scans sequentially with a narrower context budget.

## Guardrails

- Do not assume `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, or any one filename is universal.
- Do not paste the full GOATED onboarding or delivery workflow into every target project.
- Do not copy full `SKILL.md` bodies into target-project instructions.
- Do not edit instructions before detecting or confirming the chosen framework.
- Do not overwrite existing project-specific rules, safety notes, or framework syntax.
- Do not route to target-project artifacts that do not exist without marking them missing or planned.
- Do not include private notes, ignored local scratch files, credentials, client data, or sensitive personal context unless the user explicitly requests a private artifact.
- Prefer a small router that points to installed skills and durable target-project artifacts.

## References

No external references are required. This skill is self-contained after installation.
