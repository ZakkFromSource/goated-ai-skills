# Install And Adapt GOATED AI Skills

GOATED AI Skills supports an integrated V2 installation and individual skill
installation. Both remain docs-first in this foundation release: copy or adapt
the files into the agent framework you already use.

The integrated stack is the recommended V2 mode. Individual installation
remains supported when you need one specialist workflow or cannot apply shared
instructions.

## Integrated Stack Installation

Registry `path` values are portable package paths resolved from one GOATED
distribution root. That root contains sibling `skills/` and `stack/`
directories.

1. Create or choose a distribution root such as `<goated-root>/`.
2. Copy `stack/` and the selected complete folders under `skills/` into that
   root without changing their package-relative paths. For example,
   `<goated-root>/skills/engineering/tdd/SKILL.md` matches the registry path
   `skills/engineering/tdd/SKILL.md`.
3. Configure your framework to discover skills from `<goated-root>/skills`, or
   add a thin framework adapter that maps the registry's package paths to the
   framework's installed skill locations.
4. Use `<goated-root>/stack/AGENTS.md` as the shared GOATED
   policy. Merge it into the instruction artifact your framework actually
   applies; do not assume every framework reads `AGENTS.md`.
5. Keep stronger user, organization, and target-project instructions when
   merging the shared policy.
6. Run `uv run python scripts/validate_skills.py` in this source checkout before
   distributing a changed catalog.

The integrated policy owns shared behavior, the registry owns cross-skill
metadata, and each installed `SKILL.md` owns its specialist procedure. The
registry is data for routing and validation; it is not an installer or runtime.
Its paths describe the portable distribution layout, not a universal
framework-native filesystem location.

## Individual Skill Installation

1. Choose one folder under `skills/<category>/<skill-name>/`.
2. Copy the whole folder, including `SKILL.md` and any `references/`,
   `scripts/`, or `assets/`.
3. Put it where your framework discovers reusable skills or instructions.
4. Invoke it directly or route to it from a thin framework instruction.

An individual skill remains usable without `stack/AGENTS.md`,
`stack/goated-stack.yaml`, or this repository's root files. During the staged
V2 migration, current skill folders retain their standalone V1 behavior.

## Three Layers

Layer 0: Skill Pack Distribution

- Clone, download, copy, or install skill folders from this repo.
- Put them where your chosen agent framework discovers skills, commands, prompts, or workflow files.
- Do not treat this repo as a template that must be cloned into every target project.

Layer 1: Target Project Onboarding

- Choose a lightweight, standard, or full onboarding artifact budget from one
  discovery pass. Create or refresh only artifacts that solve a demonstrated
  retrieval, terminology, standards, architecture, or routing need.
- Lightweight projects may stop after shared-policy merge and thin framework
  routing. `CONTEXT.md`, a context matrix, and a standards profile are
  optional.
- For resumable work, use `.local/goated/work-envelopes/` and
  `.local/goated/handoffs/` only after verifying `.local/` is ignored.
- Use OS temp `goated-handoffs/<project-name>/` when project-local state is
  inappropriate or cannot be stored safely.

Layer 2: Target Project Delivery

- Use the installed delivery skills inside the target project for PRDs, architecture plans, issues, prototypes, just-in-time implementation plans, TDD, review, security checks, docs, commit messages, and handoffs.

## Generic Adaptation Pattern

1. Keep each copied skill folder intact.
2. If your framework needs a routing file, add a short instruction that points
   to the installed skills.
3. For integrated installs, merge the shared policy into that framework
   instruction instead of copying specialist procedures into it.
4. Do not require copied skills to load this repo's root `AGENT.md`,
   `README.md`, or `CONTEXT.md`.

Installed skills should retain a compact standalone fallback. They may
reference files inside their own skill folder, but should not depend on this
source repo at runtime.

Use `using-goated-ai-skills` as the portable router when an installed stack needs to choose the right GOATED workflow. It is docs-first guidance for skill selection, not runtime bootstrap, hook installation, automatic loading, or adapter manifest generation.

## Next: How To Use The Stack

After the skill folders are copied or adapted into your agent framework, read [how-to-use.md](how-to-use.md) for the human operator manual. It explains the onboarding and delivery pipelines, what each current skill does, and how to prompt the stack during real project work.

## Codex Notes

For Codex-style skill systems, copy skill folders into the configured skills directory or project skill location supported by your environment. Keep the folder name and `SKILL.md` together.

If the environment supports repo instructions, use a thin adapter that routes Codex to the installed skills and target-project artifacts. Do not paste the full GOATED workflow into every target project.

## Claude Code Notes

For Claude Code-style workflows, adapt each skill into the supported command, skill, or instruction format for that environment. If a project instruction file is used, keep it short and route to the installed skills.

Use `agent-instructions-integrator` to help create the correct target-project routing instructions.

## Hermes Notes

For Hermes-style workflows, copy or adapt GOATED skill folders into the Hermes skill/workflow location. Preserve the skill body and references so each skill remains self-contained.

If Hermes uses a central skill registry or index, add the installed skills there without making them depend on this source repo.

## OpenCode Notes

For OpenCode-style workflows, place copied or adapted skills wherever OpenCode expects reusable agent instructions. If the framework uses a single instruction file, keep it as a router to installed skills rather than a duplicate of every skill body.

## Target Project Artifacts

Installed skills should use these defaults around a target project:

```text
CONTEXT.md                         optional tracked project context and language
docs/agents/context-matrix.md      optional tracked context map
docs/agents/project-standards.md   optional tracked standards profile
docs/agents/external-docs/         optional dated, attributed external-doc lookup notes
docs/specs/                        tracked specs only when product scope, roadmap intent, or acceptance criteria need durable capture
docs/agents/architecture-plan.md   tracked project-wide architecture blueprint when useful
docs/architecture/                 tracked feature-specific architecture blueprints when useful
.local/goated/work-envelopes/      ignored resumable work state after ignore verification
.local/goated/handoffs/            ignored resumable handoffs after ignore verification
<os-temp>/goated-handoffs/<project-name>/ fallback temporary handoff notes
.local/scratch/                    ignored temporary notes or experiments
```

Durable project facts should be tracked. Session-private state should remain
ignored; use OS temp when a safe ignored project-local path is unavailable.

## Out Of Scope For The V2 Foundation

- Installer scripts.
- Automatic framework detection.
- Generated skill indexes.
- Compatibility testing across every agent framework.
- Adapter repair automation.
- Runtime hooks, automatic loading, or Factory orchestration.
