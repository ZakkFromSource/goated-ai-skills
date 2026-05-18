# GOATED AI Skills Context

GOATED AI Skills is a public source library for reusable, installable AI skill folders. It should feel like a compact operating system for high-quality agent work, not a prompt dump.

## Domain Language

- **Skill** - a reusable folder containing a `SKILL.md` workflow and optional `references/`, `scripts/`, or `assets/`.
- **Source repo** - this public repository, used to publish, maintain, and document the skill library.
- **Installed skill** - a copied or installed skill folder inside a user's chosen agent framework.
- **Target project** - a user's own project where installed skills are used.
- **Agent instruction artifact** - a file or configuration entry that tells a specific agent framework how to use installed skills.
- **Progressive disclosure** - load the smallest amount of context needed now, and deeper references only when the task requires them.
- **Target Project Onboarding** - preparing a target project for serious agent work.
- **Target Project Delivery** - moving one target-project change from intent through implementation, review, docs, and handoff.
- **Public core** - portable skills safe for public use.
- **Private adaptation** - private or domain-specific extensions that use the same conventions outside public main.

## Public V1 Scope

V1 includes only active public categories:

- `agent-workflows`
- `engineering`
- `productivity`

Do not add private project names, sensitive personal domains, client context, handles, or private personal workflows to public main unless they are sanitized into genuinely portable public skills.

## Quality Bar

Skills should be:

- installable into different agent frameworks;
- self-contained after installation;
- specific enough to change agent behavior;
- concise enough to avoid context bloat;
- explicit about triggers, outputs, guardrails, dependencies, and delegation;
- portable unless classified otherwise;
- honest about what they cannot verify.
