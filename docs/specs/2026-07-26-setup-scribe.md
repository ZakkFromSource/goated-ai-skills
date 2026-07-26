# Setup Scribe

## Status

Ticket Ready

## Mode

Compact

## Problem

Project setup often depends on an ordered mixture of package installation,
toolchain configuration, application or operating-system settings, manual GUI
actions, environment preparation, and verification commands. These steps are
easy to lose once the project works, especially when the final state is spread
across tracked configuration, machine-local state, and chat history.

The existing GOATED stack covers documentation authoring, documentation drift,
learning capture, and handoff, but no skill owns project-specific setup
reproducibility. Agents may therefore leave a working environment that another
person or future session cannot reconstruct, duplicate declarative
configuration in prose, record secrets, or generate automation that is
mistakenly treated as tested.

## Goals

- Preserve the verified path required to recreate a project's working
  environment.
- Maintain one ordered, current setup recipe that complements existing
  manifests, configuration, and automation without duplicating their facts.
- Capture setup knowledge during relevant work without adding unnecessary
  interaction.
- Reconstruct existing undocumented setup with honest evidence labels.
- Detect drift between the setup recipe and current project sources.
- Convert suitable steps into safe, reviewable, Bash-first automation.
- Keep project, user, machine, platform, privacy, and verification boundaries
  explicit.
- Work as an integrated GOATED gate and as a self-contained individual skill.

## Non-Goals

- Monitor operating-system, application, terminal, or GUI activity in the
  background.
- Maintain a general journal of personal computer customizations.
- Replace package manifests, lockfiles, containers, environment templates,
  version-manager files, task runners, or other declarative sources of truth.
- Replace substantial onboarding manuals or runbooks owned by
  `documentation-writer`.
- Replace changed-fact documentation checks owned by `doc-sync`.
- Replace reusable lesson notes owned by `learning-capture` or continuity notes
  owned by `handoff`.
- Store credentials, tokens, licence keys, private certificates, secret values,
  or other restricted data.
- Execute generated setup automation merely because it was created.
- Build framework-specific hooks, passive telemetry, or runtime monitoring.
- Guarantee that one script can automate every platform-specific or GUI step.

## Requirements

### Identity And Routing

- The canonical skill name must be `setup-scribe`, with the human-facing name
  **Scribe**, under the `productivity` category.
- The discovery description must trigger when project-dependent installation,
  environment changes, application or machine settings, manual setup, ordered
  configuration, backfill, drift auditing, or replay automation would
  otherwise be lost.
- The integrated stack must treat Scribe as a conditional project
  reproducibility gate rather than a mandatory step for every task.
- The integrated route must recognize a `reproducibility-impact` signal or the
  equivalent direct task condition when durable project setup knowledge is
  missing, changed, stale, or ready for automation.
- The individual skill must retain a compact standalone fallback that does not
  depend on this source repository, the stack registry, or hidden session
  files.

### Scope And Artifact Ownership

- Scribe must be project-first. Record machine-wide changes only when the
  project depends on them; classify optional personal conveniences separately
  or omit them.
- Prefer the target project's established setup-document and automation
  conventions.
- When no convention exists, default the shared recipe to
  `docs/setup/project-setup.md` and setup automation to `scripts/setup/`.
- Keep the shared recipe tracked and suitable for teammates and future agents.
- Keep sensitive, uncertain, temporary, or machine-specific observations in
  session state or a verified-ignored local draft. For resumable work, prefer
  `.local/goated/setup-scribe/<effort-slug>.md` after confirming `.local/` is
  ignored; otherwise use OS temporary storage.
- Maintain one authoritative current recipe. Use version-control history for
  normal evolution and create a separate chronological history only when the
  user or project convention requests one.
- Reference existing declarative artifacts instead of copying their owned
  facts. The recipe owns prerequisites, ordering, manual actions, rationale,
  verification, gaps, and links between those artifacts.

### Operating Modes

- **Capture:** collect project-relevant installation commands, settings
  changes, manual actions, outcomes, and evidence during current work, then
  reconcile them at closeout.
- **Backfill:** inspect current project evidence and user-provided recollection
  to reconstruct a candidate recipe without claiming it is the exact historical
  sequence originally followed.
- **Audit:** compare the recipe with current manifests, lockfiles, toolchain
  files, environment templates, automation, configuration paths, supported
  platforms, commands, and verification expectations.
- **Automate:** propose or generate replay tooling only for suitable verified
  or source-backed steps, while preserving manual checkpoints and evidence
  labels.
- Audit findings must distinguish `current`, `stale`, `missing`, `moved`,
  `unverifiable`, and `obsolete`.

### Evidence And Truthfulness

