# External Docs Lookup Notes

Use this convention when external documentation materially informs target-project work and the finding is likely to help future agents. Examples include API behavior, SDK version details, current commonly used syntax or modules, import paths, CLI flags, vendor migration guidance, troubleshooting facts, security notes, or architecture constraints.

These notes are durable project evidence, not documentation mirrors. Prefer concise summaries and source links over copied vendor text.

## Default Location

When the target project has no better convention, write lookup notes under:

```text
docs/agents/external-docs/<library-or-service>.md
```

Use a clear library or service slug, such as `supabase.md`, `stripe.md`, `react-router.md`, or `openai-api.md`.

If the target project already has a documented vendor-docs, ADR, runbook, or context-pack convention, follow that convention and keep the same safety rules.

## When To Capture

Create or update an external-docs note when all of these are true:

- The lookup materially affected implementation, a PRD, architecture planning, troubleshooting, security posture, configuration, or documentation.
- The lookup confirmed up-to-date syntax, modules, imports, package APIs, or commands that may differ from the agent's built-in knowledge and matter to the target project.
- The source is likely to be useful in a future session.
- The result can be summarized without exposing private context or copying large source text.

Skip durable capture when the lookup was incidental, obvious from local docs, private to the current session, or likely to become misleading without a near-term re-check.

## Note Shape

Each captured lookup should include:

- Date: `YYYY-MM-DD`.
- Lookup tool or source: browser, vendor docs, official API reference, Context7 MCP lookup when available, OpenAI Docs MCP lookup when available, DeepWiki, GitMCP, package docs, changelog, issue tracker, or another named source.
- Library or service name.
- Version, product tier, API version, or docs version when known.
- Source URL, package docs URL, changelog URL, or library id.
- Query or topic searched, written generically enough to avoid private prompt leakage.
- Concise relevant summary in the agent's own words.
- Freshness caveat, including when future agents should re-check the source.

Prefer a short entry format like:

```markdown
## 2026-05-27 - <topic>

- Source: <tool/source and URL or library id>
- Library/service: <name>
- Version: <version or "unknown">
- Query/topic: <generic topic>
- Summary: <brief relevant finding>
- Freshness caveat: <when to re-check>
```

## Safety Rules

- Do not paste raw large documentation dumps, long copyrighted excerpts, private prompts, credentials, secrets, proprietary code, client data, sensitive context, real user data, or private workflow assumptions into tracked notes.
- Use lookup notes to reduce unnecessary repeat source, tool, or API requests by preserving concise, attributed, project-relevant findings. You may recreate sections of docs as a paraphrased mirror for information that is relevant to the project.
- Do not imply that Context7, OpenAI Docs MCP, DeepWiki, GitMCP, browsers, MCP servers, or other tools are installed or required. Name tool-specific sources only as possible lookup sources when they were actually used or when giving an example.
- Do not treat lookup notes as automatically refreshed, generated, or authoritative. They are dated notes with attribution.
- Re-check external docs when freshness matters, especially for version-sensitive APIs, security guidance, legal or compliance details, pricing, availability, migrations, deprecations, or operational limits.

## Context Matrix

When `docs/agents/external-docs/` exists, `context-matrix-map` may list relevant notes as optional project evidence. Put them in the lowest useful tier, usually **Only-If-Needed**, unless a specific captured source is central to most serious work in the target project.
