---
name: goated-prompt
description: Use when the user wants to transform a rough request into a GOATED-aware prompt, reusable prompt, spec prompt, task prompt, refinement prompt, or prompt-writing guidance.
metadata:
  goated-category: productivity
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

## Dependencies

Hard: None.

Soft:
- using-goated-ai-skills when the request should route through the installed GOATED stack
- grill-me for lightweight intent, audience, tradeoff, or success-criteria clarification
- grill-with-docs when unresolved project intent or conflicting evidence materially blocks a useful prompt
- write-a-spec when the prompt should ask for a scoped spec before implementation
- writing-plans when an approved issue or task needs exact implementation steps
- framework-agnostic-skill-creator for an installable skill

Fallback: If companion skills or project evidence are unavailable, use conversation context, state assumptions, and avoid undiscovered project-fact claims.

## Workflow

1. Choose the mode:
   - Use **GOATED Prompt mode** when the user names GOATED, asks to translate a request into GOATED workflow language, or wants the prompt to route through installed skills.
   - Use **Reusable Prompt mode** when the user wants a high-quality prompt that can travel across models, coding assistants, or agent frameworks.
   - Use both modes when the user asks for both, or when a reusable prompt should also include a GOATED route note.
   - If the user really wants an installable skill, route to `framework-agnostic-skill-creator` instead of disguising skill creation as prompt writing.

2. Classify the prompt type:
   - Read [Prompt Type Router](references/prompt-type-router.md) when the type is unclear or the request mixes several shapes.
   - Use **Spec/build** when a new deliverable needs a scoped product contract. File count alone does not require a spec prompt.
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
   - Default to the outcome, relevant context, constraints, acceptance criteria, verification, and authorized completion boundary.
   - Read the relevant shape in [Prompt Templates](references/prompt-templates.md) only when a template or example would help.
   - For focused tasks, name the location and observable change. For builds, state the product contract and let the receiving agent choose implementation details.
   - Include ordered tasks only for agreed dependencies, required sequencing, or explicit user requests. Distinguish necessary constraints from optional suggestions.
   - For refinement, state what should improve, what must remain stable, and how to evaluate the result. For planning, state decision criteria and the requested recommendation.
   - Use IDK action and detail language when it increases clarity; read [IDK Glossary](references/idk-glossary.md) when selecting precise verbs or coding nouns.

5. Write the optimized prompt:
   - Be directive, concrete, and information dense.
   - Name the target, action, context, constraints, output format, and success criteria.
   - For implementation prompts, carry through authorization and the expected endpoint, including relevant verification and fixes. Preserve review-only scope and explicit approval checkpoints.
   - Prefer generic model classes such as fast capable model, reasoning model, code-specialized model, or general model instead of current model-name claims.
   - For GOATED Prompt mode, name the likely route, such as `using-goated-ai-skills`, `grill-with-docs`, `write-a-spec`, `writing-plans`, `tdd`, `doc-sync`, or `framework-agnostic-skill-creator`, without pretending routing is automatic.
   - Put the final prompt in a clearly labeled code block.
   - Put the finished prompt before classification, route notes, assumptions,
     or explanation.

6. Review before delivering:
   - Read [Prompt Review Checklist](references/prompt-review-checklist.md) for non-trivial, GOATED-aware, security-sensitive, or reusable prompts.
   - Check context/model/prompt alignment, missing or excessive context, prompt type fit, specificity, output contract, privacy, and assumptions.
   - Remove filler, stale model names, passive hedging, private paths, credentials, raw private source excerpts, and framework-specific syntax presented as universal.
   - If the prompt may fail because source evidence is missing, say what the receiving agent should inspect first.

## Output Contract

Return the finished prompt first by default:

````markdown
```text
<optimized prompt>
```
````

Add assumptions, recipient or route guidance, and explanation after the prompt
only when they materially affect use or the user requests them. Omit empty
fields, including `Assumptions: None`. Explanation is optional, not part of the
default artifact.

When one critical question must be answered first, return:

```markdown
**Prompt Mode**: <mode>
**Blocked Context**: <the missing decision>
**Question**: <one focused question>
**Default If Unanswered**: <reasonable default and risk>
```

## Delegation

Main owns classification, prompt quality, privacy, and communication. Delegate
only bounded context, alternate-structure, checklist, privacy, or
success-criteria review.

## Guardrails

- Do not ask unnecessary clarifying questions when a strong prompt can be produced with explicit assumptions.
- Do not hide uncertainty; put assumptions or required source checks into the prompt.
- Do not turn every request into a full spec. Match prompt weight to task size and risk.
- Preserve essential requirements and constraints regardless of prompt length; multiple files or public visibility alone do not justify a larger workflow.
- Do not replace `using-goated-ai-skills`, `grill-with-docs`, `write-a-spec`, `writing-plans`, `framework-agnostic-skill-creator`, or implementation workflows. Route to them when they are the better owner.
- Do not recommend specific current model names unless the user provides them or current official docs were checked.
- Do not include private paths, credentials, client data, proprietary excerpts, raw private notes, source clone URLs, ignored scratch content, or sensitive personal context in reusable prompts.
- Do not present one framework's command syntax, file mention syntax, plugin behavior, or automation as universal.
- Do not put route metadata or explanation before the finished prompt.
- Do not require this source repo's root files, issue files, `.local/`, or hidden chat history after installation.

## References

Linked support files, read at the workflow gates above: [Prompt Type Router](references/prompt-type-router.md), [IDK Glossary](references/idk-glossary.md), [Prompt Templates](references/prompt-templates.md), and [Prompt Review Checklist](references/prompt-review-checklist.md).
