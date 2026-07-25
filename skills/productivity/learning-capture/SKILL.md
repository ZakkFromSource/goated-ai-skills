---
name: learning-capture
description: Use when the user asks to capture what was learned, document reusable discoveries, extract durable lessons from provided material, or nurture existing knowledge notes.
metadata:
  goated-category: productivity
---

# Learning Capture

## Purpose

Capture reusable lessons as atomic Markdown notes.

Use this skill after research, brainstorming, design, iteration, implementation, debugging, review, or reading user-provided material reveals knowledge worth preserving. The output should be useful to both a human learner and future agents.

This skill is writer-focused. It may read existing notes only to deduplicate,
update, merge, link, or nurture them. It does not perform broad knowledge-base
search, synthesis, or Q&A. Use the read-only `knowledge-retrieval` companion
for that retrieval surface.

## Inputs

- User request to capture what was learned, document a discovery, extract lessons, or improve existing notes.
- Session evidence, user material, research, experiments, or existing notes.
- Destination hints or local capture config.
- Existing topic notes for deduplication or nurture.
- Privacy and sensitivity constraints.

## Dependencies

Hard: None.

Soft:
- `grill-me` when the lesson, subject, audience, or capture threshold is unclear
- `grill-with-docs` when project evidence must shape the lesson
- `doc-sync` when captured lessons reveal documentation drift in a target project
- `verification-before-completion` before claiming notes were written, updated, skipped correctly, or are ready to rely on
- `knowledge-retrieval` for scoped read-only search before separate capture

Fallback: Use provided context, label assumptions, and ask before writing when
destination or approval is missing.

## Workflow

1. Choose the mode:
   - Use **capture** for durable lessons from the current session or milestone.
   - Use **extract** for durable lessons from user-provided notes, docs, research, or conversation excerpts.
   - Use **nurture** to improve existing `seedling` or `budding` notes with new evidence, examples, caveats, links, or clearer wording.
   - If the user is asking broad questions of a knowledge base, route the
     read-only work to `knowledge-retrieval` and continue here only when
     capture or nurture is separately requested.

2. Resolve the destination:
   - Prefer the current user instruction.
   - Then check for optional local config: `learning-capture.config.md` first, `.learning-capture.yml` second.
   - Keep config discovery shallow: current directory, repo root, known knowledge root, and direct user-provided paths only.
   - If project or local agent docs explicitly mention learning capture, use that convention after config.
   - If no destination is known, ask before writing.
   - Config may define destination and metadata defaults, but is optional.

3. Identify candidate lessons:
   - Capture only durable, reusable lessons that could change a future decision, implementation, explanation, or research direction.
   - Make each candidate atomic: one specific lesson per note.
   - Phrase every candidate as an evidence-bounded claim.
   - Exclude sensitive material, trivia, temporary state, unsupported hunches,
     and claims already covered by a trusted note.
   - Allow `seedling` candidates only when the claim is clearly tentative, has some evidence trail, and includes caveats.

4. Normalize metadata:
   - Use the path shape `<knowledge-root>/<subject>/<topic>/<lesson-slug>.md`.
   - Use readable kebab-case filenames without date prefixes.
   - Required frontmatter fields are `title`, `tags`, `subject`, `topic`, `status`, `confidence`, `source_type`, `source`, `created`, and `updated`.
   - `status` means note maturity: `seedling`, `budding`, `evergreen`, or `mature`.
   - New lessons default to `budding`; use `seedling` for tentative,
     evidence-trailed claims, `evergreen` for well-supported durable claims,
     and `mature` only after reuse across contexts.
   - `confidence` means factual confidence: `low`, `medium`, or `high`.
   - Use `learning-capture`, subject, topic, and useful optional type tags.
   - Use configured `source_type` values or the compact taxonomy in
     [Source Type Taxonomy](references/source-type-taxonomy.md).
   - Add optional metadata only when useful. Use `review_after` for
     time-sensitive claims.

5. Deduplicate before proposing writes:
   - Check the destination topic folder or provided related notes for overlap.
   - For overlap, update, merge, link separately, skip, or block.
   - Do not scan an entire personal vault unless the user explicitly asks and the path is in scope.

6. Present candidate cards and apply the shared approval mode:
   - Show compact candidate cards using [Lesson Note Template](references/lesson-note-template.md).
   - Include title, subject, topic, tags, status, confidence, source_type, destination, proposed filename, one-sentence claim, and recommendation.
   - Candidate review is always required, but a second approval is not. Honor
     the active shared mode and consent already recorded for the destination
     and write reach.
   - Under `confirm-each-write`, request approval for each proposed note write.
   - Under `approve-batch`, request one approval for the reviewed batch.
   - Under `standing-session-consent`, proceed after presenting the cards when
     current consent covers the destination and writes.
   - Under `draft-without-applying`, return cards or full previews without
     writing.
   - With no selected mode, use the shared risk-adaptive default. Request fresh
     approval only when required or when scope, destination, sensitivity, or
     action reach materially changes.
   - Full note previews are optional when useful or requested.

7. Write or update approved notes:
   - Use one atomic Markdown note per lesson.
   - Use portable YAML frontmatter.
   - Use body sections: `Lesson`, `For Humans`, `For Agents`, `Use When`, `Caveats`, and optional `Example`.
   - In nurture mode, preserve useful content and update evidence, caveats, and
     metadata only when justified.

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

After writes, report only non-empty `Created`, `Updated`, `Nurtured`,
`Skipped`, or `Blocked` categories with paths and compact reasons.

Use [Lesson Note Template](references/lesson-note-template.md) for note and
card shape.

## Delegation

Main owns selection, destination, approval interpretation, note quality,
privacy, and communication. Delegate only one duplicate scan, evidence check,
candidate card, or schema/privacy review.

## Guardrails

- Do not write or update notes before candidate review and approval coverage
  under the active shared mode.
- Do not request approval again when active batch or standing consent still
  covers the reviewed destination and write reach.
- Do not reuse consent after a material destination, scope, sensitivity, or
  action-reach change.
- Do not capture unsupported hunches as knowledge.
- Do not capture secrets or sensitive/private source material.
- Do not put personal notes in public project files without explicit approval.
- Do not treat old notes as current truth without checking `updated`, `status`, `confidence`, `source_type`, and freshness caveats.
- Do not let `status` imply factual certainty; use `confidence` for truth confidence.
- Do not create one giant chronological journal or a topic file containing many unrelated lessons.
- Do not create a persistent capture log.
- Do not expand into broad retrieval, vault crawling, sync, databases, or
  knowledge-tool automation.
- Do not require this source repo's root files, issue files, `.local/`, or hidden chat history after installation.

Before a completion claim, verify each written note is atomic,
evidence-bounded, non-sensitive, destination-resolved, deduplicated, and
schema-complete.

## References

Read these only when their detail is needed:

- [Lesson Note Template](references/lesson-note-template.md) - candidate card, config, note, and final audit templates.
- [Source Type Taxonomy](references/source-type-taxonomy.md) - optional source-type values and extensibility rules.
- [Worked Examples](references/examples.md) - programming and non-programming examples covering capture, extract, and nurture.
