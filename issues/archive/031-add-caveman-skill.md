## Parent PRD

`issues/prd-goated-ai-skills-v1-additions.md`

## Type

AFK

## What to build

Implement `caveman` under `skills/productivity/`. The skill should provide a user-triggered compact communication mode while preserving technical accuracy, safety, uncertainty, exact errors, confirmations, code blocks, and required output contracts.

## Acceptance criteria

- [x] `skills/productivity/caveman/SKILL.md` exists and follows the lean schema.
- [x] The skill activates on explicit compact-mode requests such as "caveman mode", "use caveman", "less tokens", or "be brief".
- [x] The skill defines when compact mode persists and how the user exits it.
- [x] The workflow compresses prose without changing code blocks, exact errors, technical terms, warnings, assumptions, or required output formats.
- [x] Examples use simple Python and PostgreSQL, replacing upstream examples.
- [x] Guardrails require normal clarity for destructive confirmations, security warnings, multi-step instructions that could be misread, and user confusion.
- [x] MIT attribution is included if substantial upstream wording is reused.

## Blocked by

- `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`

## User stories addressed

- As an agent user, I can ask for compact responses without losing important technical or safety context.
- As a maintainer, I can include a productivity skill that is portable and public-safe.

## Implementation notes

- Use the upstream skill as inspiration: https://github.com/mattpocock/skills/blob/main/skills/productivity/caveman/SKILL.md
- Keep the public skill name `caveman`.
- Implement after the authoring-contract updates in `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md` are complete.
- Do not let brevity override GOATED output contracts, review findings, user confirmations, uncertainty, or security/safety language.
- The installable skill intentionally omits upstream attribution, license text, and reference links per maintainer instruction; public project attribution will be handled separately before publication.
