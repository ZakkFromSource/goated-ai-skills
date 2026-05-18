## Parent PRD

`issues/prd-goated-ai-skills-v1-public-core.md`

## Type

AFK

## What to build

Confirm and tighten the source repo scaffold so it clearly presents GOATED AI Skills as a public distribution library, not a target-project template. Cover the PRD sections "Root Repo Requirements", "Public/Private Boundary", "Installation Requirements", and "Acceptance Criteria".

## Acceptance criteria

- [x] Root docs distinguish the source repo, installed skills, and target projects.
- [x] `README.md`, `CONTEXT.md`, `AGENT.md`, `AGENTS.md`, and `CLAUDE.md` stay aligned with their source-repo responsibilities.
- [x] `.gitignore` ignores `.local/`, and no public behavior depends on `.local/`.
- [x] `skills/agent-workflows/`, `skills/engineering/`, and `skills/productivity/` exist as the only active public category folders.
- [x] No actual `SKILL.md` files are created by this issue.
- [x] Public docs do not include private names, handles, credentials, client data, or sensitive personal context.

## Blocked by

- None - can start immediately

## User stories addressed

- As an agent user, I can understand that this repo is the distribution home for reusable skills.
- As a maintainer, I can preserve the public/private boundary before implementation starts.
