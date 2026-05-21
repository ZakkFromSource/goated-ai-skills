---
name: framework-agnostic-skill-creator
category: agent-workflows
classification: portable
status: wip
description: Use when creating a new GOATED skill from clarified intent or porting, adapting, sanitizing, or publishing an existing skill, command, prompt, workflow, or agent instruction for portable GOATED use.
triggers:
  - user asks to create, write, design, update, evaluate, or publish a GOATED skill
  - user wants to turn clarified intent, repeated agent behavior, or reusable workflow knowledge into an installable skill folder
  - user asks to port, adapt, generalize, sanitize, or publish an existing skill, command, prompt, workflow, or agent instruction
  - a source workflow is tied to one agent framework, project, issue tracker, folder layout, or private operating convention
  - a candidate skill needs trigger, support-file, dependency, adapter, evaluation, privacy, or portability review before implementation
outputs:
  - selected mode: create from clarified intent or port from source material
  - clarified skill intent, success criteria, audience, category, classification, status, triggers, outputs, dependencies, and adapters
  - source package manifest with files and links inspected or skipped when porting source material
  - proposed neutral GOATED skill shape or patched skill folder
  - support-file plan covering prose, references, scripts, assets, and final review checks
  - skill evaluation plan or results covering RED baseline, pressure scenarios, rationalization capture, and GREEN verification
  - adapter notes, privacy and portability judgment, and remaining blockers
depends_on:
  hard: []
  soft:
    - grill-with-docs before creating or changing public-facing, cross-workflow, unclear, or high-impact skills
    - session-start-progressive-disclosure before working in an unfamiliar target project or source package
    - agent-instructions-integrator when the result needs target-project framework routing
    - handoff when skill creation or porting work is interrupted or should be resumed later
  fallback: If companion skills, source framework docs, or live subagents are unavailable, inspect the available artifacts directly, mark unverified assumptions, and produce a reviewable plan or artifact with explicit residual risk.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Framework-Agnostic Skill Creator

## Purpose

Create self-contained GOATED skill folders that can travel across agent frameworks.

Use this skill in two modes:

- **Create from clarified intent** when the user wants a new or revised GOATED skill based on reusable behavior, preferences, standards, or a repeated workflow.
- **Port from source material** when an existing skill, prompt, command, workflow, or instruction set must be converted into GOATED shape.

Both modes preserve GOATED's lean schema, public boundary, dependency classification, adapter notes, delegation contract, and self-contained installed behavior.

## Inputs

- User request and desired destination: new skill, revised skill, review report, private-only adaptation, or public GOATED contribution.
- Clarified intent, success criteria, audience, workflow scope, non-goals, and examples of user requests that should trigger the skill.
- Source workflow artifacts when porting, such as a `SKILL.md`, command file, prompt, agent instruction section, checklist, script, template, issue, PRD, or handoff.
- Source package links or folders, including adjacent references, scripts, templates, examples, assets, producer artifacts, or consumer artifacts.
- Target GOATED category, classification, status, and installation context, if already decided.
- Public/private boundary requirements, including anything that must be removed, generalized, or kept out of tracked output.
- Relevant framework docs, repository standards, or source licenses when they materially affect portability or reuse.

## Workflow

1. Select the mode and boundary:
   - Use create mode when the main input is clarified intent or reusable behavior rather than an existing source package.
   - Use port mode when the main input is existing source material; if both apply, audit the source first, then design the created GOATED skill.
   - Identify the intended output: implemented skill folder, patch to an existing skill, proposal, adapter note, private fork artifact, or portability review.
   - Keep source repo guidance, installed skill behavior, and target-project artifacts distinct.
   - If the work is unclear, public-facing, or high-impact, use `grill-with-docs` or gather equivalent source-grounded clarification before drafting.

2. Create mode - clarify the skill contract:
   - State the behavior the skill should change, the audience, success criteria, scope, non-goals, and examples of triggering user requests.
   - Choose `agent-workflows`, `engineering`, or `productivity`; recommend `portable`, `domain-specific`, or `private`; and set `stable`, `wip`, or `deprecated`.
   - Write a trigger-focused `description`: say when to load the skill using requests, symptoms, task conditions, or project context. Do not summarize workflow steps in `description`.
   - Add concrete `triggers` and `outputs` that make discovery and completion expectations explicit.
   - Classify dependencies as hard, soft, or graceful fallback. Keep adapter notes small and honest.

