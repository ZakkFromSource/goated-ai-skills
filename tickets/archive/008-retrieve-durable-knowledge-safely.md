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

- [x] Retrieval is progressive and read-only.
- [x] Authority, relevance, confidence, maturity, and freshness affect ranking.
- [x] Current authoritative evidence is distinguished from history,
      observation, inference, brainstorming, and stale notes.
- [x] Results add paths, provenance, scope, and uncertainty to shared evidence.
- [x] Conflicts and stale knowledge are reported rather than silently merged.
- [x] Note nurturing is recommended through a separate workflow and never
      performed implicitly.
- [x] Ordinary files work without Obsidian, semantic search, a database, or a
      connector.
- [x] External web research remains outside this skill.

## Expected Proof

- Authoritative-source fixture.
- Stale-note and conflicting-note fixtures.
- Ordinary-files-only fixture.
- Missing-capability fallback fixture.
- No-mutation filesystem check.
- Validator and word-budget output.

## Blocked By

- `tickets/archive/002-route-work-through-adaptive-gates.md`

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

## Implementation Proof

- `skills/productivity/knowledge-retrieval/SKILL.md` and its linked ranking
  reference implement progressive read-only retrieval, claim-scoped ranking,
  six evidence classes, explicit conflict/staleness handling, shared-evidence
  deltas, ordinary-file fallback, and the separate `learning-capture` boundary.
- Six fixtures under `stack/fixtures/knowledge-retrieval/` cover current
  authority, stale notes, conflicting observations, ordinary files, missing
  optional capabilities, and filesystem non-mutation using generic public-safe
  sample files.
- Validator mutation tests reject non-progressive or mutating search, incomplete
  ranking factors or classifications, stale/conflict merging, implicit
  nurturing, missing ordinary-file sources, vague freshness, incomplete
  evidence provenance, missing conflict invalidation, external web fallback,
  and mutation-enabled contracts. A byte-for-byte fixture-tree check confirms
  validation itself performs no writes.
- Live before/after evaluation showed the skill turns a correct but informal
  baseline answer into a scoped retrieval audit with traceable freshness,
  ranked classifications, full shared-evidence entries, invalidation links,
  preserved conflicts, explicit uncertainty, and a firm refusal to silently
  clean up notes.
- `uv run python -m unittest
  tests.test_validate_skills.KnowledgeRetrievalFixtureValidationTests -v`
  passed 14 focused tests. `uv run python -m unittest discover -s tests -v`
  passed all 63 tests.
- `uv run python scripts/validate_skills.py` passed 34 implemented skills, 34
  registry entries, and every fixture family, including six
  knowledge-retrieval scenarios, with zero blocking errors or human-review
  notes. The new skill is 1,169 words, within the focused operational target,
  and the shared policy remains 1,183 words, within its 800-1,200 target.
- `git diff --check` passed. Independent standards and spec review findings
  about provenance dates, traceable freshness, and conflict invalidation were
  fixed; focused re-review found no remaining findings. Security review was not
  applicable because the change adds no executable retrieval engine,
  credentials, auth, persistent write path, dependency, or external action.
