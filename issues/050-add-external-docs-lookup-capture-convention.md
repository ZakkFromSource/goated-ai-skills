## Parent PRD

No separate parent PRD. This issue is part of the user-approved 2026-05-26 post-V1 improvement issue set. Use this file as the implementation contract.

## Type

AFK

## What to build

Add a safe convention for capturing external documentation lookups, including Context7 MCP lookups when available, during target-project work.

The convention should store concise, dated, attributed lookup notes or source links in target-project docs, not raw vendor documentation dumps. It should help future agents avoid repeated lookups while preserving freshness, attribution, and public-safety boundaries.

## Recommended first reads

- `AGENT.md`
- `CONTEXT.md`
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md`
- `docs/install.md`
- `docs/how-to-use.md`
- `skills/engineering/doc-sync/SKILL.md`
- `skills/agent-workflows/context-matrix-map/SKILL.md`
- `skills/agent-workflows/project-standards-calibration/SKILL.md`
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md`

## Relevant source links

- `skills/engineering/doc-sync/SKILL.md` - likely home for external docs capture guidance or reference.
- `skills/agent-workflows/context-matrix-map/SKILL.md` - future agents may need to discover captured external-doc notes.
- `docs/adr/0001-v1-runtime-bootstrap-and-adapter-automation.md` - boundary against tool-specific automation and runtime behavior.
- `CONTEXT.md` - durable artifact and public/private boundary language.

## Acceptance criteria

- [ ] A portable convention is added for external-doc lookup capture, with Context7 as an example rather than a hard dependency.
- [ ] The convention recommends target-project storage such as `docs/agents/external-docs/<library-or-service>.md` when the target project has no better convention.
- [ ] Captured notes include date, lookup tool/source, library/service name, version when known, source URL or library id, query/topic, concise relevant summary, and freshness caveats.
- [ ] Guardrails prohibit raw large documentation dumps, credentials, private prompts, proprietary code, client data, sensitive context, and copyright-risk copying.
- [ ] The convention tells agents to prefer source links and summaries over bulk pasted docs, and to re-check external docs when freshness matters.
- [ ] `context-matrix-map` recognizes captured external-doc notes as optional project evidence when present.
- [ ] `doc-sync` or a linked reference explains when to create/update these notes after external documentation materially informs implementation, PRDs, architecture, or troubleshooting.
- [ ] No wording implies automatic Context7 usage, MCP installation, background caching, or rate-limit circumvention.

## Expected proof

- Manual review of changed skill/reference files for public safety and self-contained installation.
- Targeted `rg` checks for `Context7`, `external-docs`, `raw`, `credentials`, `cache`, `rate limit`, and stale automation wording.
- Scenario checks: external docs capture creates a concise attributed note; no Context7 installation still has a graceful fallback; freshness-sensitive work re-checks docs instead of trusting stale notes.

## Blocked by

- None - can start immediately.

## User stories addressed

- As an agent user, I can preserve useful external documentation findings without repeatedly spending tool calls on the same lookup.
- As a maintainer, I can keep external docs capture portable, attributed, and safe.

## Implementation route

- Use `grill-with-docs` if storage location or durable-artifact boundaries become unclear.
- Use `writing-plans` before editing `doc-sync`, `context-matrix-map`, or support references.
- Use `doc-sync` and `verification-before-completion` before closeout.

## Scope exclusions

- Do not add a Context7-specific hard dependency.
- Do not implement MCP detection, automated caching, generated indexes, or background refresh.
- Do not store raw vendor documentation or long copyrighted excerpts.

