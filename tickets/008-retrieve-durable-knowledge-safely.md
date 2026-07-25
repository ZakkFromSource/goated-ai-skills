# Ticket 008: Retrieve Durable Knowledge Safely

## Parent Spec

`docs/specs/2026-07-25-goated-ai-skills-v2.md`

## Type

AFK

## What To Build

Add lean read-only knowledge retrieval that searches progressively, ranks
evidence by authority and freshness, reports conflicts, and feeds the shared
evidence bundle without mutating a knowledge base.

## Recommended First Reads

- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — Shared Evidence and Knowledge
  Retrieval
- `skills/productivity/learning-capture/SKILL.md`
- `skills/productivity/learning-capture/references/`
- `stack/templates/evidence-entry.md`
- `stack/goated-stack.yaml`

## Relevant Source Links

- `docs/agents/`
- `CONTEXT.md`

## Acceptance Criteria

- [ ] Retrieval is progressive and read-only.
- [ ] Authority, relevance, confidence, maturity, and freshness affect ranking.
- [ ] Current authoritative evidence is distinguished from history,
      observation, inference, brainstorming, and stale notes.
- [ ] Results add paths, provenance, scope, and uncertainty to shared evidence.
- [ ] Conflicts and stale knowledge are reported rather than silently merged.
- [ ] Note nurturing is recommended through a separate workflow and never
      performed implicitly.
- [ ] Ordinary files work without Obsidian, semantic search, a database, or a
      connector.
- [ ] External web research remains outside this skill.

## Expected Proof

- Authoritative-source fixture.
- Stale-note and conflicting-note fixtures.
- Ordinary-files-only fixture.
- Missing-capability fallback fixture.
- No-mutation filesystem check.
- Validator and word-budget output.

## Blocked By

- `tickets/002-route-work-through-adaptive-gates.md`

## User Stories Addressed

- Derived: As an agent, I can use durable knowledge without treating stale
  memory or inference as current truth.

## Implementation Route

- Use `framework-agnostic-skill-creator` in create mode.
- Use `writing-plans` for the retrieval procedure, evidence integration,
  learning-capture relationship, and fixtures.

## Scope Exclusions

- Do not build indexing infrastructure, embeddings, vault crawling, sync, or
  write-back automation.
- Do not add external research or source-ledger scope.
