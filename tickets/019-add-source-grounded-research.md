# Ticket 019: Add Source Grounded Research

## Parent Spec

`docs/specs/2026-07-26-selective-upstream-skill-adoption.md`

## Type

AFK

## What To Build

Add `source-grounded-research` as a portable specialist for external
investigation against a question-specific source hierarchy.

Deliver the self-contained skill, evidence and output guidance, pressure
scenarios, registry and routing metadata, fixtures, validation coverage, and
public documentation while preserving the boundaries with local
`knowledge-retrieval`, optional `learning-capture`, and external-doc
`doc-sync`.

## Recommended First Reads

- `docs/specs/2026-07-26-selective-upstream-skill-adoption.md` — R5 and AC5.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` — creation
  and evaluation workflow.
- `skills/productivity/knowledge-retrieval/SKILL.md` — read-only local
  retrieval boundary.
- `skills/engineering/doc-sync/SKILL.md` and
  `skills/engineering/doc-sync/references/external-docs-lookup-notes.md` —
  optional durable capture boundary.
- `stack/templates/evidence-entry.md` — shared provenance and freshness shape.

## Relevant Source Links

- `skills/productivity/learning-capture/SKILL.md`
- `stack/AGENTS.md`
- `stack/goated-stack.yaml`
- `skills/engineering/README.md`
- `README.md`
- `docs/how-to-use.md`
- `https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md`

## Acceptance Criteria

- [ ] The skill frames the exact question, decision use, and currency
      requirement before broad collection.
- [ ] It defines a question-specific source hierarchy and prefers primary
      sources where available.
- [ ] Claims retain source, date or freshness, applicable scope, and
      confidence.
- [ ] Findings, inference, disagreement, missing evidence, and unresolved
      uncertainty remain distinct.
- [ ] Read-only inline output is valid and durable Markdown is optional.
- [ ] Durable capture reuses the existing external-doc convention or a
      project-owned research convention rather than creating duplicate truth.
- [ ] Delegation is optional and the workflow remains single-agent-compatible.
- [ ] Copyright, private-data, credential, and restricted-source boundaries are
      explicit.
- [ ] Fixtures cover stale sources, conflicting sources, no primary source,
      read-only output, durable capture, and no-delegation fallback.

## Expected Proof

- RED/GREEN or forward evaluation using a real public research question without
  leaking the desired answer.
- Focused fixture, registry, link, and public-boundary tests.
- Manual source-authority and copyright-boundary review.
- Fresh repository acceptance commands required by the parent spec.

## Blocked By

- `tickets/015-sharpen-skill-authoring-discipline.md`

Ticket 013 is not a functional dependency. Sequence overlapping validator
edits if its refactor is in progress.

## User Stories Addressed

- As an agent user, I can obtain current, cited external research without
  confusing it with local project memory.
- As a future workflow, I can reuse compact evidence without forcing a tracked
  research artifact.

## Implementation Route

- Use `framework-agnostic-skill-creator`, `writing-plans`, and scenario-first
  proof.
- Use `code-security-review` if restricted sources, credentials, private data,
  or unsafe retrieval mechanisms enter scope.
- Use `standards-and-spec-review`, `doc-sync`, and
  `verification-before-completion` before closeout.

## Scope Exclusions

- Do not require background agents.
- Do not add a browsing tool, MCP dependency, cache, crawler, or refresh daemon.
- Do not copy raw external documentation or long copyrighted excerpts.
- Do not mutate local knowledge notes as part of read-only research.