- Classify every material step as:
  - **Verified:** performed or safely checked in the applicable environment
    with an observable successful result.
  - **Source-backed:** supported by current project evidence or an
    authoritative source but not replayed in the current environment.
  - **Unverified:** inferred from recollection, final state, or incomplete
    evidence.
- Never present an inferred command as one that was actually executed.
- Never promote a generated script to verified merely because it was created
  or passed static inspection.
- Record platform, scope (`project`, `user`, `machine`, or `external service`),
  expected result, and verification method wherever they materially affect
  safe reproduction.
- Preserve unresolved evidence gaps in the recipe or closeout rather than
  manufacturing certainty.

### Automatic Capture And Approval

- During relevant work, collect candidate setup observations in the shared work
  envelope, session context, or approved local draft without interrupting for
  routine low-risk facts.
- At closeout, reconcile captured observations against the current recipe and
  existing declarative sources.
- When existing consent covers project documentation writes, update clear,
  verified required steps and report the change in the consolidated closeout.
- Ask or defer when a candidate is uncertain, personal, sensitive, outside the
  current project-write reach, or conflicts with project policy.
- Propose automation before creating it unless the user explicitly requested
  automation or existing consent clearly covers that artifact.
- Treat execution of newly generated automation as a separate action requiring
  applicable approval and safety checks.

### Setup Recipe Contract

- Adapt to existing project conventions and omit empty sections.
- When no stronger convention exists, support these sections as applicable:
  supported environments, prerequisites, required tool installation,
  environment configuration, project dependency installation, project
  initialization, run and verification, optional setup, confirmed
  troubleshooting, automation, and remaining manual or unverified steps.
- For each material step, capture what to do, why it matters, applicable
  platform and scope, evidence state, expected result, verification, material
  rollback or cleanup, and automation status.
- Use links and concise orchestration instructions when another tracked
  artifact owns the detailed configuration.

### Automation Policy

- Prefer automation in this order:
  1. existing declarative configuration or project task runner;
  2. portable, POSIX-conscious Bash;
  3. a narrowly scoped platform-native helper when Bash is unreliable;
  4. BAT only for a specific compatibility need;
  5. an explicit manual checkpoint for unsafe or non-automatable work.
- Document Git Bash or another compatible Bash environment as a Windows
  prerequisite when Bash automation is used on Windows.
- Permit a shared Bash entry point to invoke narrowly scoped native helpers for
  operations such as Windows registry, service, permission, or API changes.
- Generated automation must check prerequisites, fail clearly, detect already
  satisfied steps, be safe to rerun where practical, disclose action scope,
  avoid embedded secrets, support preview or dry-run behavior when feasible,
  verify material stages, and document deliberate manual gaps.
- Do not imply cross-platform support when commands, paths, package managers,
  privileges, or system APIs are platform-specific.

### Safety, Integration, And Support Files

- Replace secret values with variable names, placeholders, or safe acquisition
  instructions.
- Require explicit approval for destructive actions, credentials, external
  changes, protected locations, machine-wide settings, and other actions beyond
  current consent.
- Emit or route `security-impact` when setup or automation touches trust
  boundaries, permissions, secrets, unsafe execution, protected settings, or
  external services.
- Route substantial guide authoring to `documentation-writer`, related changed
  facts to `doc-sync`, reusable lessons to `learning-capture`, and complex
  completion claims to `verification-before-completion`.
- Keep `SKILL.md` lean and place detailed reusable guidance in:
  `references/setup-recipe-template.md`,
  `references/automation-and-safety.md`, and
  `references/pressure-scenarios.md`.
- Do not add bundled executable helpers in the first version. Add them only
  after real usage demonstrates a stable, project-agnostic operation worth
  maintaining.
- Add focused behavioral fixtures for capture, backfill, audit, automation,
  secret handling, existing-source ownership, personal-setting exclusion, and
  mixed evidence states.
- Update the registry, shared routing policy, public catalog, usage guidance,
  context or terminology docs, and validation expectations needed to make the
  new skill an integrated and individually installable part of the stack.

## Acceptance Criteria

- [ ] `skills/productivity/setup-scribe/SKILL.md` exists, follows the lean
      schema, stays within the source-repo soft line budget, and is usable
      without root repository files.
- [ ] The skill implements capture, backfill, audit, and automate modes with
      clear activation, stop, approval, and closeout behavior.
- [ ] The skill distinguishes verified, source-backed, and unverified steps and
      does not convert reconstruction or generated output into false proof.
- [ ] The skill preserves a tracked current recipe, uses ignored or temporary
      staging safely, and makes chronological history optional.
- [ ] The recipe contract is project-first, ordered, platform- and
      scope-aware, secret-safe, and adaptable to existing conventions.
