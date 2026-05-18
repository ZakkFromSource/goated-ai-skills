---
name: prototype
category: engineering
classification: portable
status: wip
description: Create target-project-local throwaway artifacts to answer one focused product or technical question before PRD creation or during focused issue exploration.
triggers:
  - user asks to prototype, spike, sanity-check, mock up, try variants, or explore an idea cheaply
  - a PRD, issue, or implementation decision depends on one risky product, UI, data, state, or technical question
  - the user wants something runnable, clickable, or inspectable before committing to production implementation
  - target-project delivery needs evidence from a disposable experiment before write-a-prd, prd-to-issues, or tdd
outputs:
  - explicit prototype question and approach
  - clearly marked prototype artifacts located near the relevant code or route
  - run command, URL, toggle, script path, or inspection path for the prototype
  - verdict, observations, and recommended next action
  - cleanup status showing whether the prototype was deleted, absorbed into real work, or explicitly handed off
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before prototyping in an unfamiliar target project
    - grill-with-docs when the question is unclear, expensive, public-facing, cross-file, or affected by project docs and standards
    - write-a-prd when the prototype verdict should feed a broader product requirements document
    - prd-to-issues when the prototype is exploring one focused implementation issue
    - tdd when validated behavior is absorbed into production code after the prototype
  fallback: If companion skills or project docs are unavailable, inspect the smallest relevant local evidence, state assumptions, and keep the prototype disposable.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Prototype

## Purpose

Build a disposable target-project-local experiment that answers one focused question quickly.

Use this skill before PRD creation, during issue exploration, or before committing to a production design when a short prototype can reveal whether a UI direction, state model, data shape, integration path, or workflow idea is worth pursuing. The prototype is not a first draft of production code; it is a learning instrument that should be deleted, absorbed deliberately, or handed off with an explicit cleanup note.

## Inputs

- User request, PRD draft, issue, product question, design uncertainty, or technical risk.
- Target-project root path.
- One focused prototype question, stated before building.
- Relevant nearby route, component, module, command, schema, API, workflow, or test surface.
- Existing project docs, standards, ADRs, context matrix, or planning artifacts when they affect the question.
- Existing run commands, routing conventions, task runners, fixture patterns, and local development constraints.

## Workflow

1. Confirm the prototype question:
   - State the exact question the prototype must answer before creating artifacts.
   - Keep it to one question, such as "Does this state model handle rescheduling cleanly?" or "Which layout makes the approval flow easiest to scan?"
   - If the question is unclear, inspect the minimum relevant docs or code, then use `grill-with-docs` or ask a focused question before building.
   - Write the question in the conversation and in the prototype artifact, such as a top-of-file comment, local README, route label, or note file.

2. Decide whether a prototype is justified:
   - Use a prototype when the answer is easier to learn by running, clicking, toggling, or inspecting than by discussing.
   - Prefer direct implementation when the change is obvious, low risk, and already specified.
   - Do not use a prototype as a way to postpone required requirements work, tests, or design decisions.

3. Choose the prototype shape:
   - For logic, state, data-shape, or API questions, build the smallest local script, terminal loop, fixture harness, or isolated module needed to drive the state and show results.
   - For UI or workflow questions, prefer mounting variants inside the nearest existing route, page, story, preview, or component surface so surrounding context remains visible.
   - Create a new throwaway route or standalone surface only when there is no natural nearby host.
   - For integration questions, stub external effects unless the question specifically concerns the integration boundary.

4. Locate and mark artifacts:
   - Put prototype files close to the relevant code, route, module, or feature area so context is obvious.
   - Follow the target project's existing routing, task-runner, story, preview, fixture, and naming conventions.
   - Include `prototype`, `spike`, or a similarly explicit marker in filenames, route names, comments, or local notes.
   - Add a visible warning such as `PROTOTYPE - delete or absorb before closeout`.
   - Avoid creating broad top-level prototype folders unless the target project already uses one.

5. Build the smallest runnable experiment:
   - Use existing dependencies, commands, components, fixtures, and styling conventions.
   - Make it runnable or viewable with one command, URL, story, script, or documented entrypoint.
   - Keep state in memory by default.
   - Use fixtures, stubs, local scratch data, or clearly wipeable files for sample data.
   - Surface the relevant state after each action, variant switch, run, or simulated case so the result can be judged.
   - Skip production polish: no broad abstractions, no unrelated cleanup, no hardened error handling, and no tests for the throwaway shell.

6. Evaluate the question:
   - Run, click through, or inspect the prototype enough to answer the stated question.
   - Capture observations, surprising behavior, tradeoffs, and the decision the prototype supports.
   - If the prototype does not answer the question, either adjust it narrowly or stop and report what is still unknown.

7. Clean up or hand off before final closeout:
   - Delete the prototype when it has served its purpose and no user review is pending.
   - Absorb only the validated idea into production code, then treat that production work as normal implementation with appropriate tests, docs, and review.
   - If the user still needs to inspect it, leave an explicit handoff note with the question, entrypoint, verdict status, cleanup owner, and cleanup trigger.
   - Do not close the work as complete while prototype artifacts remain unexplained.

## Output Contract

During or after the prototype, report:

- Question: the focused question stated before building.
- Approach: the shape used, such as local script, terminal harness, UI variants on an existing route, story, fixture, or integration stub.
- Artifacts touched: prototype files, nearby host files, commands, URLs, stories, fixtures, or scratch data.
- Verdict: answer, observations, confidence, and what remains unknown.
- Cleanup status: `deleted`, `absorbed`, or `handed off`, with paths and rationale.
- Next action: direct implementation, PRD update, issue split, TDD work, more discovery, or no further action.

If a handoff is needed because the user must inspect the prototype later, include this minimum note in or near the prototype:

```markdown
# Prototype Handoff: <short topic>

Question: <focused question>
Entrypoint: <command, URL, story, or file>
Approach: <what was built and where>
Verdict status: <answered | partially answered | waiting for user review>
Cleanup trigger: <when to delete or absorb>
Cleanup owner: <agent, user, or future implementer>
```

## Delegation

The main agent owns the prototype question, scope control, final verdict, cleanup decision, and user communication.

When subagents are available, use them only for bounded work that can return evidence, such as:

- finding the nearest route, component, module, story, fixture, or command convention;
- drafting independent UI variants for the same stated question;
- creating a focused logic harness in a clearly owned file set;
- running a verification pass that checks prototype artifacts are marked and disposable;
- summarizing what the prototype demonstrated from files, commands, or screenshots.

Require every subagent result to include:

- paths inspected or changed;
- commands run or deliberately skipped;
- the stated prototype question it served;
- evidence for the verdict;
- cleanup recommendation and remaining artifacts.

If subagents are unavailable, perform the same work sequentially with a narrower context budget.

## Guardrails

- Do not build before the prototype question is stated.
- Do not answer more than one major question with one prototype.
- Do not let prototype code become accidental production behavior.
- Do not add persistence, real mutations, production database writes, network side effects, or durable background jobs unless the question explicitly requires that boundary.
- Do not introduce new frameworks, package managers, services, design systems, or major dependencies just for a prototype.
- Do not polish the prototype beyond what is needed to learn from it.
- Do not add tests for the throwaway shell; add tests only when validated behavior is absorbed into production code.
- Do not leave prototype routes, switches, variants, scripts, fixtures, or scratch data in the project without an explicit handoff and cleanup trigger.
- Do not include private data, credentials, client details, sensitive personal context, or real user data in prototype fixtures.
- Prefer a small honest verdict over a large impressive demo that does not answer the question.

## References

This skill is self-contained after installation.
