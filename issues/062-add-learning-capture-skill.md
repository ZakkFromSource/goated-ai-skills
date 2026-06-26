## Parent PRD

No separate parent PRD. This issue is based on the user-approved 2026-06-26 `grill-me` brief for adding `learning-capture` as a post-V1 productivity skill. The approved scope decisions are embedded here so a future agent can implement from this issue without hidden chat history.

## Type

AFK

## What to build

Implement `learning-capture` under `skills/productivity/`.

The skill should help agents capture durable, reusable lessons discovered during research, brainstorming, design, iteration, implementation, debugging, review, or extraction from user-provided material. It should create or update atomic Markdown lesson notes that are easy for humans to read, useful for future agents, and immediately compatible with Obsidian-style YAML frontmatter when placed in an Obsidian vault.

The skill is writer-focused. It may read existing notes only to deduplicate, update, merge, link, or nurture them. It must not become a broad knowledge-base search, synthesis, or Q&A skill.

The V1 workflow must support three modes:

- `capture` - capture durable lessons from the current session or milestone.
- `extract` - extract durable lessons from user-provided notes, docs, research, or conversation excerpts.
- `nurture` - improve existing `seedling` or `budding` notes when new evidence, examples, caveats, or links make them stronger.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `skills/README.md`
- `skills/productivity/README.md`
- `skills/productivity/grill-me/SKILL.md`
- `skills/productivity/goated-prompt/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md`
- `README.md`
- `docs/how-to-use.md`

## Relevant source links

