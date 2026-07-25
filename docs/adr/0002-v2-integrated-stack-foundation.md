# ADR 0002: V2 Integrated Stack Foundation

## Status

Accepted on 2026-07-25.

This ADR supersedes the installation-primary and per-skill self-containment
decisions in [ADR 0001](0001-v1-runtime-bootstrap-and-adapter-automation.md).
ADR 0001 remains the historical V1 decision and remains authoritative for the
runtime-automation exclusions not replaced here.

## Context

V1 distributes manually copied, self-contained skill folders. That experience
must remain usable, but requiring every skill to carry the whole routing,
delegation, evidence, approval, and closeout policy creates repeated prompt
cost and inconsistent orchestration when the complete stack is installed.

V2 needs one portable policy and one validated catalog that future routing
work can consume. It must establish those shared contracts without migrating
every skill at once or making a standalone skill depend on this source
repository.

The completed V1 implementation is preserved by the annotated Git tag
`v1-baseline`, which resolves to commit `e3b5b26`.

## Decision

V2 has two supported installation modes:

1. **Integrated stack**, the recommended V2 mode, installs selected skill
   folders together with:
   - `stack/AGENTS.md`, the portable shared-policy template;
   - `stack/goated-stack.yaml`, the machine-readable catalog;
   - `stack/schemas/stack-registry.schema.json`, its versioned schema;
   - human-readable work-envelope and evidence-entry templates.
2. **Individual skill**, the compatibility mode, copies one complete skill
   folder and uses its specialist procedure and compact standalone fallback.

The integrated policy owns universal behavior. The registry owns cross-skill
orchestration metadata. Each `SKILL.md` remains authoritative for how that
skill performs its specialist work.

An individually copied skill must remain safely and usefully operable without
the shared policy or registry. “Self-contained” is therefore narrowed from
“repeat all stack-wide behavior” to “retain the task-critical activation,
procedure, evidence, safety, and fallback guidance needed when invoked alone.”
Later V2 migrations may remove duplicated global policy from skills only after
preserving that fallback.

`stack/AGENTS.md` is a source template, not a universal filename requirement.
Installers or users merge its behavior into the instruction artifact their
framework actually applies, while preserving stronger user and project rules.

The registry contract is versioned independently from the stack release. It
represents the current implemented catalog. Future tickets may migrate
canonical names and add aliases without creating duplicate alias folders.

## Decisions From ADR 0001 That Remain In Force

This decision does not authorize:

- runtime bootstrap or automatic skill loading;
- hooks or prompt injection;
- generated plugin manifests;
- installer or adapter-repair automation;
- automatic framework detection;
- executable orchestration or a Factory runtime.

Those capabilities still require separately scoped decisions and
implementation work.

## Consequences

Positive:

- complete-stack installs can share policy once;
- registry structure and source cross-references have one validation path;
- routing work can depend on stable contract names rather than prose scans;
- standalone skill installation remains available during staged migration.

Costs and constraints:

- integrated installation includes shared files beyond the selected skills;
- registry changes must stay synchronized with skill paths and names;
- the current catalog uses current V1 skill names until the tickets that own
  canonical renames add aliases and migrate references;
- shared policy changes now affect every integrated-stack workflow and require
  responsibility-boundary review.
