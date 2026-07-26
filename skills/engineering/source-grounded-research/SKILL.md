---
name: source-grounded-research
description: Use when a current external question needs cited public or authorized sources, source authority or freshness matters, or conflicting or missing external evidence must be reconciled.
metadata:
  goated-category: engineering
---

# Source-Grounded Research

## Purpose

Investigate one exact external question against a question-specific source
hierarchy and return cited, freshness-aware findings.

Use this specialist for current public or authorized external evidence. Use
`knowledge-retrieval` instead when the question should be answered from local
project knowledge. Research is read-only by default; durable capture is an
optional, separately authorized output branch.

## Inputs

- Exact question, decision or work the answer will support, applicable scope,
  and required currency.
- User-provided sources, known source owners, existing evidence entries, and
  available public or authorized retrieval capabilities.
- Data sensitivity, source-access constraints, action reach, and exclusions.
- Desired output mode: inline read-only result or optional durable Markdown.
- Target-project research, vendor-doc, or external-doc convention when durable
  capture is requested.

## Dependencies

Hard: None.

Soft:
- existing shared evidence entries when they cover the external claim
- `knowledge-retrieval` for a separate local durable-knowledge question
- `doc-sync` when external findings materially inform project work and the
  established external-doc lookup-note convention should capture them
- `learning-capture` for a separately requested reusable lesson rather than a
  research record
- `verification-before-completion` when the research supports a complex,
  high-risk, audited, or long-lived claim

Fallback: Use user-provided sources and any ordinary authorized retrieval
capability available. Without external access, return the framed question,
sources inspected, missing evidence, and the claim that cannot be established.
Do not substitute model memory or local project notes for current external
evidence.

## Workflow

1. **Frame the research contract.**
   - State the exact question, decision use, applicable scope, and currency
     threshold before broad collection.
   - Set data sensitivity and action reach. Default to read-only inline output.
   - Separate facts needed to answer the question from useful but optional
     context.
   - Stop for direction before credentials, private or restricted sources, a
     materially broader scope, or a durable write not already authorized.
   - Complete this phase when the answerable claims and freshness standard are
     explicit.

2. **Build a question-specific source hierarchy.**
   - Rank source types for this question rather than applying a universal list.
   - Prefer the source that owns or directly demonstrates each fact:
     governing specifications, laws or standards; first-party documentation,
     source, datasets, changelogs, or statements; then strong independent
     analysis and discovery sources.
   - Use secondary sources for synthesis, criticism, or the best available
     evidence when no primary source exists. Label that limitation and reduce
     confidence.
   - Treat relevance and applicable scope as gates. Authority, freshness,
     directness, and confidence then determine weight; recency alone does not.
   - Complete this phase when each material claim has a preferred source type
     and a fallback.

3. **Collect progressively and stop proportionately.**
   - Start with named sources and existing current evidence, then inspect the
     preferred primary sources for unresolved claims.
   - Expand to fallback sources only for a material gap, contradiction, or
     scope check. Do not collect broadly after the decision can be supported.
   - Record publication, update, effective, version, or retrieval dates that
     let another agent judge currency. `current`, `stale`, or `unknown` alone
     is not a freshness marker.
   - Re-check volatile claims such as software versions, security guidance,
     laws, pricing, availability, migrations, deprecations, and operational
     limits against current authoritative sources.
   - Complete this phase when evidence is sufficient for the framed claims or
     the bounded search has exposed a specific unresolved gap.

4. **Build the claim and evidence record.**
   - Keep these result types distinct:
     - **finding**: directly supported by a cited source;
     - **inference**: reasoned from named findings but not stated by a source;
     - **disagreement**: sources make materially incompatible claims;
     - **missing evidence**: the required source or fact was not found;
     - **unresolved uncertainty**: available evidence cannot settle the claim.
   - For each material claim retain source identifier, relevance, applicable
     scope, finding, provenance, traceable freshness, confidence, and
     uncertainty. Retain invalidated or stale evidence with its qualifier.
   - Never merge competing claims into false consensus. Name a governing source
     only when authority, scope, and validity justify it.
   - Complete this phase when every conclusion maps to evidence or is visibly
     labeled as inference or uncertainty.