- `skills/README.md` - lean schema, support-file policy, implementation boundary, validation command, and self-contained installed-skill rules.
- `CONTEXT.md` - source repo, installed skill, target project, public-safe, support-file, and skill anatomy language.
- `skills/productivity/grill-me/SKILL.md` - nearby productivity skill style and one-question-at-a-time clarification pattern that produced this issue.
- `skills/productivity/goated-prompt/SKILL.md` - nearby productivity skill with references-based examples and public-safe workflow boundaries.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` - skill creation, support-file, portability, privacy, and evaluation guidance.
- `skills/agent-workflows/framework-agnostic-skill-creator/references/skill-evaluation.md` - scenario review expectations for a new skill.

## Acceptance criteria

- [ ] `skills/productivity/learning-capture/SKILL.md` exists and follows the lean schema.
- [ ] The skill is portable, public-safe, self-contained after installation, and does not depend on this source repo's root docs at runtime.
- [ ] The discovery description triggers on requests to capture what was learned, document reusable discoveries, extract lessons from material, or nurture existing knowledge notes.
- [ ] The skill supports `capture`, `extract`, and `nurture` modes.
- [ ] The skill treats V1 as session or milestone learning capture, not a full knowledge-management system.
- [ ] The skill captures only durable, reusable lessons that could change a future decision, implementation, explanation, or research direction.
- [ ] The skill defaults to topic-scoped folders with one atomic lesson note per file, not one giant chronological log and not many lessons in one topic file.
- [ ] Lesson paths follow `<knowledge-root>/<subject>/<topic>/<lesson-slug>.md`, using readable kebab-case filenames without date prefixes.
- [ ] Destination resolution is defined in this order: current user instruction, optional local config, project/local agent docs that explicitly mention learning capture, then ask before writing.
- [ ] The primary optional config convention is `learning-capture.config.md` with YAML frontmatter; `.learning-capture.yml` may be supported as an advanced fallback.
- [ ] Config discovery stays shallow and explicit: current directory, repo root, known knowledge root, and direct user-provided paths only.
- [ ] The config convention can define `knowledge_root`, `default_subject`, `default_status`, source-type taxonomy path, and tag taxonomy hints, but config is not required.
- [ ] Candidate review happens before writing notes, unless a future approved change deliberately relaxes that rule.
- [ ] Candidate cards include title, subject, topic, tags, status, confidence, source_type, destination, proposed filename, and a one-sentence lesson claim.
- [ ] The write gate requires each approved lesson to be atomic, evidence-bounded, non-sensitive, deduplicated, destination-resolved, schema-complete, and worth preserving.
- [ ] Overlapping lessons are handled case by case: merge/update existing notes, append a new note and link related notes, or skip when duplication would reduce quality.
- [ ] `seedling` notes are allowed when the claim is clearly tentative, has some evidence trail, and includes caveats; unsupported hunches are blocked.
- [ ] Every lesson note uses YAML frontmatter compatible with Obsidian.
- [ ] Required frontmatter includes `title`, `tags`, `subject`, `topic`, `status`, `confidence`, `source_type`, `source`, `created`, and `updated`.
- [ ] Optional frontmatter can include fields such as `related`, `aliases`, `project`, `framework`, `confidence_reason`, and `review_after`.
- [ ] `review_after` is used only for time-sensitive lessons, such as APIs, libraries, laws, policies, prices, or current tool behavior.
- [ ] `status` represents note maturity, not factual certainty, with values `seedling`, `budding`, `evergreen`, and `mature`.
- [ ] New approved lessons default to `budding` unless evidence or user direction clearly justifies `seedling` or `evergreen`; `mature` is reserved for notes reused or linked across multiple contexts.
- [ ] `confidence` represents factual confidence, with values `low`, `medium`, and `high`.
- [ ] The note body uses a fixed compact structure: `Lesson`, `For Humans`, `For Agents`, `Use When`, `Caveats`, and optional `Example`.
- [ ] Tags use a light taxonomy, including `learning-capture`, `subject/<subject-slug>`, `topic/<topic-slug>`, and optional `type/<concept|syntax|library|convention|discovery|gotcha|pattern|other-useful-type>`.
- [ ] `source_type` is controlled but user-extensible: use a local/vault/project taxonomy when configured, otherwise use a compact default set and avoid near-duplicate inventions.
- [ ] A directly linked reference file exists for the longer optional `source_type` taxonomy inspired by the user's vault list.
- [ ] The skill phrases lessons as evidence-bounded claims, especially when they come from inference, brainstorming, partial investigation, or mixed sources.
- [ ] The skill includes non-capture rules for secrets, credentials, private client details, sensitive personal facts, low-value trivia, temporary task state, unsupported claims, and lessons already covered by a trusted existing note.
- [ ] The final chat summary lists created, updated, nurtured, skipped, and blocked candidates with compact reasons, omitting sensitive details.
- [ ] V1 does not create a persistent capture log in the knowledge root.
- [ ] The skill mentions a future `knowledge-retrieval` or `second-brain-query` companion skill only as a non-goal and possible future complement for broad search and synthesis.
- [ ] The skill includes two worked examples, one programming and one non-programming, and the examples collectively demonstrate `capture`, `extract`, and `nurture`.
- [ ] Long source-type taxonomy, examples, templates, and quality-check details live in directly linked `references/` files rather than bloating `SKILL.md`.
- [ ] The skill includes a short `Quality Check` section for manual verification.
- [ ] `README.md`, `docs/how-to-use.md`, and `skills/productivity/README.md` list the skill only after implementation is complete.

## Expected proof

- Manual schema review of `skills/productivity/learning-capture/SKILL.md`.
- Manual review that every support-file link exists and has a clear read condition.
- Manual review that the installed skill folder is self-contained and does not require this issue, `AGENT.md`, `CONTEXT.md`, or other source-repo root files at runtime.
- Manual public-boundary review confirming that personal Obsidian conventions are generalized into portable public guidance and no private vault paths, private project names, credentials, client data, or sensitive personal notes are included.
- Manual scenario review for:
  - a programming `capture` lesson from a development/debugging session;
  - a non-programming `extract` lesson from user-provided research or notes;
  - a `nurture` pass that improves an existing `seedling` or `budding` note;
  - a duplicate or overlapping lesson that triggers merge/update/link/skip reasoning;
  - a time-sensitive lesson that uses `review_after`;
  - a candidate that is skipped for being transient, sensitive, too broad, unsupported, or already covered.
- Run `uv run python scripts/validate_skills.py`.
- Targeted `rg` checks for `learning-capture`, stale planned wording, public catalog consistency, private path patterns, and persistent-log wording.

## Blocked by

- None - the user approved the scope and asked to create the implementation issue.

## User stories addressed

- Derived: As an agent user, I can ask an agent to capture what was learned from a session or milestone so durable lessons are not lost in chat history.
- Derived: As a human learner, I can read a plain-language explanation of each lesson while future agents get a structured reuse section.
- Derived: As a knowledge worker, I can extract reusable lessons from research notes or provided material without turning every source into a messy summary dump.
- Derived: As a maintainer of a personal or project knowledge base, I can nurture rough notes toward evergreen quality when new evidence arrives.
- Derived: As a GOATED maintainer, I can add learning capture without expanding V1 into broad knowledge-base retrieval or Obsidian-specific automation.

## Implementation route

- Use `framework-agnostic-skill-creator` to create the skill package in GOATED shape.
- Use `doc-sync` after implementation because public catalogs and operator guidance change.
- Use `verification-before-completion` before claiming the skill, references, examples, and docs are implemented.

## Scope exclusions

- Do not implement broad knowledge-base search, retrieval, synthesis, or Q&A in V1.
- Do not implement the future `knowledge-retrieval` or `second-brain-query` companion skill.
- Do not add a persistent capture log under the knowledge root.
- Do not add scripts, databases, sync services, background automation, Obsidian plugins, Dataview queries, vault crawlers, remote issue tracker integration, or installer automation.
- Do not make Obsidian usage mandatory; only make the Markdown and YAML output compatible with Obsidian.
- Do not store private personal vault paths, private project names, credentials, client details, sensitive personal notes, or private workflow assumptions in public main.
- Do not require one fixed knowledge root. Respect user instructions, optional config, project docs, and ask before writing when destination is unclear.

## Implementation notes

- Candidate review format should stay compact. Full note previews can be offered only when useful or requested.
- Suggested candidate card shape:

```markdown
### Candidate: <title>

