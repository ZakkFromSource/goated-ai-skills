---
name: learning-capture
description: Use when the user asks to capture what was learned, document reusable discoveries, extract durable lessons from provided material, or nurture existing knowledge notes.
metadata:
  goated-category: productivity
---

# Learning Capture

## Purpose

Capture durable, reusable lessons as atomic Markdown notes.

Use this skill after research, brainstorming, design, iteration, implementation, debugging, review, or reading user-provided material reveals knowledge worth preserving. The output should be useful to both a human learner and future agents.

This skill is writer-focused. It may read existing notes only to deduplicate, update, merge, link, or nurture them. It does not perform broad knowledge-base search, synthesis, or Q&A. A future `knowledge-retrieval` or `second-brain-query` companion skill could own that retrieval surface.

## Inputs

- User request to capture what was learned, document a discovery, extract lessons, or improve existing notes.
- Current-session context, user-provided excerpts, research notes, source observations, experiments, or existing note paths.
- Destination hints such as a knowledge root, topic folder, project convention, or `learning-capture.config.md`.
- Existing topic notes when deduplication, update, or nurture is in scope.
- User privacy, public-boundary, or sensitivity constraints.

## Dependencies

Hard: None.

Soft:
- `grill-me` when the lesson, subject, audience, or capture threshold is unclear
- `grill-with-docs` when project docs, standards, ADRs, code behavior, tests, schemas, or source evidence must shape the lesson
- `doc-sync` when captured lessons reveal documentation drift in a target project
- `verification-before-completion` before claiming notes were written, updated, skipped correctly, or are ready to rely on

Fallback: If companion skills, config files, or existing notes are unavailable, use the provided context, label assumptions, and ask before writing when destination or approval is missing.

## Workflow

1. Choose the mode:
   - Use **capture** for durable lessons from the current session or milestone.
   - Use **extract** for durable lessons from user-provided notes, docs, research, or conversation excerpts.
   - Use **nurture** to improve existing `seedling` or `budding` notes with new evidence, examples, caveats, links, or clearer wording.
   - If the user is asking broad questions of a knowledge base, state that retrieval/Q&A is out of scope for V1 and continue only with capture-relevant work.

2. Resolve the destination:
   - Prefer the current user instruction.
   - Then check for optional local config: `learning-capture.config.md` first, `.learning-capture.yml` second.
   - Keep config discovery shallow: current directory, repo root, known knowledge root, and direct user-provided paths only.
   - If project or local agent docs explicitly mention learning capture, use that convention after config.
   - If no destination is known, ask before writing.
   - A config may define `knowledge_root`, `default_subject`, `default_status`, source-type taxonomy path, and tag taxonomy hints, but config is optional.

3. Identify candidate lessons:
   - Capture only durable, reusable lessons that could change a future decision, implementation, explanation, or research direction.
   - Make each candidate atomic: one specific lesson per note.
   - Phrase every candidate as an evidence-bounded claim, especially for inference, brainstorming, partial investigation, or mixed sources.
   - Do not capture secrets, credentials, private client details, sensitive personal facts, low-value trivia, temporary task state, unsupported hunches, or claims already covered by a trusted existing note.
   - Allow `seedling` candidates only when the claim is clearly tentative, has some evidence trail, and includes caveats.

4. Normalize metadata:
   - Use the path shape `<knowledge-root>/<subject>/<topic>/<lesson-slug>.md`.
   - Use readable kebab-case filenames without date prefixes.
   - Required frontmatter fields are `title`, `tags`, `subject`, `topic`, `status`, `confidence`, `source_type`, `source`, `created`, and `updated`.
   - `status` means note maturity: `seedling`, `budding`, `evergreen`, or `mature`.
   - New approved lessons default to `budding` unless evidence or user direction clearly justifies `seedling` or `evergreen`; reserve `mature` for notes reused or linked across multiple contexts.
   - `confidence` means factual confidence: `low`, `medium`, or `high`.
   - Use tags `learning-capture`, `subject/<subject-slug>`, `topic/<topic-slug>`, and optional `type/<concept|syntax|library|convention|discovery|gotcha|pattern|other-useful-type>`.
   - Use configured `source_type` values when available. Otherwise use a compact controlled set and avoid near-duplicate inventions; read [Source Type Taxonomy](references/source-type-taxonomy.md) when needed.
   - Add optional fields such as `related`, `aliases`, `project`, `framework`, `confidence_reason`, or `review_after` only when they help.
   - Use `review_after` only for time-sensitive lessons, such as APIs, libraries, laws, policies, prices, or current tool behavior.

