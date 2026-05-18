# Context Docs

Use this reference when a grill depends on project language, glossary/context docs, `CONTEXT.md`, `CONTEXT-MAP.md`, ownership, boundaries, or cross-context meaning.

Context docs are optional project conventions, not universal requirements. Many projects have no dedicated context file. Some have one root `CONTEXT.md`. Larger or multi-context projects may have nested context docs or a root `CONTEXT-MAP.md` that routes agents to domain-specific context files. Always inspect the target project's existing convention before recommending a structure.

## What To Look For

- Root `CONTEXT.md`, nested `CONTEXT.md` files, `CONTEXT-MAP.md`, glossary docs, architecture notes, README language, PRDs, ADRs, issue templates, and agent instructions.
- Terms that shape decisions: domain objects, actors, workflows, states, status labels, identity concepts, ownership boundaries, and overloaded words.
- Relationships that affect implementation: lifecycle order, ownership, identity, cardinality, partial vs whole operations, failure states, and cross-context effects.
- Conflicts between user language, documented language, source behavior, tests, and accepted decisions.

## How To Use Context Evidence In The Grill

- Prefer discovered project language over invented terminology.
- When the user uses a vague or overloaded term, propose a precise term and ask one question to confirm or correct it.
- When source evidence conflicts, surface the contradiction and ask which source should change.
- Use concrete scenarios to test boundaries between concepts:
  - lifecycle: "What happens before, during, and after this state?"
  - ownership: "Which context owns the source of truth?"
  - identity: "Are these two names the same entity or separate identities?"
  - cardinality: "Can one item map to many, or exactly one?"
  - partial vs whole operations: "Can the action apply to part of the object?"
  - failure states: "What is durable after this fails?"
  - cross-context effects: "Which other context observes or reacts to this?"

## Candidate Durable Updates

During the grill, list candidate durable updates instead of writing context docs by default. Possible candidates include:

- project boundaries or non-boundaries;
- canonical terms, aliases to avoid, or resolved ambiguities;
- relationships between domain concepts;
- durable artifact meanings;
- reusable architecture vocabulary;
- gaps where docs, code, tests, and user intent disagree.

Route target-project `CONTEXT.md` creation or curation to `project-context-calibration` when that skill is available. If it is unavailable, continue the grill with lower confidence and report candidate context updates in the working brief. Only write context docs during the grill when the user explicitly asks for that or the target project's established workflow requires immediate capture.

## Optional Structures

For single-context projects, a root `CONTEXT.md` is often enough when the project has durable language future agents must reuse.

For multi-context projects, a root `CONTEXT-MAP.md` may point to context-specific docs and explain how they relate. This is a convention to detect or recommend carefully, not a requirement to impose. If the project already uses another glossary, architecture, or domain-doc convention, prefer that.

