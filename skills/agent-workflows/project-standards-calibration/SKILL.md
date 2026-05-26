---
name: project-standards-calibration
category: agent-workflows
classification: portable
status: wip
description: Use when onboarding a project, capturing project standards, or separating documented standards, inferred conventions, and user-confirmed preferences.
triggers:
  - user asks to onboard a project for durable or repeated agent work
  - user asks to capture, calibrate, audit, or document project standards
  - agent needs to create or refresh docs/agents/project-standards.md
  - future delivery work depends on coding, testing, documentation, or review conventions
outputs:
  - tracked target-project docs/agents/project-standards.md by default
  - documented standards with source evidence
  - inferred conventions separated from documented rules
  - user-confirmed preferences and unresolved questions
  - enforcement levels for standards, conventions, and preferences
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure before calibrating a new or unfamiliar target project
    - context-matrix-map when a target project already has or needs docs/agents/context-matrix.md
    - project-context-calibration when root CONTEXT.md exists or project language affects standards
    - verification-before-completion before claiming the standards profile is complete, checked, or ready for future agents
  fallback: If companion skills are unavailable, inspect the minimum relevant project files directly and state lower confidence.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Project Standards Calibration

## Purpose

Create a durable standards profile that helps future agents distinguish hard project rules, observed conventions, user preferences, and open questions.

Use this skill during target-project onboarding, before repeated delivery work, or when agents keep rediscovering the same formatting, testing, review, or documentation norms. The profile should make standards easier to apply without forcing future agents to reread the whole project.

## Inputs

- User request or onboarding goal.
- Target-project root path.
- Existing `docs/agents/context-matrix.md`, if present.
- Existing root `CONTEXT.md`, if present.
- Existing `docs/agents/project-standards.md`, if refreshing.
- Project docs, agent instructions, ADRs, contributor guides, issue or PRD templates, and review guidance.
- Build, lint, format, typecheck, test, CI, dependency, schema, and editor configuration files.
- Representative source files and tests when needed to infer local conventions.

## Workflow

1. Confirm the target-project boundary:
   - Identify the project root from the user request, current directory, or repository metadata.
   - Keep installed-skill guidance separate from target-project standards.
   - If a context matrix exists, use it to choose what to read first instead of rediscovering everything.

2. Inspect documented standards before asking questions:
   - Read only the relevant sections of README files, contributor docs, agent instructions, ADRs, style guides, testing docs, release docs, and review checklists.
   - Inspect command definitions from package manifests, build files, CI configs, task runners, Makefiles, scripts, or equivalent project sources.
   - Inspect formatter, linter, typechecker, editor, compiler, schema, migration, and test configuration files.
   - Record each documented standard with a source path and a short evidence note.

3. Infer conventions from local evidence:
   - Sample representative source files, tests, docs, and recent patterns only as needed.
   - Look for naming, layout, module boundaries, error handling, dependency patterns, test style, fixture style, docs style, logging, configuration, and migration conventions.
   - Treat repeated patterns as inferred conventions, not documented standards, unless a source explicitly says they are required.
   - Capture uncertainty when examples conflict or the sample is thin.

4. Classify enforcement level:
   - **tooling-enforced**: enforced or checked by formatter, linter, typechecker, compiler, schema, tests, CI, hooks, or generated checks.
   - **review-enforced**: documented or strongly expected, but dependent on human or agent review.
   - **preference-only**: user-confirmed or locally preferred behavior with little or no project evidence.
   - Do not mark a rule tooling-enforced unless the tool or command is identified.

5. Ask only about non-discoverable preferences:
   - Ask after the documented standards, tooling, and inferred convention evidence pass, not before.
   - Ask one focused question at a time when a user preference or ambiguous tradeoff materially changes future work.
   - Include the recommended default and the evidence behind it.
   - For code style, first decide whether contributor docs, style guides, stronger project instructions, formatter or linter configuration, or clearly consistent inferred conventions already settle the style. If they do, record that source instead of asking a preference question.
   - When code style remains materially undecided, ask one posture-focused question with `Balanced/intermediate` as the recommended default because it preserves readability while still allowing idiomatic local patterns. Offer these choices:
     - `Beginner-friendly`: clear names, straightforward structure, and helpful comments, useful when newer contributors or future agents need code that explains itself.
     - `Balanced/intermediate`: readable first, idiomatic local patterns, and abstractions when they reduce real repetition or complexity.
     - `Advanced/terse`: denser abstractions allowed when justified, fewer comments, and stronger reliance on local conventions.
     - `No durable preference`: follow documented standards, tooling, and inferred conventions case by case.
   - Store a selected code-style posture under `User-Confirmed Preferences` with `preference-only` enforcement. If the user chooses `No durable preference`, record that opt-out as a `preference-only` preference so future agents do not keep re-asking.
   - If the user skips the code-style question or cannot answer, record an unresolved question instead of assuming a posture.
   - Do not store programming level or stack familiarity as a durable label; use it only as conversational context if it helps the user choose a posture.
   - Do not ask about facts that can be discovered from project files or commands.

