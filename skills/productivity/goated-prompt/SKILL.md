---
name: goated-prompt
category: productivity
classification: portable
status: wip
description: Use when the user wants to transform a rough request into a GOATED-aware prompt, reusable prompt, spec prompt, task prompt, refinement prompt, or prompt-writing guidance.
triggers:
  - user asks to make a prompt GOATED, improve a prompt, optimize a prompt, rewrite a prompt, or create a reusable prompt
  - user provides a rough request and wants a high-quality prompt for an AI coding assistant or reasoning model
  - user wants a request translated into the GOATED AI Skills workflow without bypassing the installed router or companion skills
  - user asks for a spec prompt, task prompt, planning prompt, iterative refinement prompt, or general non-code prompt
  - prompt quality depends on classifying the task, calibrating context, choosing the right prompt structure, or naming assumptions
outputs:
  - detected mode and prompt type
  - recommended GOATED skill route or model class when useful
  - optimized prompt in a clearly labeled code block
  - context plan, assumptions, missing-context question, or privacy warning when needed
  - short rationale naming classification and key prompt-structure decisions
depends_on:
  hard: []
  soft:
    - using-goated-ai-skills when the request should be routed through the installed GOATED stack
    - grill-me when user intent, audience, tradeoffs, or success criteria need lightweight clarification without project docs
    - grill-with-docs when project docs, standards, ADRs, source behavior, tests, schemas, or public-facing engineering facts matter
    - write-a-prd when the optimized prompt should ask for a scoped PRD before implementation
    - writing-plans when an approved issue or scoped task needs exact implementation steps rather than another prompt rewrite
    - framework-agnostic-skill-creator when the user wants the prompt turned into an installable GOATED skill
  fallback: If companion skills or project evidence are unavailable, produce the best prompt from conversation context, state assumptions, and avoid claiming undiscovered project facts.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# GOATED Prompt

## Purpose

Turn rough user requests into precise, useful prompts.

Use this skill in two compatible modes:

- **GOATED Prompt mode** translates a request into a prompt that works with the GOATED AI Skills framework, including likely route, context needs, assumptions, and companion-skill handoff when appropriate.
- **Reusable Prompt mode** creates a portable prompt for an AI coding assistant, reasoning model, or general agent without assuming GOATED is installed.

The skill improves prompt quality; it does not replace project discovery, PRDs, implementation plans, skill creation, or execution. When another GOATED skill should own the next step, the prompt should say so clearly.

## Inputs

- User's raw request, rough prompt, draft instruction, goal, feature idea, bug report, code task, planning question, or existing model output.
- Intended recipient when known: GOATED-enabled agent, coding assistant, reasoning model, general assistant, reviewer, or future agent.
- Target mode if the user states one: GOATED Prompt, Reusable Prompt, or both.
- Relevant context the user provides, such as audience, files, project facts, constraints, success criteria, examples, current output, or desired tone.
- Sensitivity constraints for private paths, credentials, client data, proprietary details, or source excerpts.

## Workflow

1. Choose the mode:
   - Use **GOATED Prompt mode** when the user names GOATED, asks to translate a request into GOATED workflow language, or wants the prompt to route through installed skills.
   - Use **Reusable Prompt mode** when the user wants a high-quality prompt that can travel across models, coding assistants, or agent frameworks.
   - Use both modes when the user asks for both, or when a reusable prompt should also include a GOATED route note.
   - If the user really wants an installable skill, route to `framework-agnostic-skill-creator` instead of disguising skill creation as prompt writing.

2. Classify the prompt type:
   - Read [Prompt Type Router](references/prompt-type-router.md) when the type is unclear or the request mixes several shapes.
   - Use **Spec/build** for new features, apps, modules, systems, or multi-file work.
   - Use **Focused task** for narrow code, docs, config, or review actions on an existing artifact.
   - Use **Planning/design** for architecture, design decisions, tradeoffs, strategy, or conceptual work before implementation.
   - Use **Iterative/refinement** when the user has existing output, code, docs, prompt text, or analysis to improve, debug, or compare.
   - Use **General** for non-code research, explanation, comparison, writing, documentation, analysis, or reasoning tasks.

3. Calibrate context before writing:
   - Identify the minimum context a competent agent would need: goal, current state, target location or artifact, constraints, examples or references, success criteria, and verification expectation.
   - Add missing context only when it is known from the conversation or user-provided material.
   - Ask one focused question only when missing context would materially change the prompt's target, scope, risk, or success criteria.
   - When the missing fact is not critical, write the prompt with an explicit assumption and tell the receiving agent what to verify.
   - Trim context that is redundant, private, stale, tool-specific, or likely to confuse a model with similarly named entities.

