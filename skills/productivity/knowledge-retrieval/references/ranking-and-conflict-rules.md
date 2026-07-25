# Ranking And Conflict Rules

Use these rules when a retrieval result cannot be ranked safely from obvious
current authority alone.

## Claim-Scoped Ranking

Ranking is a reasoned comparison, not a universal numeric score.

1. **Applicable scope and relevance**
   - Exclude results that do not apply to the project, component, audience,
     environment, jurisdiction, or time period in the question.
   - Prefer direct support for the exact claim over topical similarity.

2. **Authority**
   - Prefer the source that owns or demonstrates the fact: current source and
     tests for behavior, active standards for requirements, approved decisions
     for settled choices, and current operator docs for supported procedures.
   - Treat summaries and knowledge notes as navigation and context unless the
     project explicitly grants them governing authority.

3. **Freshness and validity**
   - Look for commits, modification dates, effective dates, review dates,
     supersession links, deprecation markers, and changed source behavior.
   - Newer is not automatically better. A recent brainstorm remains weaker
     than an older authoritative decision that is still active.

4. **Confidence**
   - Judge how strongly the source supports its claim. Direct executable or
     first-party evidence can justify higher confidence than memory, hearsay,
     or unverified AI output.
   - Preserve the source's stated confidence when useful, but make an
     independent retrieval judgment.

5. **Maturity**
   - For learning notes, `seedling`, `budding`, `evergreen`, and `mature`
     describe development and reuse.
   - Maturity can break a tie between otherwise similar notes. It cannot turn
     an observation into policy or make stale knowledge current.

Use a stable path order only as a final presentation tie-break when all
substantive factors are equivalent. Do not imply that the tie-break adds
evidentiary strength.

## Classification Tests

Ask:

- Does this source currently govern or directly demonstrate the claim?
  Classify it as `authoritative`.
- Did it govern in an earlier period or explain a superseded decision?
  Classify it as `history`.
- Does it record something seen or experienced without establishing a rule?
  Classify it as `observation`.
- Is the claim derived rather than directly stated? Classify it as `inference`.
- Is it an option, idea, question, or unsettled direction? Classify it as
  `brainstorming`.
- Has its review date passed, authority been superseded, source changed, or
  currency become inadequate? Add or use `stale`.

When more than one label matters, state the combination in prose while keeping
the primary output classification compact.

## Conflict Procedure

For each material conflict:

1. Record both locators, applicable scopes, findings, classifications, and
   freshness.
2. Check whether the sources actually conflict or apply to different scopes or
   periods.
3. Name the governing source only when project authority and current validity
   support that judgment.
4. Explain why the weaker source remains useful as history, observation, or an
   unresolved signal.
5. If authority is unclear, return `unresolved`; do not choose by majority,
   recency alone, note polish, or keyword count.
6. Add uncertainty and invalidation links to shared evidence without deleting
   the older locator.

## Read-Only Boundary

Retrieval may:

- read metadata and content;
- compare paths, timestamps, commits, or checksums;
- add compact evidence references to session or work-envelope state;
- recommend a later capture or nurture workflow.

Retrieval may not:

- edit metadata or content;
- mark a note stale inside the source file;
- create backlinks, indexes, caches, embeddings, databases, or logs;
- merge, archive, delete, rename, or reclassify source files;
- invoke `learning-capture` as an implicit write step.

If the user asks for retrieval and cleanup together, complete and report the
read-only retrieval first. Treat cleanup or nurturing as a separate requested
workflow with its own destination, review, approval, and verification rules.