6. Write or refresh the standards profile:
   - Use `docs/agents/project-standards.md` unless the user requested another tracked path.
   - Create `docs/agents/` if needed.
   - Preserve useful existing user-confirmed preferences unless contradicted by the user or project evidence.
   - Date the update and list the main evidence paths and commands used.

7. Stop when future agents can apply standards:
   - Do not turn the profile into a full architecture map, context matrix, security review, or onboarding tutorial.
   - Defer missing context-map work to `context-matrix-map`.
   - Defer code-quality findings from a specific diff to `standards-and-spec-review` or `code-security-review`.
   - Use `verification-before-completion` before claiming the standards profile is complete, checked, or ready for future agents.

## Output Contract

Write `docs/agents/project-standards.md` with this shape by default:

```markdown
# Project Standards

## Purpose

One short paragraph explaining how future agents should use this profile.

## Documented Standards

| Standard | Enforcement | Source | Notes |
| --- | --- | --- | --- |

## Inferred Conventions

| Convention | Enforcement | Evidence | Confidence |
| --- | --- | --- | --- |

## User-Confirmed Preferences

| Preference | Enforcement | Confirmed by | Notes |
| --- | --- | --- | --- |

## Unresolved Questions

| Question | Why it matters | Current default | Needed before |
| --- | --- | --- | --- |

## Commands And Checks

| Command | Purpose | Enforcement | Source |
| --- | --- | --- | --- |

## Enforcement Levels

- `tooling-enforced`: checked by named project tooling, CI, tests, schemas, hooks, or generated checks.
- `review-enforced`: documented or strongly expected but requires human or agent review.
- `preference-only`: user-confirmed or locally preferred, with little or no project evidence.

## Last Updated

- Date: <YYYY-MM-DD>
- Updated by: <agent or user label>
- Evidence used: <brief list of paths and commands>
```

After writing the file, report:

- artifact path;
- highest-impact tooling-enforced standards;
- preferences or unresolved questions that still need the user;
- evidence paths and commands used.

When the optional code-style posture is captured, the `User-Confirmed Preferences` row must use `preference-only` enforcement and its notes must say that documented standards, formatters, linters, contributor docs, existing style guides, stronger project instructions, and tooling-enforced checks override the preference.

## Delegation

The main agent owns the target-project boundary, standard classification, user questions, final artifact, and user communication.

When subagents are available, use them only for bounded evidence scans, such as:

- documented standards in docs and instruction files;
- tool-enforced standards in config, build, and CI files;
- inferred conventions in one named source or test area;
- existing `docs/agents/` artifacts.

Require every subagent result to include:

- paths inspected;
- commands run or deliberately not run;
- exact source files used as evidence;
- explicit assumptions and confidence;
- candidate enforcement level for each finding.

If subagents are unavailable, perform the same scans sequentially with a narrower context budget. Do not promote unevidenced summaries into standards.

## Guardrails

- Do not ask the user about discoverable facts.
- Do not ask preference questions before inspecting available project evidence.
- Do not ask a code-style posture question when project docs, tooling, or strong inferred conventions already settle the style; record that evidence instead.
- Do not treat common ecosystem habits as project standards without local evidence.
- Do not merge documented standards, inferred conventions, and user preferences into one undifferentiated list.
- Do not mark a standard tooling-enforced unless a specific tool, command, config, check, or test evidence supports it.
- Do not let a `preference-only` code-style posture override documented standards, formatter or linter behavior, contributor docs, existing style guides, stronger project instructions, or tooling-enforced checks.
- Do not include ignored local scratch files, private notes, credentials, client data, or sensitive personal context unless the user explicitly requests a private artifact.
- Do not turn this profile into a broad architecture essay, exhaustive command catalog, style lecture, or review of a specific diff.
- Prefer "unknown", "not found in this pass", or an unresolved question over guessing.

## References

No external references are required. This skill is self-contained after installation.