4. Select the prompt structure:
   - Read [Prompt Templates](references/prompt-templates.md) for templates and compact examples.
   - Use Location -> Action -> Detail phrasing for focused tasks.
   - Use a spec prompt for complex builds: high-level objective, mid-level objectives, implementation notes, context, and ordered low-level tasks.
   - Use TCREI for refinement: Task, Context, References, Evaluate, Iterate.
   - Use What > How for planning/design prompts: state the outcome, constraints, evaluation criteria, and decision needs before implementation tactics.
   - Use IDK action and detail language when it increases clarity; read [IDK Glossary](references/idk-glossary.md) when selecting precise verbs or coding nouns.

5. Write the optimized prompt:
   - Be directive, concrete, and information dense.
   - Name the target, action, context, constraints, output format, and success criteria.
   - Prefer generic model classes such as fast capable model, reasoning model, code-specialized model, or general model instead of current model-name claims.
   - For GOATED Prompt mode, name the likely route, such as `using-goated-ai-skills`, `grill-with-docs`, `write-a-prd`, `writing-plans`, `tdd`, `doc-sync`, or `framework-agnostic-skill-creator`, without pretending routing is automatic.
   - Put the final prompt in a clearly labeled code block.

6. Review before delivering:
   - Read [Prompt Review Checklist](references/prompt-review-checklist.md) for non-trivial, GOATED-aware, security-sensitive, or reusable prompts.
   - Check context/model/prompt alignment, missing or excessive context, prompt type fit, specificity, output contract, privacy, and assumptions.
   - Remove filler, stale model names, passive hedging, private paths, credentials, raw private source excerpts, and framework-specific syntax presented as universal.
   - If the prompt may fail because source evidence is missing, say what the receiving agent should inspect first.

## Output Contract

Return this shape by default:

````markdown
**Prompt Mode**: <GOATED Prompt | Reusable Prompt | GOATED + Reusable>
**Prompt Type**: <Spec/build | Focused task | Planning/design | Iterative/refinement | General>
**Principles Applied**: <KISS, context/model/prompt alignment, IDK, balance-to-complexity, plan-is-prompt, TCREI, or other relevant principles>
**Recommended Recipient**: <GOATED-enabled agent route or generic model class>

```text
<optimized prompt>
```

**Assumptions**: <explicit assumptions, or "None">
**Why This Structure**: <2-4 concise sentences explaining classification, context choices, and format>
````

When one critical question must be answered first, return:

```markdown
**Prompt Mode**: <mode>
**Blocked Context**: <the missing decision>
**Question**: <one focused question>
**Default If Unanswered**: <reasonable default and risk>
```

## Delegation

The main agent owns mode selection, prompt type classification, final prompt quality, privacy judgment, and user communication.

When subagents are available, use them only for bounded prompt-improvement support, such as:

- checking whether a prompt has enough context for one domain or code area;
- generating alternate prompt structures for the same raw request;
- reviewing the optimized prompt against the checklist;
- identifying privacy risks, stale tool assumptions, or missing success criteria;
- drafting pressure scenarios for reusable prompt evaluation.

Require delegated results to include inspected inputs, prompt type recommendation, assumptions, privacy concerns, missing context, suggested changes, and confidence. If subagents are unavailable, perform the same checks directly with a smaller context budget.

## Guardrails

- Do not ask unnecessary clarifying questions when a strong prompt can be produced with explicit assumptions.
- Do not hide uncertainty; put assumptions or required source checks into the prompt.
- Do not turn every request into a full spec. Match prompt weight to task size and risk.
- Do not turn serious multi-file, architectural, public-facing, or standards-sensitive work into a tiny prompt just because the raw request is short.
- Do not replace `using-goated-ai-skills`, `grill-with-docs`, `write-a-prd`, `writing-plans`, `framework-agnostic-skill-creator`, or implementation workflows. Route to them when they are the better owner.
- Do not recommend specific current model names unless the user provides them or current official docs were checked.
- Do not include private paths, credentials, client data, proprietary excerpts, raw private notes, source clone URLs, ignored scratch content, or sensitive personal context in reusable prompts.
- Do not present one framework's command syntax, file mention syntax, plugin behavior, or automation as universal.
- Do not require this source repo's root files, issue files, `.local/`, or hidden chat history after installation.

## References

- [Prompt Type Router](references/prompt-type-router.md) - read when classifying a raw request or resolving mixed prompt types.
- [IDK Glossary](references/idk-glossary.md) - read when choosing precise action verbs and coding-object nouns.
- [Prompt Templates](references/prompt-templates.md) - read when building the final prompt structure.
- [Prompt Review Checklist](references/prompt-review-checklist.md) - read before delivering non-trivial, GOATED-aware, sensitive, or reusable prompts.