3. Create mode - choose the artifact shape:
   - Use prose when judgment, sequencing, or project-sensitive decisions matter.
   - Use `scripts/` when a repeatable operation is safer, clearer, or more deterministic as maintained code than as generated prose.
   - Use `references/` for long examples, pressure scenarios, templates, checklists, stack-specific notes, rationalization tables, anti-pattern catalogs, or adapter playbooks.
   - Use `assets/` for reusable fixtures, templates, images, snippets, or packaged materials that support the skill's output.
   - Keep support files one level below `SKILL.md`, link each directly from `SKILL.md`, and say when to read or run each file.
   - Do not add standalone `README.md`, install guides, changelogs, or decorative support files to a skill folder.

4. Port mode - build the source package manifest:
   - If the source is a folder, repo slice, public package, or entrypoint with adjacent support files, read [Source Package Audit](./references/source-package-audit.md) before judging the port.
   - Recursively inventory the provided source package before summarizing behavior.
   - Read first-party support files that carry workflow behavior, including templates, references, scripts, examples, assets, producer artifacts, and consumer artifacts.
   - Record files and links inspected, skipped files, skip reasons, and residual uncertainty.
   - Do not judge portability, classification, or neutral shape until this manifest exists.

5. Port mode - translate behavior into GOATED shape:
   - Summarize what the full source package makes the agent do, when it triggers, what it asks from the user, what it edits or creates, and how it stops.
   - Separate durable behavior from incidental phrasing, persona, examples, local habits, and framework UI details.
   - Inventory framework mechanics such as slash commands, file mention syntax, MCP tools, apps, plugin APIs, command palettes, or model-specific features.
   - Inventory project mechanics such as instruction filenames, issue trackers, label vocabularies, docs layouts, scratch paths, build commands, or release processes.
   - Classify dependencies, assumptions, adapter requirements, privacy risks, and portability blockers.
   - Preserve source-specific details only when they genuinely fit the destination workflow and remain public-safe.

6. Draft the GOATED skill:
   - Use the lean schema: `name`, `category`, `classification`, `status`, `description`, `triggers`, `outputs`, `depends_on`, and `adapters`.
   - Make the body a framework-neutral operating procedure with `Purpose`, `Inputs`, `Workflow`, `Output Contract`, `Delegation`, `Guardrails`, and `References` when useful.
   - Keep `SKILL.md` under the soft 300-line review threshold whenever possible.
   - Attribute public inspiration when useful, but do not bulk-copy external material or private source text.
   - If the user requested review only, return the proposed shape and blockers without editing files.

7. Evaluate the skill:
   - For a new, substantially changed, or discipline-heavy skill, read [Skill Evaluation](./references/skill-evaluation.md).
   - Design pressure scenarios or representative usage scenarios before trusting the skill.
   - When live subagents are available and safe, run a RED baseline without the skill, capture failures or rationalizations, then run GREEN verification with the skill.
   - When live evaluation is unavailable, write the evaluation plan and residual risk instead of claiming behavioral proof.
   - Add rationalization counters, stop rules, red flags, proof gates, or anti-pattern references when testing or review shows agents can dodge the intended behavior.

8. Validate the artifact:
   - Check the lean schema, category, classification, status, triggers, outputs, dependencies, adapters, and self-contained runtime behavior.
   - Check that every local reference or script linked from `SKILL.md` exists and has a clear read or run condition.
   - Check that no root source-repo files are required after installation.
   - Check that private or sensitive content was removed, generalized, or kept in a private artifact.
   - Check that copied or adapted names, commands, instruction-file precedence, issue tracker conventions, and docs layouts fit the destination workflow and are not presented as universal GOATED requirements by accident.

## Output Contract

When producing a review or proposal, use this shape:

