# Setup Recipe Template

## Contents

- [Default Location](#default-location)
- [Recipe Header](#recipe-header)
- [Ordered Sections](#ordered-sections)
- [Material Step Shape](#material-step-shape)
- [Evidence Rules](#evidence-rules)
- [Audit Finding Shape](#audit-finding-shape)
- [Secret And Private Data Handling](#secret-and-private-data-handling)

Use this structure when the project has no stronger setup-document convention.
Omit empty sections and link to existing declarative sources instead of copying
their contents.

## Default Location

Store the shared current recipe at `docs/setup/project-setup.md`. Keep it
tracked and suitable for teammates and future agents.

Use `.local/goated/setup-scribe/<effort-slug>.md` only for resumable uncertain,
sensitive, temporary, or machine-specific staging after confirming `.local/`
is ignored. Otherwise use operating-system temporary storage.

## Recipe Header

```markdown
# Project Setup

## Supported Environments

<Supported and unsupported platforms, shells, runtimes, and material limits.>

## Sources Of Truth

- `<path>` - <fact owned by this manifest, config, container, or task runner>
```

Do not use the header to imply support that has not been verified or
source-backed.

## Ordered Sections

Use the applicable sections in this order:

1. Supported environments
2. Prerequisites
3. Required tool installation
4. Environment configuration
5. Project dependency installation
6. Project initialization
7. Run and verification
8. Optional setup
9. Confirmed troubleshooting
10. Automation
11. Remaining manual or unverified steps

Add a section only when it helps reproduce the project. Preserve project
language and established headings when adapting an existing document.

## Material Step Shape

```markdown
### <Ordered action>

- Why: <project dependency or outcome>
- Source of truth: `<path or authoritative reference>` | `recipe-owned`
- Platform: <all supported | named platform>
- Scope: <project | user | machine | external-service>
- Evidence: <verified | source-backed | unverified>
- Action: <command, setting path, or concise manual action>
- Expected result: <observable result>
- Verification: <safe check and observed or expected result>
- Cleanup: <material rollback, uninstall, or "not material">
- Automation: <existing | generated-unverified | proposed | manual>
```

Keep `Action` concise. If a manifest or task runner owns the detail, point to
the command that consumes it rather than copying versions or configuration.

For a GUI action, name the application, stable setting path, chosen value,
project reason, and verification. Mark the step `unverified` when the setting
cannot be inspected safely.

## Evidence Rules

- `verified`: performed or safely checked in the applicable environment with
  an observable successful result.
- `source-backed`: supported by current project or authoritative evidence but
  not replayed here.
- `unverified`: inferred from recollection, final state, or incomplete
  evidence.

Evidence describes the step, not the whole recipe. A recipe with one verified
command and three inferred settings has mixed evidence.

Never say a reconstructed command was executed. Never treat a generated script
as verified until it is separately approved and run successfully in an
applicable environment.

## Audit Finding Shape

```markdown
### <Recipe item or missing step>

- State: <current | stale | missing | moved | unverifiable | obsolete>
- Current evidence: `<path, command, or authoritative source>`
- Finding: <specific difference or confirmed match>
- Repair: <smallest proposed recipe or source update>
- Verification gap: <remaining uncertainty; omit when none>
```

Use `moved` when the fact remains valid but its owning source or path changed.
Use `obsolete` only when current evidence shows the step is no longer needed.

## Secret And Private Data Handling

Record a variable name such as `SERVICE_API_TOKEN`, the approved acquisition
method, and a safe presence check. Never record the value.

Exclude private local paths, account names, machine identifiers, and unrelated
personal settings unless a project requirement makes a generalized form
necessary. Keep sensitive unresolved details out of the tracked recipe.
