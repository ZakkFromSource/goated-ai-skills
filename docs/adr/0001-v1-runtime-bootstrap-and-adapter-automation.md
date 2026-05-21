# ADR 0001: V1 Runtime Bootstrap And Adapter Automation

## Status

Accepted on 2026-05-21.

## Context

GOATED AI Skills V1 is a public source library of installable, framework-agnostic skill folders. The V1 installation model is docs-first: users clone, download, copy, install, or adapt completed skill folders into their chosen agent framework.

Issue `035` compared that model with Superpowers-inspired runtime activation ideas, including bootstrap scripts, plugin manifests, marketplace packaging, hook-based activation, and automatic skill loading.

The relevant existing constraints are:

- `AGENT.md` says V1 installation is docs-first, not automated.
- `CONTEXT.md` defines docs-first installation as manual copy, install, or adaptation using documentation instead of installer automation.
- `docs/install.md` says `using-goated-ai-skills` is docs-first guidance, not runtime bootstrap, hook installation, automatic loading, or adapter manifest generation.
- `skills/agent-workflows/using-goated-ai-skills/SKILL.md` describes routing behavior only and explicitly avoids hooks, adapter manifests, automatic activation, installer scripts, and framework detection automation.
- `skills/agent-workflows/agent-instructions-integrator/SKILL.md` allows thin target-project routing layers that point to installed skills without copying full skill bodies or assuming one framework's artifact names are universal.

Superpowers demonstrates the value of runtime activation for a plugin product: session-start bootstrap injection, framework plugin manifests, hook configuration, and automatic skill discovery can make agent behavior more reliable. Bootstrap injection means automatically adding starter instructions or router content to the agent's prompt or session context before the user asks for a specific skill. Those mechanisms are also framework-specific and change the product boundary from a portable skill library toward runtime plugin distribution.

## Decision

GOATED V1 allows **narrow adapter notes only**.

Allowed in V1:

- self-contained skill folders with lean `SKILL.md` frontmatter;
- portable router guidance such as `using-goated-ai-skills`;
- small framework compatibility notes in skill `adapters` fields;
- thin target-project instruction adapters created by `agent-instructions-integrator`;
- docs-first install and adaptation guidance.

Not allowed in V1:

- runtime bootstrap scripts or automatic prompt/session-context injection;
- hook-based skill activation;
- automatic skill loading or automatic activation behavior;
- plugin manifests or marketplace packaging;
- installer scripts, adapter repair scripts, or framework detection/setup automation;
- adapter sync, release, version, or drift automation.

## Consequences

V1 remains framework-agnostic and public-safe. A copied skill folder must stay useful without depending on this source repo's root files, ignored local research, issue handoffs, or one agent framework's runtime behavior.

The tradeoff is that V1 does not get Superpowers-style automatic activation. Agents and users rely on docs-first installation, explicit routing guidance, and the chosen framework's native skill-loading behavior.

Before runtime automation can be considered public-safe and framework-agnostic, future work must define:

- which product layer owns automation: this source repo, per-framework adapter packages, or external plugins;
- which frameworks are supported and how unsupported frameworks degrade gracefully;
- how installed skills remain self-contained without depending on source-repo root files;
- how user and target-project instructions keep priority over generated bootstrap behavior;
- how manifests, hooks, installers, generated indexes, and drift checks are tested across platforms;
- how public docs avoid implying silent runtime assumptions for generic users.

Any future runtime automation requires a new PRD or implementation issue with explicit scope and acceptance criteria. Issue `035` does not approve implementation.
