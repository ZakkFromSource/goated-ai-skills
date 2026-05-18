# ADR Capture

Use this reference when a settled decision may need durable architectural decision record capture.

ADR capture is a recommendation, not automatic output from the grill. The grill should identify candidate ADRs, explain why they qualify, and route follow-up according to the target project's existing convention.

## First Inspect The Project Convention

Before recommending an ADR path or format, inspect the target project for:

- `docs/adr/`, `docs/adrs/`, `adr/`, architecture decision folders, or decision logs;
- existing ADR filenames, numbering, status fields, and templates;
- contributor docs, agent instructions, README guidance, or PRD notes about decision records;
- accepted ADRs that already govern the current decision.

Prefer the target project's existing convention over any default. If conventions conflict, ask which one should win.

## When To Recommend ADR Capture

Recommend ADR capture only when all three tests pass:

- Hard to reverse: changing the decision later would carry meaningful migration, coordination, data, user, or operational cost.
- Surprising without context: a future maintainer could reasonably wonder why this choice exists.
- Tradeoff-driven: there were genuine alternatives, and the chosen path reflects constraints, priorities, or rejected options worth preserving.

Skip ADR capture when the decision is obvious, easy to reverse, local to one small change, already documented well enough, or merely repeats implementation detail.

## Good ADR Candidates

- Architectural shape, module boundaries, ownership boundaries, or cross-context integration patterns.
- Technology choices with meaningful lock-in, such as database, message bus, auth provider, deployment target, or storage model.
- Deliberate deviations from the obvious local pattern.
- Constraints not visible in code, such as compliance, partner contracts, performance requirements, or migration limits.
- Rejected alternatives that future maintainers are likely to reconsider.

## Candidate Durable Updates

During the grill, capture ADR candidates in the working brief with:

- decision title;
- chosen outcome;
- evidence or rationale;
- known alternatives or rejected options;
- existing ADR convention found, or "not found in this pass";
- recommended owner or next step.

If the project has no ADR convention and the user asks to create one, suggest the smallest useful default: a tracked `docs/adr/` folder, sequential filenames such as `0001-short-title.md`, and a short record containing context, decision, and rationale. Add optional status, considered options, or consequences only when they help future readers.

Do not create an ADR during the grill unless the user explicitly asks for it or the target project's established workflow requires immediate capture.

