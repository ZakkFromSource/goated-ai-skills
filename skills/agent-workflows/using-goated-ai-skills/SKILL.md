---
name: using-goated-ai-skills
category: agent-workflows
classification: portable
status: wip
description: Use when an installed GOATED skill stack needs to choose the right skill path for a user request, especially across source-repo maintenance, onboarding, delivery, installation, tiny tasks, or explicit overrides.
triggers:
  - user asks which GOATED skill or workflow to use
  - user starts work in a project with GOATED skills installed
  - user asks to install, adapt, create, maintain, or use GOATED AI Skills
  - an agent needs to classify a task before loading deeper skills
  - a request might be tiny enough to skip onboarding or planning ceremony
  - user gives explicit instructions that may override default GOATED routing
outputs:
  - task-surface classification
  - instruction-precedence decision
  - selected GOATED skill path or direct-action path
  - tiny-task or explicit-override handling
  - assumptions, missing context, and next action
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure for serious, unfamiliar, cross-file, PRD-level, architectural, repeated, or public-facing work
    - grill-with-docs when intent, scope, success criteria, project language, or public behavior needs docs-grounded clarification
    - framework-agnostic-skill-creator when creating, porting, adapting, sanitizing, or publishing GOATED skills
    - agent-instructions-integrator when a target project needs framework routing to installed skills and durable artifacts
  fallback: If companion skills are unavailable, classify the task directly, obey user and project instructions, keep context loading narrow, and state lower confidence.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Using GOATED AI Skills

## Purpose

Choose the right GOATED skill path without making the user memorize the stack.

Use this router at the start of installed-skill work, when a user asks which skill applies, or when a request could fall into more than one GOATED workflow. The router describes decision behavior only. It does not install hooks, generate adapter manifests, require automatic activation, or override the user's agent framework.

## Inputs

- User request, direct instructions, and any explicit skill names.
- Current working directory and project boundary, when available.
- Target-project instructions, repo instructions, or framework guidance that applies to the workspace.
- Installed GOATED skill list or known skill folder location, when available.
- Existing target-project artifacts, when present, such as root `CONTEXT.md`, `docs/agents/context-matrix.md`, or `docs/agents/project-standards.md`.

## Workflow

1. Apply instruction precedence first:
   - Follow direct user instructions and applicable target-project instructions before GOATED routing advice.
   - If the user explicitly says to use or skip a skill, honor that unless it conflicts with safety, policy, or stronger project instructions.
   - If instructions conflict, surface the conflict and ask only for the decision that cannot be discovered locally.

2. Classify the task surface:
   - **Source repo maintenance**: changing GOATED's public source repo, issue handoffs, docs, skill folders, or maintainer artifacts.
   - **Skill installation/adaptation**: copying, installing, adapting, or routing installed GOATED skills into an agent framework or target project.
   - **Target Project Onboarding**: preparing a target project for durable, repeated, cross-file, PRD-level, architectural, or public-facing work.
   - **Target Project Delivery**: planning, implementing, reviewing, documenting, or handing off one target-project change.
   - **Tiny one-off task**: a small, obvious, low-risk request such as a typo fix, one-line rename, formatting-only edit, or direct command the user already specified.
   - **Explicit override**: the user names a different path or asks to bypass normal routing.

3. Choose the route:
   - For source repo maintenance, follow that repo's maintainer instructions first, then use the relevant GOATED authoring, review, doc-sync, or handoff skill only when it applies.
   - For installation/adaptation, use `session-start-progressive-disclosure` if the environment is unfamiliar, then `agent-instructions-integrator` for project routing or `framework-agnostic-skill-creator` for creating, porting, or adapting skills.
   - For onboarding, start with `session-start-progressive-disclosure`, then use `grill-with-docs` before durable onboarding decisions.
   - For delivery, start with `session-start-progressive-disclosure`; use `grill-with-docs` when the request is PRD-level, architectural, cross-file, repeated, public-facing, unclear, or standards-sensitive.
   - For tiny one-off tasks, proceed directly with the smallest useful context and skip full onboarding, grilling, or planning ceremony.
   - For explicit overrides, follow the override and record any skipped GOATED step and residual risk.

