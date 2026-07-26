---
name: setup-scribe
description: Use when project-dependent installation, environment changes, application or machine settings, manual setup, setup backfill, reproducibility drift, or replay automation would otherwise be lost or become stale.
metadata:
  goated-category: productivity
---

# Setup Scribe

## Purpose

Preserve the evidence-bounded path required to recreate a project's working
environment.

Scribe maintains one ordered current setup recipe that points to manifests,
configuration, and automation instead of duplicating them. It can capture
setup during current work, reconstruct undocumented setup, audit recipe drift,
or propose safe replay automation.

Scribe is project-first. Include a user-, machine-, or external-service change
only when the project depends on it. It does not passively monitor activity or
maintain a personal computer journal.

## Inputs

- The setup request or setup-affecting project work.
- Current project instructions, setup docs, manifests, lockfiles, environment
  templates, containers, toolchain files, task runners, configuration, and
  automation.
- Commands or manual actions observed in the current session.
- User-provided recollection for backfill, treated as recollection rather than
  execution evidence.
- Supported environments, action reach, consent, privacy constraints, and
  available verification.

## Dependencies

Hard: None.

Soft:
- `documentation-writer` when the required artifact is a substantial
  onboarding manual or runbook rather than a focused setup recipe
- `doc-sync` when related changed facts outside the recipe may have drifted
- `learning-capture` for separately requested reusable lessons
- `code-security-review` when permissions, secrets, protected settings,
  external services, or unsafe execution are involved
- `verification-before-completion` for complex or multi-surface reproducibility
  claims

Fallback: Without an integrated policy or companion skills, apply the scope,
evidence, approval, safety, and closeout rules below. Use ordinary project
files and available commands; mark gaps instead of inventing proof.

## Workflow

1. Decide whether Scribe is relevant:
   - Select it when durable project setup knowledge is missing, changed, stale,
     or suitable for replay automation.
   - Skip it for changes that do not affect reproducibility. Do not produce a
     ceremonial skip report.
   - Treat `reproducibility-impact` as a conditional checkpoint signal in an
     integrated stack, not as a mandatory gate for every task.

2. Choose one primary mode:
   - **Capture:** collect project-relevant setup observations during current
     work and reconcile them at closeout.
   - **Backfill:** reconstruct a candidate recipe from current evidence and
     recollection without claiming the original historical sequence.
   - **Audit:** compare the recipe with fresh current project evidence.
   - **Automate:** propose or generate replay tooling for suitable,
     evidence-bounded steps.
   - Combine modes only when the request genuinely needs them; keep one mode as
     the controlling purpose.

3. Resolve scope and artifact ownership:
   - Follow the project's established setup-document and automation
     conventions.
   - With no convention, use `docs/setup/project-setup.md` for the tracked
     recipe and `scripts/setup/` for approved automation.
   - Maintain one authoritative current recipe. Let version control preserve
     normal history; add a chronological history only when requested or
     established by project convention.
   - Stage uncertain, sensitive, temporary, or machine-specific observations
     in session state. For resumable staging, use
     `.local/goated/setup-scribe/<effort-slug>.md` only after verifying
     `.local/` is ignored; otherwise use operating-system temporary storage.
   - Read [Setup Recipe Template](references/setup-recipe-template.md) when
     creating, backfilling, or materially restructuring the recipe.

4. Build a source and evidence map:
   - Reference declarative sources rather than copying their facts. Manifests,
     lockfiles, containers, environment templates, toolchain files, task
     runners, and checked-in configuration retain ownership of their details.
   - Let the recipe own prerequisites, order, rationale, manual actions,
     verification, material cleanup, gaps, and links between sources.
   - Classify each material step:
     - `verified`: performed or safely checked in the applicable environment
       with an observable successful result;
     - `source-backed`: supported by current project or authoritative evidence
       but not replayed in the current environment;
     - `unverified`: inferred from recollection, final state, or incomplete
       evidence.
   - Record platform, scope (`project`, `user`, `machine`, or
     `external-service`), expected result, verification method, and automation
     state where they affect safe reproduction.

