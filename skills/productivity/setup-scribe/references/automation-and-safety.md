# Automation And Safety

## Contents

- [Selection Order](#selection-order)
- [Creation Gate](#creation-gate)
- [Generated Automation Checklist](#generated-automation-checklist)
- [Bash Entry-Point Pattern](#bash-entry-point-pattern)
- [Execution Gate](#execution-gate)
- [Manual Checkpoints](#manual-checkpoints)

Read this before proposing, generating, reviewing, or approving setup replay
automation.

## Selection Order

Prefer the first suitable option:

1. Existing declarative configuration or project task runner.
2. Portable, POSIX-conscious Bash.
3. A narrowly scoped platform-native helper when Bash is unreliable.
4. BAT only for a demonstrated compatibility need.
5. An explicit manual checkpoint for unsafe or non-automatable work.

An existing task runner may expose the setup entry point. If it cannot express
the operation declaratively and new imperative replay logic is required, keep
that logic Bash-first unless Bash is demonstrably unreliable for the specific
operation. Do not treat `npm`, another ecosystem runner, or a cross-platform
runtime as an automatic reason to skip Bash.

Treat Bash as the preferred orchestration language, not proof that commands,
paths, package managers, privileges, or system APIs are portable.

When Bash is used on Windows, document Git Bash or another compatible Bash
environment as a prerequisite. A shared Bash entry point may call a narrow
PowerShell helper for Windows registry, service, permission, or API behavior
that Bash cannot handle reliably. Keep the helper's input, action scope, and
supported platform explicit.

## Creation Gate

Propose the automation before creating it unless the user explicitly requested
automation or existing consent clearly covers the artifact.

Before creation, state:

- target path and supported environments;
- actions automated and manual gaps retained;
- project, user, machine, or external-service reach;
- required privileges and dependencies;
- destructive, credentialed, or external effects;
- evidence state of every automated step;
- intended preview, verification, and rerun behavior.

Do not automate an `unverified` destructive or machine-wide step merely to make
the recipe look complete.

## Generated Automation Checklist

Generated automation must:

- check prerequisites before mutation;
- fail clearly with an actionable message;
- disclose platform, privilege, and action scope;
- detect already satisfied steps;
- be safe to rerun where practical;
- avoid embedded secrets and private machine values;
- acquire sensitive input through an approved mechanism;
- support preview or dry-run behavior when feasible;
- verify material stages with observable checks;
- preserve deliberate manual checkpoints;
- document unsupported environments and rollback where material.

Idempotence is a goal, not a label. If a step cannot safely detect prior state,
say so and keep it manual or require an explicit confirmation.

## Bash Entry-Point Pattern

Use a small, readable entry point:

```bash
#!/usr/bin/env bash
set -euo pipefail

preview=false
if [[ "${1:-}" == "--dry-run" ]]; then
  preview=true
fi

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing prerequisite: $1" >&2
    exit 1
  }
}

require_command git
```

This is a shape, not a complete setup script. Add only project-required
commands. Quote paths and variables, avoid `eval`, and do not use remote
download-to-shell pipelines as a convenience shortcut.

If invoking a native helper, validate the platform and pass explicit
non-secret arguments. The helper must perform only the native operation it
owns; do not duplicate the whole setup flow in two languages.

## Execution Gate

Creation approval does not authorize execution.

Before any execution:

- inspect the final script and resolved targets;
- confirm current consent covers its action reach;
- obtain fresh approval for destructive, credentialed, protected,
  machine-wide, privileged, or external changes;
- prefer preview first when it provides meaningful evidence;
- protect current user data and existing configuration;
- define the verification and recovery path.

Never describe generated automation as `verified` because it parsed, linted,
rendered, or passed static review. Verification requires separately authorized
execution or a safe equivalent check in an applicable environment, plus an
observable successful result.

## Manual Checkpoints

Keep a step manual when automation would obscure:

- an irreversible or destructive choice;
- interactive authentication or credential handling;
- a GUI-only setting without a stable supported interface;
- an external-service change requiring accountable human review;
- a platform branch that cannot be detected reliably;
- a recovery decision that depends on current local state.

Document what the operator must do, why automation stops, the expected result,
and how to verify it.
