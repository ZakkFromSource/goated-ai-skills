## Parent PRD

`issues/prd-goated-ai-skills-v1-superpowers-absorption.md`

## Type

AFK

## What to build

Update relevant GOATED skills so they soft-depend on `verification-before-completion` before they make completion, correctness, review readiness, or documentation-sync claims.

## Acceptance criteria

- [x] Implemented skills that close out engineering work mention `verification-before-completion` as a soft dependency or final gate where appropriate.
- [x] At minimum, inspect `tdd`, `standards-and-spec-review`, `code-security-review`, `doc-sync`, `commit-message`, `write-a-prd`, `prd-to-issues`, `prototype`, `plan-codebase-architecture`, and `improve-codebase-architecture` for verification routing needs.
- [x] The update does not force verification ceremony for tiny direct commands or tasks where the user explicitly requested only a draft or analysis.
- [x] Each edited skill remains self-contained after installation and does not depend on this source repo's root files.
- [x] Category READMEs or root docs are updated only if needed to avoid routing drift.
- [x] The final implementation report lists which skills were changed and which were inspected but left unchanged.

## Blocked by

- `issues/archive/036-add-verification-before-completion-skill.md`

## User stories addressed

- As an agent user, I can expect proof-backed closeout across the GOATED stack instead of one isolated verification skill.
- As a maintainer, I can keep verification routing consistent without duplicating a long proof workflow in every skill.

## Implementation notes

- Use `grill-with-docs` before implementation to confirm which existing skills and docs are in scope.
- Superpowers source inspiration: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
- Keep dependency language soft unless the skill truly cannot produce a safe output without verification.
- Do not pre-wire skills that do not exist yet; instead make their implementation issues reference `verification-before-completion`.