5. Perform the selected mode:
   - **Capture:** collect routine low-risk observations quietly. At closeout,
     reconcile them with the current recipe and declarative sources. Update
     clear required steps when existing project-write consent covers them.
   - **Backfill:** inspect current evidence first, then add recollection as
     `unverified`. Describe the result as a reconstruction, never an exact
     transcript of commands previously run.
   - **Audit:** classify each relevant recipe item as `current`, `stale`,
     `missing`, `moved`, `unverifiable`, or `obsolete`; cite the fresh evidence
     used and propose the smallest repair.
   - **Automate:** read
     [Automation And Safety](references/automation-and-safety.md), propose the
     automation before creating it unless the user already requested it, and
     preserve manual checkpoints. A task-runner entry point does not by itself
     justify newly written non-Bash imperative replay logic.

6. Reconcile approval and safety:
   - Ask or defer when an observation is uncertain, personal, sensitive,
     outside current project-write reach, or conflicts with project policy.
   - Replace secret values with variable names, placeholders, or safe
     acquisition instructions. Never place credentials, tokens, licence keys,
     private certificates, or restricted values in tracked recipes or scripts.
   - Require fresh applicable approval for destructive actions, credentials,
     external changes, protected locations, machine-wide settings, or actions
     beyond current consent.
   - Treat creating automation and executing it as separate actions. Never
     execute newly generated setup automation merely because it was created.
   - Emit or route `security-impact` when setup touches a trust boundary,
     permission, secret, protected setting, unsafe execution, or external
     service.

7. Verify and close out:
   - Verify only the steps safe and applicable to the current environment.
   - Do not promote generated automation to `verified` through generation,
     review, linting, or static inspection alone.
   - Preserve manual and evidence gaps visibly.
   - Return one compact delta: mode, recipe or proposal changed, evidence
     states, verification performed, deferred items, approval needs, and route
     signals.
   - Read [Pressure Scenarios](references/pressure-scenarios.md) when time,
     authority, sunk-cost, or convenience pressure encourages false proof,
     secret capture, source duplication, or automatic execution.

## Output Contract

Produce or update one ordered current setup recipe, one audit result, or one
automation proposal according to the selected mode.

For each material step, preserve:

- action and rationale;
- source-of-truth link when another artifact owns the detail;
- platform and scope when material;
- `verified`, `source-backed`, or `unverified` evidence state;
- expected result and verification method;
- material rollback or cleanup;
- automation state and remaining manual work.

In chat, report only material non-empty fields:

```markdown
- Mode: <capture | backfill | audit | automate>
- Recipe: <created | updated | unchanged | proposed path>
- Evidence: <verified, source-backed, and unverified summary>
- Verification: <checks and observable results>
- Deferred: <manual, uncertain, sensitive, or out-of-reach items>
- Approval: <required next action; omit when none>
- Route delta: <reproducibility, security, docs, or proof signal; omit when none>
```

## Delegation

Main owns project scope, evidence classification, approval interpretation,
artifact integration, safety judgment, and final communication.

Delegate only bounded source discovery, one platform branch, drift comparison,
or static automation review. Require inspected paths and commands, evidence,
assumptions, uncertainty, and status. The main agent must review results before
changing the recipe or making a reproducibility claim. Without delegation,
perform the same passes sequentially.

## Guardrails

- Do not claim passive observation of commands, settings, or GUI actions that
  were not available in the session.
- Do not include unrelated personal preferences or machine customization.
- Do not duplicate facts owned by declarative project sources.
- Do not convert recollection, final state, generated output, or static
  inspection into execution evidence.
- Do not hide unsupported platforms, privileges, package-manager differences,
  system APIs, or manual gaps behind a cross-platform claim.
- Do not create automation without covered consent, or execute newly generated
  automation without separate authority and safety checks.
- Do not store secrets or private machine details in tracked or public output.
- Do not replace substantial manuals, doc drift review, learning notes,
  handoffs, or broad knowledge retrieval.
- Do not require this source repository, an integrated registry, hidden chat
  history, or local staging state after installation.

## References

- [Setup Recipe Template](references/setup-recipe-template.md) - read when
  creating, backfilling, or materially restructuring a recipe.
- [Automation And Safety](references/automation-and-safety.md) - read before
  proposing, generating, reviewing, or approving replay automation.
- [Pressure Scenarios](references/pressure-scenarios.md) - read when pressure
  may encourage shortcuts or when evaluating Scribe behavior.