- Subject: `<subject>`
- Topic: `<topic>`
- Tags: `<tags>`
- Status: `<seedling|budding|evergreen|mature>`
- Confidence: `<low|medium|high>`
- Source type: `<source_type>`
- Destination: `<knowledge-root>/<subject>/<topic>/`
- Proposed filename: `<lesson-slug>.md`
- Claim: <one sentence>
- Recommendation: <create | update | nurture | skip | block>
```

- Suggested note shape:

```markdown
---
title: <title>
tags:
  - learning-capture
  - subject/<subject-slug>
  - topic/<topic-slug>
  - type/<type-slug>
subject: <subject-slug>
topic: <topic-slug>
status: budding
confidence: medium
source_type: <source_type>
source: <brief evidence pointer>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# <Title>

## Lesson

<One atomic evidence-bounded lesson.>

## For Humans

<Plain explanation for the human learner.>

## For Agents

<How future agents should apply or not over-apply the lesson.>

## Use When

<Situations where this lesson is relevant.>

## Caveats

<Limits, uncertainty, freshness concerns, or when to verify first.>

## Example

<Optional concrete example.>
```

- Suggested final chat audit shape:

```markdown
Created
- `<path>` - status: `<status>`

Updated
- `<path>` - <compact reason>

Nurtured
- `<path>` - <status change or improvement>

Skipped
- "<candidate title>" - <compact reason with sensitive details omitted>

Blocked
- "<candidate title>" - <what is needed before writing>
```

- The optional source-type reference should include the longer taxonomy as inspiration, but the skill should instruct agents to prefer configured local values when available and avoid inventing near-duplicates.
