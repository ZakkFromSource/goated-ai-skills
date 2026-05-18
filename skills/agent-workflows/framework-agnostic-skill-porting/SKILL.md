---
name: framework-agnostic-skill-porting
category: agent-workflows
classification: portable
status: wip
description: Convert tool-specific or project-specific workflows into the neutral GOATED skill format while separating universal behavior from adapter notes and private assumptions.
triggers:
  - user asks to port, adapt, generalize, sanitize, or publish an existing skill, command, prompt, workflow, or agent instruction
  - a source workflow is tied to one agent framework, project, issue tracker, folder layout, or private operating convention
  - a maintainer wants to convert private or domain-specific workflow knowledge into a public-safe GOATED skill
  - a candidate skill needs portability, dependency, adapter, or privacy review before implementation
outputs:
  - source workflow behavior inventory
  - tool-specific mechanics, assumptions, dependencies, and portability risks
  - proposed neutral GOATED skill shape or patched skill folder
  - adapter notes, classification recommendation, and remaining blockers
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before porting an unfamiliar source workflow
    - agent-instructions-integrator when the result needs target-project framework routing
    - handoff when porting work is interrupted or should be resumed later
  fallback: If companion skills or source framework docs are unavailable, inspect the provided workflow directly and mark unverified adapter assumptions.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Framework-Agnostic Skill Porting

## Purpose

Turn a useful but tool-specific, project-specific, or private workflow into a self-contained GOATED skill that can travel across agent frameworks.

Use this skill to preserve the real behavior of the source workflow while stripping away incidental mechanics, private context, and assumptions that would make the result brittle or unsafe in public main.

## Inputs

- User request and desired destination: new skill, revised skill, review report, or private-only adaptation.
- Source workflow artifacts, such as a `SKILL.md`, command file, prompt, agent instruction section, checklist, script, template, issue, PRD, or handoff.
- Source framework or project assumptions, if known.
- Target GOATED category, classification, status, and installation context, if already decided.
- Public/private boundary requirements, including anything that must be removed, generalized, or kept out of tracked output.
- Relevant framework docs, repository standards, or source licenses when they materially affect portability or reuse.

## Workflow

1. Confirm the porting boundary:
   - Identify whether the source is public, private, project-specific, framework-specific, or a mix.
   - Identify the intended output: a GOATED skill folder, a proposal, an adapter note, a private fork artifact, or a review of portability blockers.
   - Keep source repo guidance, installed skill behavior, and target-project artifacts distinct.
   - If the source contains sensitive or private context, decide what can be generalized before writing tracked files.

2. Inventory the source behavior:
   - Summarize what the workflow makes the agent do, when it triggers, what it asks from the user, what it edits or creates, and how it stops.
   - Separate durable behavior from incidental phrasing, persona, examples, local habits, and framework UI details.
   - Capture required outputs, verification steps, failure modes, and follow-up expectations.
   - Preserve the source's useful sequencing, but do not preserve tool-specific syntax as core behavior unless it is truly required.

3. Inventory mechanics, assumptions, and dependencies:
   - List framework mechanics such as slash commands, file mention syntax, MCP tools, apps, shell tools, plugin APIs, command palettes, or model-specific features.
   - List project mechanics such as instruction filenames, issue trackers, label vocabularies, docs layouts, local scratch paths, build commands, or release processes.
   - List domain assumptions, private names, credentials, client data, sensitive personal context, and examples that cannot appear in public main.
   - Classify dependencies as hard, soft, or graceful fallback.

4. Decide portability and classification:
   - Recommend `portable` when the core workflow can run in common agent frameworks with only small adapter notes.
   - Recommend `domain-specific` when a reusable public pattern still depends on a named public domain, ecosystem, or project convention.
   - Recommend `private` when private context, sensitive data, or non-public assumptions are essential to the workflow.
   - If safe sanitization is not possible, stop with blockers instead of producing a public skill.

5. Design the neutral GOATED shape:
   - Use the lean schema: `name`, `category`, `classification`, `status`, `description`, `triggers`, `outputs`, `depends_on`, and `adapters`.
   - Make the body a framework-neutral operating procedure with `Purpose`, `Inputs`, `Workflow`, `Output Contract`, `Delegation`, `Guardrails`, and `References` when useful.
   - Phrase workflow steps around agent behavior and evidence, not one tool's command syntax.
   - Convert framework-specific or project-specific mechanics into adapter notes, detection rules, or fallback behavior.