- [ ] The workflow references declarative sources of truth rather than
      duplicating dependency, version, environment, or configuration facts.
- [ ] Audit mode reports current, stale, missing, moved, unverifiable, and
      obsolete findings using fresh project evidence.
- [ ] Automation prefers declarative configuration, then portable Bash, then
      narrowly scoped native helpers, with BAT and manual fallbacks used only
      when justified.
- [ ] Generated automation is never called verified or executed automatically
      without separate evidence and approval.
- [ ] The three planned reference files exist, are linked directly from
      `SKILL.md`, and contain no duplicated generic filler.
- [ ] The stack registry and shared routing policy represent Scribe's
      conditional gate, domains, profile eligibility, accepted and emitted
      signals, and standalone boundary without duplicating its procedure.
- [ ] Focused fixtures cover live capture, mixed-evidence backfill, drift
      repair, Bash-first automation with a native helper, secret rejection,
      source-of-truth reuse, and exclusion of unrelated personal settings.
- [ ] Catalog and operator documentation distinguish Scribe from
      `doc-sync`, `documentation-writer`, `learning-capture`, and `handoff`.
- [ ] Structural validation, relevant fixture checks, source searches, and
      Markdown or link checks defined by the repository pass with fresh
      evidence.
- [ ] A forward test demonstrates that an agent can produce a useful,
      evidence-labelled setup result from raw project evidence without seeing
      the intended answer; any unrun live checks are reported as residual risk.

## Constraints

- Preserve the public, framework-agnostic skill-library boundary.
- Do not require passive runtime hooks, background monitoring, one universal
  instruction filename, or one universal project docs layout.
- Reuse V2 work-envelope, evidence, approval, route-signal, and consolidated
  closeout behavior rather than duplicating shared policy in the skill.
- Keep the skill single-agent-compatible and subagent-aware.
- Keep target-project private data, credentials, and ignored local notes out of
  public source artifacts and tracked shared recipes.
- Treat Bash as the preferred automation language, not proof that every Bash
  command or dependency is portable.
- Preserve project conventions and existing user changes; avoid unrelated
  documentation or stack rewrites.

## Open Questions

None. Implementation details may be resolved during ticket planning as long as
they preserve this contract.

## Risks

- **Passive-monitoring expectations:** users may assume Scribe observes actions
  it cannot see. Mitigate with explicit capture boundaries and honest backfill.
- **Competing sources of truth:** recipes may duplicate manifests or
  configuration and drift. Mitigate with reference-not-duplicate ownership and
  audit fixtures.
- **False reproducibility:** inferred steps or generated scripts may look
  proven. Mitigate with mandatory evidence states and verification gates.
- **Secret leakage:** setup capture may encounter credentials or machine-local
  private values. Mitigate with placeholders, staging rules, and security
  routing.
- **Unsafe automation:** machine-wide or external changes may be destructive or
  difficult to reverse. Mitigate with separate creation and execution approval,
  action-scope labels, preflight checks, and manual checkpoints.
- **False Bash portability:** Git Bash availability does not make every
  platform command equivalent. Mitigate with explicit prerequisites, platform
  branches, native helpers, and unsupported-platform disclosure.
- **Closeout ceremony:** automatic capture could burden routine dependency
  changes. Mitigate by selecting the gate only when durable setup knowledge
  would otherwise be lost and returning a compact no-impact result.
- **Workflow overlap:** Scribe could absorb manuals, doc drift, learning notes,
  or handoffs. Mitigate with explicit ownership boundaries and routing fixtures.

## Sources

- `AGENT.md` — source-repository contribution, public-boundary, progressive
  disclosure, validation, and new-skill ticket requirements.
- `CONTEXT.md` — product boundaries, V2 integrated-stack concepts, artifact
  meanings, skill anatomy, categories, and quality bar.
- `docs/specs/2026-07-25-goated-ai-skills-v2.md` — shared policy, registry,
  evidence, route-signal, fixture, fallback, and proportionality contracts.
- `stack/AGENTS.md` — integrated approval, evidence, safety, routing, and
  closeout behavior that Scribe must reuse.
- `stack/goated-stack.yaml` — current registry metadata and route-signal model.
- `skills/agent-workflows/framework-agnostic-skill-creator/SKILL.md` — new
  GOATED skill shape, support-file, evaluation, portability, and validation
  requirements.
- `skills/engineering/doc-sync/SKILL.md` — changed-fact documentation boundary.
- `skills/engineering/documentation-writer/SKILL.md` — substantial guide and
  runbook authoring boundary.
- `skills/productivity/learning-capture/SKILL.md` — reusable lesson capture
  boundary.