4. Use a compact next-skill map when the first route is clear:
   - Fuzzy feature idea, client brief, or roadmap item -> `write-a-prd`.
   - Approved PRD, product spec, or scoped plan -> `prd-to-issues`.
   - Approved issue, scoped task, or implementation slice ready for executable steps -> `writing-plans`.
   - Implementation, bug fix, public interface change, or regression coverage -> `tdd`.
   - Architecture blueprint needed before implementation -> `plan-codebase-architecture`.
   - Descriptive architecture map, module map, or dependency map -> `architecture-design-map`.
   - Review of a diff, patch, or issue fit -> `standards-and-spec-review`; use `code-security-review` for security-relevant paths.
   - Behavior, interface, standards, or public docs may have drifted -> `doc-sync`.
   - Closeout message, commit text, or continuity note -> `commit-message` or `handoff`.

5. Load only the next useful skill:
   - Prefer the smallest skill or local evidence needed for the next safe action.
   - Do not bulk-load the full GOATED stack just because it is installed.
   - Do not treat this source repo's root files, issues, or local research folders as runtime requirements for installed skills.

6. Watch for routing shortcuts:
   - "This is too small" is valid only when the request is truly low risk and local.
   - "I already know the workflow" does not replace checking the current installed skill when a non-tiny task depends on it.
   - "I need to inspect everything first" is usually a sign to use `session-start-progressive-disclosure`.
   - "The user said implement" does not skip clarification when project instructions, public behavior, architecture, or cross-file scope make intent unclear.

7. Report the route briefly, then continue:
   - Name the selected task surface and next skill or direct action.
   - State any explicit override, tiny-task decision, or lower-confidence fallback.
   - Continue when the next action is safe; ask only when a user decision materially changes the route.

## Output Contract

Return a compact routing note before continuing when the route is not obvious:

```markdown
**GOATED Skill Route**
- Task surface: <source repo maintenance | installation/adaptation | onboarding | delivery | tiny one-off | explicit override>
- Instruction precedence: <user/project instruction applied, or "none beyond normal rules">
- Route: <skill name(s) or direct action>
- Reason: <one sentence>
- Assumptions or skipped steps: <short list or "None">
```

For tiny one-off tasks, a one-sentence note is enough. For explicit overrides, name what was skipped and the risk, if any.

## Delegation

The main agent owns routing, instruction precedence, user communication, and final judgment.

Use subagents only for bounded evidence gathering that helps choose a route, such as:

- checking which agent instructions apply in a target project;
- finding whether GOATED skills are installed and where;
- summarizing a specific docs or standards artifact;
- reviewing whether a request qualifies as tiny or standards-sensitive.

Require subagents to return paths inspected, commands run, assumptions, uncertainty, and a routing recommendation. If subagents are unavailable, perform the same scan sequentially with a smaller context budget.

## Adapter Notes

- **Codex**: use the environment's native skill-loading behavior when available. Use plans or subagents only when the active workflow calls for them.
- **Claude Code**: load the relevant installed skill through the supported skill or command mechanism for that environment.
- **Hermes**: use the configured Hermes skill or workflow registry when present; otherwise follow the copied skill folder directly.
- **OpenCode**: use the project's configured reusable instruction or skill location; keep any single instruction file as a router, not a copy of every skill body.
- **Generic agents**: read the installed skill's `SKILL.md` and any directly linked local support files needed for the active workflow.

These notes are compatibility guidance, not bootstrap automation.

## Guardrails

- Do not override direct user instructions or applicable target-project instructions with GOATED defaults.
- Do not require full onboarding for tiny one-off tasks.
- Do not skip `session-start-progressive-disclosure` and `grill-with-docs` for serious, repeated, cross-file, PRD-level, architectural, unclear, standards-sensitive, or public-facing work.
- Do not implement runtime bootstrap, automatic skill loading, hook installation, adapter manifest generation, installer scripts, or framework detection automation from this router.
- Do not assume one instruction filename, command syntax, tool name, or skill registry is universal.
- Do not make installed skills depend on this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issue files, `.local/` notes, or research folders.
- Do not copy full GOATED workflows into target-project adapters; route to installed skills by name.

## References

No external references are required. This skill is self-contained after installation.