5. **Synthesize the read-only result.**
   - Answer the exact question first and place citations near the claims they
     support.
   - State the decision implication separately from sourced findings.
   - Surface disagreements, stale evidence, missing primary sources, search
     limits, and unresolved uncertainty where they affect use of the answer.
   - Add a compact evidence delta using the established evidence-entry shape;
     link and summarize instead of copying source content.
   - Inline output is complete. Do not create a file merely because the result
     may be useful later.

6. **Capture durably only when selected.**
   - Enter this branch only when durable Markdown was requested or separately
     approved and the destination and sensitivity are resolved.
   - Reuse the target project's existing research, vendor-doc, ADR, runbook, or
     context convention. For external documentation that materially informed
     project work and has no better owner, use the `doc-sync` external-doc
     lookup-note convention, normally
     `docs/agents/external-docs/<library-or-service>.md`.
   - Store a concise dated and attributed summary, applicable version or scope,
     source links, and a freshness caveat. Do not create a documentation mirror,
     duplicate project truth, or imply automatic refresh.
   - Use `learning-capture` separately when the desired artifact is an atomic
     reusable lesson rather than the research record.

7. **Verify the claim scope.**
   - Check that cited sources support the nearby claims, dates satisfy the
     currency threshold, primary-source gaps are explicit, and inference is
     labeled.
   - Check copyright, source-access, privacy, credential, and durable-output
     boundaries before returning or writing the result.
   - Match confidence and completion language to the evidence actually found.

## Output Contract

Return:

- the framed question, decision use, scope, and currency requirement;
- the best-supported answer with claim-near citations;
- distinct findings, inference, disagreements, missing evidence, and unresolved
  uncertainty when present;
- a compact evidence delta with provenance, freshness, scope, confidence, and
  uncertainty;
- source-access or capability limits that materially constrain the answer.

For durable mode, also return the selected convention and written path. Omit
empty classification sections. Do not require a tracked artifact for a
complete read-only result.

## Delegation

The main agent owns the question, hierarchy, source acceptance, synthesis,
sensitivity, capture decision, and communication. Delegate only bounded,
independent claim or source-family investigations with the exact question,
scope, currency threshold, and return fields.

Require source locators, dates, applicable scope, findings, confidence,
uncertainty, skipped sources, and access limits. Review and reconcile all
returns before use. When delegation is unavailable, inspect the same source
families sequentially and preserve the same evidence standard; background
agents are never required.

## Guardrails

- Prefer links and original summaries. Quote only the minimum needed for an
  exact claim; do not copy documentation, articles, proprietary code, datasets,
  or long excerpts into output or tracked notes.
- Use only public or explicitly authorized sources. Do not bypass
  authentication, paywalls, access controls, robots restrictions, terms, or
  licensing limits.
- Never expose credentials, tokens, personal or client data, private prompts,
  ignored notes, restricted content, or sensitive context in queries, logs,
  evidence, tracked files, or public output.
- Treat credential use or movement into private or restricted sources as a
  sensitivity and action-reach change requiring fresh scope and any applicable
  security review.
- Do not treat accessible content as permission to reproduce it.
- Do not perform local knowledge retrieval or note nurturing as an implicit
  side effect of external research.
- Do not invent citations, dates, versions, authority, consensus, or freshness.
- Do not make a browser, search provider, MCP server, crawler, cache, database,
  refresh daemon, or subagent a runtime dependency.
- Do not require this source repo's root files, tickets, `.local/`, upstream
  sources, or hidden chat history after installation.

## References

Read [Pressure Scenarios](references/pressure-scenarios.md) when evaluating the
skill, when source authority or currency is contested, when durable capture is
requested, or when time pressure encourages weak sourcing.
