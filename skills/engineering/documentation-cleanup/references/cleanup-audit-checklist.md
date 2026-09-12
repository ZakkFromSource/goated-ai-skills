# Cleanup Audit Checklist

Use this checklist after the initial inventory and role classification. Record exact paths and evidence for each finding.

## Structure And Ownership

- Multiple docs claim to be the first read.
- Root README, agent instructions, context map, and progress docs duplicate the same long current-state summary.
- A doc has no clear audience or role.
- An AI-facing doc lives in a human guide, or a human tutorial lives in an agent routing artifact.
- `docs/agents/` is missing when the project already documents GOATED-style durable agent artifacts.
- `docs/agents/` exists but lacks a clear context matrix, standards profile, or routing purpose.
- Temporary issue handoffs contain durable truth that should be promoted to feature, layer, context, ADR, or PRD docs.
- Historical archives are linked as if they are current operating instructions.

## Freshness And Drift Signals

- "Last updated" dates disagree across docs that describe the same status.
- A status table, launch gate, feature map, or code map appears in multiple files.
- A root doc hardcodes live branch, current priority, roadmap status, command availability, or completed feature state.
- Implemented, planned, deferred, deprecated, and experimental states are blurred.
- Evidence lists or command inventories are copied into several docs with slight differences.
- External-doc lookup notes lack date, source, version when known, query/topic, or freshness caveat.
- A doc says generated, archived, or read-only content should be edited manually.

## Size And Readability

- First-read docs are too large for their job.
- Context maps contain architecture essays or exhaustive file inventories.
- Progress docs mix current status, historical log, implementation detail, issue order, and product decisions.
- Standards profiles include long tutorials instead of concise standards, evidence, enforcement levels, and questions.
- README files include agent-only process rules better owned by an agent instruction adapter.
- A small pointer would preserve meaning while reducing duplicated prose.

## Links And Navigation

- Local Markdown links point to missing files, renamed docs, old issue paths, or moved folders.
- Tables list docs that do not exist.
- Directory trees disagree with the actual file tree.
- Instructions point to private, ignored, absolute, or user-machine-specific paths as if they are portable.
- A route says to read a full PRD, archive, or generated output by default when targeted sections would be safer.

## Privacy And Public Boundary

- Public docs include local absolute paths, usernames, temp paths, private project names, client names, private repo URLs, credentials, API keys, tokens, or secret-like placeholders.
- Public docs include raw transcripts, raw model outputs, raw prompts, full trace payloads, customer data, personal notes, or ignored scratch content.
- Examples depend on one user's private folder layout or private workflow.
- Tool-specific behavior is presented as universal instead of an adapter note.

## Action Labels

Use these labels in reports:

- **keep**: role is clear and no action is needed.
- **refresh**: update stale facts in place.
- **merge**: consolidate duplicated content into a chosen owner, then leave pointers elsewhere.
- **split**: separate mixed audiences or mixed lifecycles into clearer docs.
- **move**: relocate a doc to match project conventions while preserving links.
- **archive**: move completed or historical material to the project's archive convention.
- **delete**: remove content only with explicit approval or strong project convention evidence.
- **defer**: needs product, architecture, owner, or broader source review before cleanup.

## Stop Rules

Continue safe source inspection before deciding whether a mutation is blocked.
Pause the affected edit and ask, or report the unresolved issue, when:

- two authoritative docs conflict and the correct owner is not discoverable;
- cleanup would delete, move, or archive files without clear permission;
- an edit would change legal, compliance, privacy, security, or contractual meaning without a clear authoritative source and covering authorization;
- handling exposed private or sensitive content requires an action beyond current authorization; report its location without reproducing the content;
- needed source evidence remains unavailable or contradictory after safe inspection;
- the task has grown from cleanup into new documentation authoring or product-scope decisions.

A document's subject or the need to check code is not itself an approval gate.
Repair authorized mechanical issues when their meaning is clear, preserve
immutable records, and continue independent authorized work. Reuse consent only
while it covers the same scope and action reach.
