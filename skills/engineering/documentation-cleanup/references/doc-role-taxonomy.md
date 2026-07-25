# Doc Role Taxonomy

Use this taxonomy to classify documentation before recommending cleanup. A doc may have more than one role, but cleanup is safer when one role clearly owns each fact.

## Core Roles

| Role | Purpose | Common locations | Cleanup posture |
| --- | --- | --- | --- |
| Human guide | Helps a human understand, install, operate, or contribute to the project. | `README.md`, `docs/README.md`, `docs/install.md`, `docs/how-to-use.md` | Keep readable and task-oriented. Avoid turning it into an agent scratchpad. |
| AI-facing guide | Helps agents or models load the right context, constraints, and workflow quickly. | `docs/agents/*`, `AGENTS.md`, `CLAUDE.md`, framework config | Keep concise, source-linked, and routing-focused. Avoid copying full skill bodies or broad tutorials. |
| Context source | Defines project boundaries, durable vocabulary, artifact meanings, and non-boundaries. | `CONTEXT.md`, `docs/context.md` | Refresh carefully. Conflicts here can affect many future tasks. |
| Standards profile | Separates documented standards, inferred conventions, preferences, unresolved questions, and checks. | `docs/agents/project-standards.md`, `docs/standards.md` | Keep evidence-backed. Do not promote preferences into rules without source support. |
| Routing artifact | Tells future agents or contributors what to read first and how to choose context. | `docs/agents/context-matrix.md`, `docs/context-map.md`, agent adapters | Optimize for progressive disclosure and low duplication. |
| Agent instruction adapter | Framework-specific entrypoint that points to project artifacts and installed skills. | `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Keep thin. Preserve framework syntax and project-specific rules. |
| ADR or decision record | Explains durable decisions, rationale, alternatives, and consequences. | `docs/adr/`, `docs/decisions/` | Usually immutable after acceptance. Prefer superseding records over rewriting history. |
| Spec or legacy PRD | Defines product intent, requirements, scope, user stories, or acceptance criteria. | `docs/specs/`, existing `docs/prds/`, `issues/prd-*.md` | Keep current status separate from aspirational scope when possible. |
| External-doc lookup note | Captures dated, attributed summaries of external docs used during work. | `docs/agents/external-docs/*.md` | Keep concise, sourced, and freshness-aware. Avoid vendor-doc dumps. |
| Status or progress doc | Shows current state, next work, open decisions, launch gates, or issue order. | `progress.md`, `progress_current.md`, `docs/progress.md`, roadmap docs | Keep short and current. Move durable detail to feature, layer, or context docs. |
| Architecture map or plan | Describes current topology or planned module/interface shape. | `docs/architecture.md`, `docs/agents/architecture-map.md`, `docs/architecture/*` | Separate current-state maps from future plans. Mark uncertainty and dates. |
| Feature or layer doc | Owns behavior for one product feature or shared infrastructure layer. | `docs/features/*`, `docs/layers/*`, `docs/api/*` | Keep close to source behavior. Route changed facts through `doc-sync`. |
| Issue workbench | Temporary handoff for active slices, bugs, RFCs, or implementation tasks. | `issues/`, `tickets/`, `work-items/` | Do not treat as canonical after completion. Promote durable facts elsewhere. |
| Archive or history | Preserves old sessions, completed issues, old decisions, or legacy docs. | `archive/`, `issues/archive/`, `progress_archive.*` | Usually read-only. Add pointers rather than rewriting content. |
| Scratch or private note | Session-local, ignored, personal, or sensitive working context. | `.local/`, `.scratch/`, `tmp/`, OS temp handoffs | Exclude from public cleanup unless explicitly requested for a private artifact. |
| Generated doc | Produced by codegen, static-site builds, API extraction, or docs tooling. | `site/`, `dist/`, generated API docs | Do not edit manually unless the project says generated output is committed source. |

## Source-Of-Truth Hints

- A doc that states an authority order should guide conflict resolution unless code or user instruction overrides it.
- Root routing docs often point to deeper canonical docs; they should not duplicate all details.
- Current behavior belongs near code-facing feature/layer docs or a status doc, not in every README and agent file.
- Product vision can be aspirational; mark implemented, planned, and deferred states clearly.
- Historical records are useful because they are historical. Do not "fix" them to match today's behavior unless the project explicitly treats them as living docs.

## Cleanup Decision Questions

- What role does this doc serve for a human or future agent?
- Which doc should own this fact if two docs disagree?
- Is the doc active, historical, generated, private, or unknown?
- Would deleting or moving this doc break a documented route?
- Is the content stale, or is it correctly describing an older decision?
- Can a smaller pointer replace duplicated long-form content?
