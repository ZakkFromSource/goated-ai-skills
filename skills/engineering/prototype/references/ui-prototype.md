# UI Prototype

Use this reference after choosing the UI/look/layout branch.

This branch answers questions about visual structure, density, hierarchy, affordance, flow, or interaction feel. If the real question is whether a rule, state transition, data shape, or API model works, use [Logic Prototype](logic-prototype.md) instead.

## Default Shape

For web apps, an existing route with a shareable switch often preserves useful
context. Use it when that context matters and the experiment can be gated out
of production; use an isolated preview when the host adds irrelevant work or risk.

Real navigation, data density, auth state, page chrome, loading behavior, and
neighboring actions can change the verdict. If an isolated preview omits relevant
context, reproduce it where practical or state that limitation in the evidence.

For non-web apps, use the equivalent existing host and repeatable control: a screen variant, story, preview, debug menu, deep link, build flag, fixture, or design-system showcase. Preserve the same principles: real surrounding context, easy switching, and a gate that keeps prototype controls out of production behavior.

## Process

1. State the branch and question:
   - Record that this is the UI/look/layout branch.
   - Write the focused question and any branch assumption in the prototype comment, note, route label, story description, or preview description.
   - Name the existing route, screen, component, story, or flow that hosts the variants.

2. Prefer the existing host:
   - Keep existing data loading, route parameters, permissions, auth assumptions, shell layout, navigation, and parent context in place.
   - Swap only the rendered subtree needed to compare the variants.
   - If the prototype is for a new section that naturally belongs inside an existing surface, mount it inside that surface.
   - Use an isolated route, screen, story, or preview when no suitable host exists or isolation reduces unrelated work or risk; retain the context needed for the decision.

3. Generate meaningful variants:
   - Build only the alternatives needed to distinguish the live choices. A single candidate against the existing baseline may suffice; do not invent extra variants to meet a fixed count.
   - Make variants structurally different: layout, information hierarchy, primary action, navigation model, density, or interaction pattern.
   - Avoid variants that only change color, spacing, icon choice, or copy.
   - Use the target project's existing component, typography, styling, asset, and data conventions.
   - Avoid over-sharing layout code between variants; each variant needs enough freedom to test a real direction.

4. Add a shareable switching control:
   - For web routes, prefer a reload-stable URL switch such as a query parameter when the framework supports it.
   - For non-web surfaces, use the platform's equivalent shareable or repeatable control, such as a story control, deep link, debug menu state, preview selector, fixture name, or documented toggle.
   - Make the current variant obvious and quick to cycle.
   - Keep the switcher visually separate from the design being evaluated.
   - Do not intercept normal text input, editor, or accessibility interactions when adding keyboard shortcuts or gestures.

5. Gate prototype mechanics:
   - Hide or disable switchers, debug controls, variant selectors, throwaway routes, and prototype-only fixtures in production builds or production runtime paths.
   - Use the target project's existing environment, build, feature-flag, debug, preview, or story mechanism.
   - If no production gate exists, make the prototype location and handoff explicitly state that it must not ship.

6. Keep mutations safe:
   - Prefer read-only prototypes.
   - If an interaction needs to appear mutating, use in-memory state, fixtures, stubs, or local scratch data.
   - Do not point UI prototypes at real destructive actions unless the stated question is specifically about that boundary and the environment is safe.

7. Capture the verdict:
   - Record which variant, combination, or design decision won and why.
   - Note what remains unknown, especially if the prototype lacked real data, real permissions, mobile constraints, accessibility checks, or production performance.
   - If the user must inspect the variants later, leave a handoff with branch, question, entrypoint, variant keys, verdict status, cleanup trigger, and cleanup owner.

8. Clean up or absorb:
   - Delete losing variants, switchers, debug controls, throwaway hosts, and prototype-only fixtures.
   - Fold the chosen direction into the real route, screen, component, or story deliberately.
   - Treat absorbed production UI as normal implementation work with appropriate tests, docs, accessibility checks, and project review.

## Guardrails

- Do not use UI variants to answer logic/state/data/API questions.
- Do not make variants that differ only cosmetically.
- Do not let prototype switching controls, variant branches, debug toggles, or throwaway hosts ship as production behavior.
- Do not mandate any specific web framework, routing library, styling system, browser-only mechanic, or package manager.
- Do not skip production tests or accessibility expectations when a validated UI direction is absorbed into real code.
