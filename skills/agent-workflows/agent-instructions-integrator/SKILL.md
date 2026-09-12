---
name: agent-instructions-integrator
description: Use when integrating installed GOATED skills into a target project, creating or updating agent instructions, or routing agents to durable project artifacts.
metadata:
  goated-category: agent-workflows
---

# Agent Instructions Integrator

## Purpose

Add a thin target-project routing layer that tells the user's chosen agent framework when to use installed GOATED skills and durable project artifacts.

Use this skill whenever the selected onboarding budget includes thin policy or
framework routing. Lightweight onboarding may stop here after reusing existing
docs; context, source-map, and standards artifacts do not need to exist.

## Inputs

- User request and chosen agent framework, if already known.
- Target-project root path.
- Installed GOATED skill location, registry, or framework-specific skill discovery path, if known.
- Existing target-project agent instruction files, command files, skill registries, or framework config.
- Existing root `CONTEXT.md`, if present.
- Existing `docs/agents/context-matrix.md` and `docs/agents/project-standards.md`, if present.
- Framework docs or user-provided framework conventions, when local evidence is insufficient.

## Dependencies

Hard: None.

Soft:
- using-goated-ai-skills for installed-stack entrypoint or task-surface routing
- goated-prompt for prompt-crafting, reusable prompt, or GOATED-aware routing
- session-start-progressive-disclosure for unfamiliar target projects
- context-matrix-map when routing should reference docs/agents/context-matrix.md
- project-context-calibration when routing should reference root CONTEXT.md
- project-standards-calibration when routing should reference docs/agents/project-standards.md
- verification-before-completion before complete/checked/ready adapter claims

Fallback: If companion skills or target-project artifacts are unavailable, create a minimal framework router and state unverified gaps.

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
   - Discover installed skills and the distribution root through the host's skill catalog, configuration, or installation metadata. Use registry names, supported variables, or paths relative to a verified root; do not embed machine-specific absolute paths in reusable instructions.
   - If only a skill root is known, inspect nearby installation directories for a distribution containing `stack/AGENTS.md` and `stack/goated-stack.yaml`. Keep discovery bounded; if it remains unavailable, state the gap and use standalone skill instructions within the authorized scope.
   - In integrated mode, apply one installed shared policy: merge its contents into active instructions or explicitly direct the agent to read it once when GOATED applies. Verify that the framework can perform the selected load; an ordinary link is not an import. If it cannot, merge the necessary policy instead.
   - Use installed `using-goated-ai-skills` when the route is uncertain or needs revision. A clear specialist request may go directly to that skill; unfamiliar context can justify `session-start-progressive-disclosure`.
   - For prompt-crafting requests, name installed `goated-prompt` as the owner of prompt improvement, reusable prompts, spec/task/planning/refinement prompts, and GOATED-aware request translation.
   - Name the relevant installed GOATED skills instead of pasting their full contents.
   - Keep workflow mechanics with shared policy and the router. The adapter needs only task-relevant pointers and project-specific constraints.

6. Route to target-project artifacts:
   - Point to existing root `CONTEXT.md` when project language, boundaries, or durable artifact meanings need clarification.
   - Point to an existing `docs/agents/context-matrix.md` when source discovery needs guidance.
   - Tell future agents to read `docs/agents/project-standards.md` when standards affect the work.
   - Mention only artifacts that exist. Missing optional onboarding artifacts
     do not lower confidence when discovery found no need for them.
   - Tell future agents to use `.local/goated/` for resumable envelopes and
     handoffs only after verifying `.local/` is ignored; otherwise use OS temp.
   - State lower confidence only when missing or stale evidence leaves a material task question unresolved.

7. Verify the adapter:
   - Re-read the edited artifact.
   - Check that it names the selected framework, selected artifact, installed `using-goated-ai-skills` routing, prompt-crafting routing when included, target-project artifact routing, and unresolved assumptions.
   - Check that it does not paste full GOATED skill bodies or treat any one filename as universal.
   - Use `verification-before-completion` before claiming the adapter is complete, checked, or ready for use.

## Output Contract

Update the selected target-project instruction artifact or configuration with a concise routing section. Use this shape when the framework syntax allows plain Markdown:

```markdown
## GOATED Skill Routing

- Framework: <Codex | Claude Code | Hermes | OpenCode | generic agent | other confirmed framework>
- Installed skills: <host discovery source, registry, or path relative to a verified installation root>
- Shared policy: <already applied, or explicitly locate the distribution through host configuration and read its package-relative stack/AGENTS.md once when GOATED applies; state standalone fallback if unavailable>.
- Use installed `using-goated-ai-skills` when route selection or revision is needed; clear specialist requests may go directly to that skill.
- Use installed `goated-prompt` for prompt improvement, reusable prompts, and GOATED-aware request translation.
- Use existing root `CONTEXT.md` when project language or boundaries need clarification.
- Use an existing `docs/agents/context-matrix.md` when source discovery needs guidance.
- Use `docs/agents/project-standards.md` for project standards when present.
- Use `.local/goated/` for resumable local state only after ignore verification; otherwise use OS temp.
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

Main owns framework selection, edit strategy, final patch, and user communication.

Delegate only bounded evidence scans: find framework instruction artifacts, check `docs/agents/`, summarize one candidate instruction file, or identify installed skill registry paths from local config.

Require paths inspected, commands run, framework signals, assumptions/confidence, and recommended artifact candidates rather than direct edits. If subagents are unavailable, run the same scans sequentially with a narrower context budget.

## Guardrails

- Do not assume `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, or any one filename is universal.
- Do not paste the full GOATED onboarding or delivery workflow into every target project.
- Do not copy full `SKILL.md` bodies into target-project instructions.
- Do not edit instructions before detecting or confirming the chosen framework.
- Do not overwrite existing project-specific rules, safety notes, or framework syntax.
- Do not route to target-project artifacts that do not exist without marking them missing or planned.
- Do not imply that optional context, source-map, or standards artifacts are
  missing requirements when the onboarding budget intentionally omitted them.
- Do not include private notes, ignored local scratch files, credentials, client data, or sensitive personal context unless the user explicitly requests a private artifact.
- Prefer a small router that points to installed skills and durable target-project artifacts.

## References

No external references are required. This skill is self-contained after installation.