6. Split core procedure from references:
   - Keep `SKILL.md` under the soft 300-line review threshold whenever possible.
   - Move detailed examples, long checklists, templates, stack-specific notes, source comparison matrices, or adapter playbooks into directly linked files under `references/`.
   - Tell the agent exactly when to read each reference.
   - Avoid duplicating the same guidance in both `SKILL.md` and references.
   - Use `scripts/` or `assets/` only when a deterministic helper or reusable artifact is genuinely part of the installed skill.

7. Draft or patch the artifact:
   - Create or update the target skill folder using the neutral shape.
   - Include concise adapter notes only where they help the installed skill run in Codex, Claude Code, Hermes, OpenCode, or generic agent environments.
   - Attribute public inspiration when useful, but do not bulk-copy external material or private source text.
   - If the user requested review only, return the proposed shape and blockers without editing files.

8. Validate the port:
   - Check the lean schema, category, classification, status, triggers, outputs, dependencies, adapters, and self-contained runtime behavior.
   - Check that no root source-repo files are required after installation.
   - Check that private or sensitive source content was removed, generalized, or kept in a private artifact.
   - Check that remaining tool-specific mechanics are adapter notes or explicit blockers, not hidden assumptions.

## Output Contract

When producing a review or proposal, use this shape:

```markdown
# Porting Proposal: <skill-name>

## Source Inventory

| Source | Universal behavior | Tool or project mechanics | Assumptions |
| --- | --- | --- | --- |

## Neutral Skill Shape

- Name: <candidate-name>
- Category: <agent-workflows | engineering | productivity>
- Classification: <portable | domain-specific | private>
- Status: <stable | wip | deprecated>
- Purpose: <one sentence>
- Key workflow steps: <brief list>
- Outputs: <brief list>

## Adapter Notes

| Adapter or mechanic | Neutral handling | Remaining risk |
| --- | --- | --- |

## Dependencies And References

- Hard dependencies: <none or list>
- Soft dependencies: <none or list>
- Fallbacks: <none or list>
- References to create or read: <none or list with read conditions>

## Privacy And Portability

- Public-safe content: <summary>
- Removed or generalized content: <summary>
- Classification recommendation: <portable | domain-specific | private>

## Remaining Blockers

- <blocker or "None">
```

When editing, create or update the skill folder and then report:

- files changed;
- classification recommendation;
- source mechanics converted into adapter notes;
- references created or deliberately deferred;
- privacy or portability blockers;
- verification checks performed.

## Delegation

The main agent owns the porting goal, classification decision, final artifact, and user communication.

When subagents are available, use them only for bounded independent passes, such as:

- extracting source workflow behavior from one named artifact;
- inventorying tool-specific mechanics and dependencies;
- reviewing private or sensitive content risks;
- checking the drafted skill against the lean schema and self-contained runtime rules.

Require every subagent result to include:

- source paths or links inspected;
- behavior, mechanics, assumptions, and risks found;
- direct evidence or concise excerpts where safe;
- confidence and unresolved questions;
- recommendation, not direct publication.

If subagents are unavailable, perform the same passes sequentially with a narrower context budget.

## Guardrails

- Do not publish credentials, secrets, client data, private project names, sensitive personal context, or private workflow assumptions in public main.
- Do not assume one framework's instruction filename, command syntax, file mention behavior, plugin system, or issue tracker is universal.
- Do not claim a skill is portable when it still requires one tool's private UI or unavailable API without fallback.
- Do not turn adapter notes into the core workflow unless the target skill is intentionally domain-specific or private.
- Do not bulk-copy external source material; summarize behavior, respect licensing, and attribute public inspiration when relevant.
- Do not expand `SKILL.md` with long examples, templates, or adapter matrices when a directly linked `references/` file would keep the skill lean.
- Do not require this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issues, or handoffs at installed runtime.
- Prefer explicit blockers over quiet assumptions when portability or privacy is uncertain.

## References

This skill is self-contained after installation.

For a public example of a compact workflow that separates a core setup procedure from adjacent seed templates, see [Matt Pocock's setup skill](https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills). Use it as structural inspiration only; this skill does not depend on that repository at runtime.
