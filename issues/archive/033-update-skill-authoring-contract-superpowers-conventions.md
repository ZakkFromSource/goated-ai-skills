## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Update the GOATED skill authoring contract so future skills consistently absorb the highest-value Superpowers conventions while preserving GOATED's lean schema and public-safe installability.

## Acceptance criteria

- [x] The relevant source-repo authoring docs describe trigger-only descriptions: `description` says when to use a skill, while workflow details stay in the body.
- [x] The authoring contract keeps GOATED's richer schema fields: `depends_on`, `outputs`, `adapters`, `classification`, and `status`.
- [x] The docs explicitly allow and encourage `references/`, `scripts/`, and `assets/` when they keep `SKILL.md` lean and make the installed skill more capable.
- [x] Discipline-heavy skills are expected to use rationalization tables, stop rules, proof gates, or anti-pattern references when useful.
- [x] Delegated workflows may use status enums such as `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED`.
- [x] Prompt templates for implementers and reviewers are expected to live in `references/` when they are longer than a compact workflow section.
- [x] The update remains source-repo guidance only and does not create a new installable skill.
- [x] Public docs contain no private names, handles, credentials, client context, or source-repo/runtime confusion.

## Blocked by

- `issues/archive/002-define-skill-authoring-contract.md`

## User stories addressed

- As a maintainer, I can keep future GOATED skills behavior-focused without bloating `SKILL.md`.
- As a future agent, I can see exactly which Superpowers conventions are approved for GOATED V1.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm which current docs should receive the authoring-contract updates.
- Start from `AGENT.md`, `CONTEXT.md`, `skills/README.md`, and relevant category READMEs. Do not bulk rewrite unrelated docs.
- Superpowers source inspiration: https://github.com/obra/superpowers
- Preserve GOATED's schema; Superpowers' two-field frontmatter is intentionally not adopted.
- Rewrite in GOATED-native language. Do not Include attribution if substantial upstream wording or template material is reused. But make note of what was used in the chat, the user will provide attributions in the project information itself at a later date when V1 is complete and ready to make public.
