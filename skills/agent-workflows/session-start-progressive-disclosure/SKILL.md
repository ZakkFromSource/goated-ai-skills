---
name: session-start-progressive-disclosure
category: agent-workflows
classification: portable
status: wip
description: Start an agent session by reading the smallest useful context, classifying whether the work is source-repo maintenance, skill installation/adaptation, target-project onboarding, or target-project delivery, and producing a concise orientation before deeper work begins.
triggers:
  - user starts a new session or asks the agent to orient itself
  - user asks for durable, cross-file, PRD-level, architectural, or repeated work
  - user asks to install, adapt, create, or use GOATED AI Skills
  - agent needs to decide what context to load before planning or implementation
outputs:
  - concise session orientation
  - task-surface classification
  - assumptions and missing context
  - relevant artifacts read or deferred
  - next recommended skill or workflow step
depends_on:
  hard: []
  soft:
    - context-matrix-map when a target project already has or needs a durable context map
    - project-standards-calibration when project standards affect the work
  fallback: If companion skills are unavailable, inspect the minimum relevant files directly and state lower confidence.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Session Start Progressive Disclosure

## Purpose

Start work with enough context to be useful and no more. Classify the session, read the nearest reliable sources, name assumptions, and recommend the next workflow step.

Use this skill to prevent broad context loading at the beginning of serious or repeated agent work.

## Inputs

- User request or session goal.
- Current working directory, when available.
- Local agent instruction files, when present.
- Existing target-project artifacts, when present, such as `docs/agents/context-matrix.md` or `docs/agents/project-standards.md`.

## Workflow

1. Classify the task surface:
   - **Source repo maintenance**: changing this public skill-library repo or its issue/docs scaffold.
   - **Skill pack installation/adaptation**: copying, installing, adapting, or routing installed skills into an agent framework.
   - **Target Project Onboarding**: preparing a user's project for serious agent work.
   - **Target Project Delivery**: planning, implementing, reviewing, documenting, or handing off one target-project change.
   - **Unknown**: insufficient evidence; inspect one more local source or ask a focused question.

2. Read the smallest useful context:
   - Start with the user's request and any explicit file, issue, PRD, or skill path.
   - Read local agent instructions only if they apply to the current workspace.
   - For source repo maintenance, read the repo maintainer guidance, public context, and the relevant issue or PRD.
   - For installation/adaptation, read install guidance and the specific skill folders or adapter files involved.
   - For target-project onboarding, look for existing `docs/agents/` artifacts, project instructions, README, package or build metadata, and relevant docs.
   - For target-project delivery, read the originating issue or PRD, relevant standards/context artifacts, and only the code or docs needed to plan the next action.

3. Defer deeper context until it is needed:
   - Do not bulk-read source trees, long docs, references, or generated artifacts just in case.
   - Do not load private or local scratch notes unless the user explicitly points to them or the active workflow requires them.
   - Do not read skill `references/` files until the active skill tells you when they matter.

4. Stop exploring when one of these is true:
   - The next safe action is clear and low risk.
   - The remaining uncertainty is a user preference or product decision.
   - Further reading would be broad context collection instead of targeted discovery.
   - A companion skill should take over, such as `grill-with-docs`, `context-matrix-map`, `project-standards-calibration`, or `prd-to-issues`.

5. Produce the orientation before continuing:
   - State the task surface.
   - Name the sources read.
   - Name assumptions and missing context.
   - Recommend the next skill or direct next action.
   - Keep the orientation brief enough that it helps rather than becoming a handoff.

## Output Contract

Return a compact orientation with this shape:

```markdown
**Session Orientation**
- Task surface: <source repo maintenance | installation/adaptation | onboarding | delivery | unknown>
- Goal: <one sentence>
- Read: <paths or artifacts>
- Deferred: <paths or artifact types intentionally not loaded>
- Assumptions: <short list or "None">
- Missing context: <short list or "None">
- Next step: <recommended skill or direct action>
```

If the user asked for immediate implementation and the next action is safe, continue after the orientation instead of waiting for approval.

## Delegation

The main agent owns classification, user intent, final judgment, and user communication.

Use subagents only for bounded scans that can return evidence without blocking the main next step, such as:

- finding relevant instruction files;
- summarizing a specific docs folder;
- checking whether context artifacts exist;
- comparing two candidate entrypoints.

Require subagents to return file paths, commands run, source docs, explicit assumptions, and uncertainty. If subagents are unavailable, perform the same scan sequentially with a narrower read set.

## Guardrails

- Keep source repo guidance separate from installed skill runtime guidance.
- Do not assume a target project has adopted GOATED artifacts unless they exist or the user says so.
- Do not treat `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, or any one instruction filename as universal across frameworks.
- Do not read ignored local/private folders by default.
- Do not turn the orientation into an architecture review, standards audit, security review, or handoff.
- Be explicit when confidence is lower because expected docs or artifacts are missing.

## References

No external references are required. This skill is self-contained after installation.