5. Deduplicate before proposing writes:
   - Check the destination topic folder or provided related notes for overlap.
   - When a candidate overlaps an existing lesson, decide case by case whether to update, merge, append a separate linked note, skip, or block.
   - Do not scan an entire personal vault unless the user explicitly asks and the path is in scope.

6. Present candidate cards before writing:
   - Show compact candidate cards using [Lesson Note Template](references/lesson-note-template.md).
   - Include title, subject, topic, tags, status, confidence, source_type, destination, proposed filename, one-sentence claim, and recommendation.
   - Wait for user approval before creating or updating files.
   - Full note previews are optional when useful or requested.

7. Write or update approved notes:
   - Use one atomic Markdown note per lesson.
   - Use YAML frontmatter compatible with Obsidian, but do not require Obsidian.
   - Use body sections: `Lesson`, `For Humans`, `For Agents`, `Use When`, `Caveats`, and optional `Example`.
   - For nurture mode, preserve useful existing content, improve clarity, add evidence or caveats, and update `status`, `updated`, and related metadata only when justified.

8. Return the final chat audit:
   - List created, updated, nurtured, skipped, and blocked candidates with compact reasons.
   - Omit sensitive details from skipped or blocked items.
   - Do not create a persistent capture log in the knowledge root.

## Output Contract

For candidate review, return compact cards:

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
- Claim: <one evidence-bounded sentence>
- Recommendation: <create | update | nurture | skip | block>
```

After approved writes or updates, return:

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

Use [Lesson Note Template](references/lesson-note-template.md) for note shape, config shape, candidate cards, and final audit examples. Use [Worked Examples](references/examples.md) for representative capture, extract, and nurture scenarios.

## Delegation

Main owns lesson selection, destination safety, candidate approval, final note quality, privacy judgment, and user communication.

Delegate only bounded support: scan a topic folder for duplicates, review candidate atomicity, check source evidence for one lesson, draft a candidate card, review note metadata, or inspect a changed note for schema and public-safety issues.

Require inspected paths or inputs, evidence used, assumptions, privacy concerns, confidence, and a recommendation. If subagents are unavailable, run the same checks sequentially with narrower scope.

## Guardrails

- Do not write or update notes before candidate review and user approval.
- Do not capture unsupported hunches as knowledge.
- Do not capture secrets, credentials, private client details, sensitive personal facts, or raw private source material.
- Do not write personal learning notes into public project files unless the user explicitly approves that destination.
- Do not treat old notes as current truth without checking `updated`, `status`, `confidence`, `source_type`, and freshness caveats.
- Do not let `status` imply factual certainty; use `confidence` for truth confidence.
- Do not create one giant chronological journal or a topic file containing many unrelated lessons.
- Do not create a persistent capture log.
- Do not implement broad knowledge-base retrieval, synthesis, Q&A, vault crawling, sync, databases, Obsidian plugins, or Dataview automation.
- Do not require this source repo's root files, issue files, `.local/`, or hidden chat history after installation.

## Quality Check

Before claiming a learning-capture run is complete, verify:

- Each approved note is atomic, durable, evidence-bounded, non-sensitive, destination-resolved, and schema-complete.
- Candidate review happened before writes.
- Duplicate or overlapping lessons were checked in the scoped destination.
- YAML frontmatter contains the required fields and uses allowed `status` and `confidence` values.
- Human and agent sections both add useful value.
- The final chat audit lists created, updated, nurtured, skipped, and blocked candidates as applicable.

## References

Read these only when their detail is needed:

- [Lesson Note Template](references/lesson-note-template.md) - candidate card, config, note, and final audit templates.
- [Source Type Taxonomy](references/source-type-taxonomy.md) - optional source-type values and extensibility rules.
- [Worked Examples](references/examples.md) - programming and non-programming examples covering capture, extract, and nurture.
