---
name: knowledge-retrieval
description: Use when answering from durable project knowledge, searching scoped notes or project artifacts, reconciling current guidance with older memory, or deciding whether retrieved knowledge is authoritative, stale, conflicting, or uncertain.
metadata:
  goated-category: productivity
---

# Knowledge Retrieval

## Purpose

Retrieve durable project knowledge progressively and read-only.

Answer from existing project files, notes, decisions, standards, or shared
evidence. Rank for the exact claim, distinguish current authority, surface
conflicts and staleness, and add compact provenance-aware evidence entries.

This skill never mutates the knowledge base. Capturing or nurturing a note is a
separate `learning-capture` workflow that requires its own activation and
approval.

## Inputs

- The question or claim, including project, feature, time period, and risk.
- Explicit paths, selected files, existing shared-evidence entries, context
  maps, standards profiles, ADRs, source, tests, or configured knowledge roots.
- Ordinary file listing, reading, and bounded filename or text search.
- Optional capabilities such as a note application, connector, semantic
  search, or database when the user has placed them in scope.
- Source metadata such as authority, status, confidence, maturity, source type,
  dates, supersession, and scope.

## Dependencies

Hard: None.

Soft:
- an integrated shared-evidence bundle when available
- `context-matrix-map` when an existing context matrix can route source reads
- `learning-capture` for a separately requested and approved capture or nurture
  follow-up
- `verification-before-completion` when a downstream claim needs stronger
  freshness or sufficiency proof

Fallback: Search ordinary scoped files by path, filename, headings, metadata,
and bounded text. Missing Obsidian, connectors, semantic search, databases, or
the integrated registry lowers convenience, not correctness. Report capability
limits and uncertainty instead of blocking or substituting external research.

## Workflow

1. Frame the retrieval:
   - Restate the exact question, claim, applicable scope, and required currency.
   - Set action reach to read-only. Treat logical additions to the work
     envelope or shared evidence as session state, not knowledge-base writes.
   - Reuse evidence that covers the claim. Re-read changed, stale, shallow, or
     contradicted sources.

2. Search progressively:
   - **Stage 1:** Read user-provided paths, reused evidence locators, and
     directly named artifacts.
   - **Stage 2:** Follow direct links and inspect nearby authoritative
     standards, decisions, source, tests, schemas, or operator docs.
   - **Stage 3:** Run bounded filename, heading, metadata, and exact-text
     searches inside the selected project area or knowledge root.
   - **Stage 4:** Expand to broader user-approved local roots or optional search
     capabilities only when earlier stages leave a material gap.
   - Stop when evidence is sufficient, expansion is disproportionate, or scope
     is unclear. Record gaps instead of crawling an entire vault.

3. Classify each material result:
   - `authoritative` - current source, executable evidence, standard, policy,
     or governing decision for the claim.
   - `history` - superseded or time-bounded decision and its original context.
   - `observation` - captured behavior or experience that is not a governing
     rule.
   - `inference` - a conclusion derived from evidence but not stated by an
     authoritative source.
   - `brainstorming` - an option, idea, question, or unsettled possibility.
   - `stale` - knowledge overdue for review, changed, superseded, or too old for
     the requested claim.
   - Preserve useful combinations in the explanation, such as "stale
     observation"; do not collapse everything old into history.

4. Rank for the claim:
   - Gate on applicable scope and relevance first; an authoritative but
     irrelevant file does not answer the question.
   - Compare authority, freshness, confidence, and maturity. All five factors
     affect rank but are not interchangeable.
   - For exact or high-risk claims, current authoritative source and executable
     evidence outrank summaries, memories, and notes.
   - Maturity describes development and reuse; confidence describes factual
     support. A polished note does not outrank current governing evidence.
   - Missing metadata is `unknown`, not current. Lower confidence or add
     uncertainty rather than excluding an otherwise relevant ordinary file.
   - Read [Ranking And Conflict Rules](references/ranking-and-conflict-rules.md)
     when factors disagree, sources conflict, or the result will support an
     exact, high-risk, or long-lived claim.

5. Handle conflicts and staleness:
   - Keep each conflicting locator, classification, scope, and finding visible.
   - State which source currently governs the claim and why, or state that the
     conflict remains unresolved.
   - Never merge competing claims into false consensus.
   - Retain stale material as qualified history when useful; do not delete,
     rewrite, re-tag, or refresh it.
   - If a note would benefit from correction, evidence, caveats, or maturation,
     recommend a separate `learning-capture` nurture run. Do not perform it.

6. Add an evidence delta:
   - Add compact references rather than copied source content.
   - For each material result include `identifier`, `relevance`,
     `applicable_scope`, `finding`, `provenance`, `freshness`, `confidence`,
     `uncertainty`, and `validity` when useful.
   - When contradiction invalidates an entry, retain it with `invalidated_by`.
   - Do not claim a source is current or authoritative unless its content,
     metadata, project role, or executable behavior supports that judgment.

7. Return the answer and audit:
   - Lead with the best-supported answer at the supported confidence.
   - List ranked material evidence, classifications, conflicts, stale items,
     capability limits, search boundary, and unresolved uncertainty.
   - Recommend the smallest next retrieval step only when it could materially
     change the answer.

## Output Contract

Return a compact retrieval result:

```markdown
## Retrieval Result

- Answer: <best-supported answer or unresolved>
- Scope searched: <paths, roots, and final progressive stage>
- Confidence: <high | medium | low>

### Ranked Evidence
- `<identifier>` - <classification>; <why it ranks here>; <freshness>

### Conflicts And Staleness
- <conflict, stale source, governing source, and unresolved uncertainty, or None>

### Shared-Evidence Delta
- identifier: <path or stable locator>
  relevance: <why this source bears on the exact claim>
  applicable_scope: <claim scope>
  finding: <compact finding>
  provenance: <source role or origin>
  freshness: <commit, modified date, retrieval date, or equivalent marker>
  confidence: <high | medium | low>
  uncertainty: <remaining uncertainty or none>
  validity: <current | invalidated>
  invalidated_by: <changed source or contradictory evidence when invalidated>

### Limits And Next Step
- <capability limit, skipped expansion, separate learning-capture recommendation, or None>
```

## Delegation

Main owns the question, search boundary, ranking judgment, conflict resolution,
shared-evidence delta, and user communication.

Delegate only bounded read-only searches or source assessments. Require paths,
search terms, findings, classification, authority/freshness evidence,
uncertainty, skipped scope, and no-mutation confirmation. Otherwise perform the
same stages sequentially.

## Guardrails

- Do not create, edit, delete, rename, move, tag, reformat, or silently nurture
  knowledge files.
- Do not create an index, cache, database, embedding store, source ledger, or
  retrieval log.
- Do not crawl an entire vault or project when progressive scoped search is
  sufficient.
- Do not treat recency, keyword similarity, confidence, or note maturity as a
  substitute for authority and applicable scope.
- Do not hide conflicts, discard stale history, or synthesize unsupported
  consensus.
- Do not require Obsidian, semantic search, a database, a connector, or this
  source repo's root files.
- Do not perform external web research. Route a separate research request to an
  appropriate workflow.
- Do not expose secrets or sensitive content in findings; reference the source
  and summarize only what the active data-sensitivity rules permit.

## References

- [Ranking And Conflict Rules](references/ranking-and-conflict-rules.md) - read
  when ranking factors disagree, conflicts appear, or the claim is exact,
  high-risk, or intended for durable reuse.