```markdown
# Skill Creator Proposal: <skill-name>

## Mode And Intent

- Mode: <create from clarified intent | port from source material>
- Goal: <one sentence>
- Success criteria: <observable outcomes>
- Scope and non-goals: <brief summary>

## Source Package Manifest

Use for port mode. For create mode, write `Not applicable`.

### Files/Links Inspected

| Source | Type | Why inspected | Behavior evidence found |
| --- | --- | --- | --- |

### Skipped Files / Why

| Source | Why skipped | Residual risk |
| --- | --- | --- |

## Neutral Skill Shape

- Name: <candidate-name>
- Category: <agent-workflows | engineering | productivity>
- Classification: <portable | domain-specific | private>
- Status: <stable | wip | deprecated>
- Trigger-focused description: <candidate description>
- Key workflow steps: <brief list>
- Outputs: <brief list>

## Support Files

- References: <files and read conditions>
- Scripts: <files and run conditions>
- Assets: <files and use conditions>

## Evaluation

- RED baseline or planned scenarios: <summary>
- Rationalizations or expected failure modes: <summary>
- GREEN verification or residual risk: <summary>

## Adapter Notes

| Adapter or mechanic | Neutral handling | Remaining risk |
| --- | --- | --- |

## Privacy And Portability

- Public-safe content: <summary>
- Removed or generalized content: <summary>
- Classification recommendation: <portable | domain-specific | private>

## Remaining Blockers

- <blocker or "None">
```

When editing, create or update the skill folder and then report:

- files changed;
- selected mode and classification recommendation;
- source package manifest summary when porting;
- trigger, output, dependency, support-file, and adapter decisions;
- evaluation plan or checks performed;
- privacy or portability blockers;
- verification checks performed.

## Delegation

The main agent owns the skill goal, public/private decision, classification, final artifact, and user communication.

When subagents are available, use them only for bounded independent passes, such as:

- recursively inventorying one provided source folder, repo slice, or package link;
- extracting source workflow behavior from one named artifact or support-file family;
- drafting pressure scenarios or representative usage scenarios for evaluation;
- forward-testing a skill with minimal context when safe;
- inventorying tool-specific mechanics and dependencies;
- reviewing private or sensitive content risks;
- checking the drafted skill against the lean schema and self-contained runtime rules.

Require every subagent result to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- source paths or links inspected;
- skipped paths or links with reasons;
- behavior, mechanics, assumptions, and risks found;
- evaluation evidence or proposed scenarios when relevant;
- confidence and unresolved questions;
- recommendation, not direct publication.

Handle delegated status this way: `DONE` means integrate the audit, evaluation, privacy check, schema check, or portability recommendation; `DONE_WITH_CONCERNS` means inspect concerns before publishing or editing; `NEEDS_CONTEXT` means provide the missing source artifact, install target, category, classification, adapter constraint, or public/private rule and re-dispatch; `BLOCKED` means narrow the work, split the audit, keep the result private, or escalate to the user before creating tracked output.

If subagents are unavailable, perform the same passes sequentially with a narrower context budget and mark any live-evaluation gaps.

## Guardrails

- Do not publish credentials, secrets, client data, private project names, sensitive personal context, or private workflow assumptions in public main.
- Do not put workflow steps, proof gates, or implementation detail in `description`; keep `description` focused on triggers.
- Do not inspect only the obvious entrypoint when a provided source package includes first-party support files that may define real behavior.
- Do not assume one framework's instruction filename, command syntax, file mention behavior, plugin system, issue tracker, or docs layout is universal.
- Do not claim behavioral proof from skill evaluation unless scenarios actually ran; describe unrun checks as a plan or residual risk.
- Do not bulk-copy external source material; summarize behavior, respect licensing, and attribute public inspiration when relevant.
- Do not expand `SKILL.md` with long examples, templates, or adapter matrices when a directly linked `references/` file would keep the skill lean.
- Do not require this source repo's root `AGENT.md`, `README.md`, `CONTEXT.md`, issues, `.local/`, or handoffs at installed runtime.
- Prefer explicit blockers over quiet assumptions when portability, privacy, or evaluation confidence is uncertain.

## References

- [Source Package Audit](./references/source-package-audit.md) - read in port mode before judging any source folder, repo slice, public package, or entrypoint with adjacent support files.
- [Skill Evaluation](./references/skill-evaluation.md) - read before trusting a new, substantially changed, or discipline-heavy skill.
