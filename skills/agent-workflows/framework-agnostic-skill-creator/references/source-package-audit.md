# Source Package Audit

Use this reference before porting any source folder, repo slice, public package, or source entrypoint with adjacent support files.

The goal is to understand the source as a package before judging what is portable. A small entrypoint can depend on templates, references, scripts, examples, assets, producer artifacts, or consumer artifacts that carry the real workflow behavior.

## Audit Order

1. Define the package boundary:
   - Start from the user-provided folder, repo slice, link, or explicit entrypoint.
   - Include first-party files in that package unless they are generated, vendored, binary, or clearly unrelated.
   - Keep source repo maintenance guidance, installed-skill runtime behavior, and target-project artifacts separate.

2. Recursively inventory the package:
   - List every first-party file or link that appears to belong to the provided package.
   - Group files by role: entrypoint, reference, template, script, example, asset, producer artifact, consumer artifact, config, generated/vendor/binary, or unknown.
   - For public links, inspect the directory listing or package tree before opening only the obvious entrypoint.

3. Read behavior-bearing support files:
   - Read references, templates, scripts, examples, and config when they define triggers, decisions, generated output, commands, file layouts, user questions, or validation behavior.
   - Read producer artifacts that create setup, configuration, issues, docs, or instructions.
   - Read consumer artifacts that downstream skills, agents, or users are expected to rely on.
   - Treat assets as evidence when they affect output shape, examples, prompts, templates, or user-visible behavior.

4. Skip deliberately:
   - Skip generated, vendored, binary, lock, cache, or bulky media files unless they clearly define behavior.
   - Skip unrelated neighboring files outside the package boundary.
   - Record every skipped file group with a reason and residual risk.

5. Build the manifest before judging:
   - Record `Files/Links Inspected` with source, type, why it was inspected, and behavior evidence found.
   - Record `Skipped Files / Why` with source, reason, and residual risk.
   - Only after the manifest exists, summarize behavior, classify portability, or design the neutral GOATED shape.

## File Roles

- **Entrypoint**: primary skill, command, prompt, readme, or instruction file that activates the workflow.
- **Reference**: longer procedure, checklist, adapter notes, or detailed examples read by the entrypoint.
- **Template**: seed output or file content the workflow writes, updates, or asks the user to customize.
- **Script**: deterministic helper whose arguments, outputs, failure behavior, or side effects shape the workflow.
- **Example**: sample input or output that shows intended behavior, edge cases, tone, or scope.
- **Asset**: packaged material such as fixtures, diagrams, images, snippets, or reusable resources.
- **Producer artifact**: a file that describes what the workflow creates or updates.
- **Consumer artifact**: a file that downstream agents, skills, or users are expected to read after setup.
- **Config**: metadata, adapter config, package metadata, or framework discovery information.

## Extraction Checklist

When reading the package, identify:

- Core behavior that should survive in a portable GOATED skill.
- Source-specific details that are useful as-is for the destination workflow.
- Source-specific details that should become adapter notes, examples, detection rules, or fallbacks.
- Project-only assumptions such as issue trackers, label names, docs paths, instruction-file precedence, commands, and release processes.
- Public/private risks, including names, credentials, client context, sensitive personal data, or non-public operating assumptions.
- Hard dependencies, soft dependencies, and graceful fallback paths.
- Verification steps, stopping conditions, and user confirmation points.

## Translation Notes

Do not flatten all source specificity into bland generic behavior. Branded names, commands, filenames, issue tracker conventions, and docs layouts can be copied directly when they genuinely fit the destination workflow and remain public-safe.

The important check is whether the port presents those details intentionally:

- If they are required by the destination, keep them in core workflow.
- If they are useful only for one adapter or environment, place them in adapter notes or examples.
- If they are source-only assumptions, generalize them or mark them as blockers.
- If the user explicitly wants a private or domain-specific adaptation, preserve more specificity and classify it honestly.

## Boundary Checks

Before finalizing the port, confirm:

- Source repo maintenance rules are not treated as installed-skill runtime requirements.
- Installed skill guidance stays self-contained inside the skill folder and local support files.
- Target-project artifacts are described as outputs, inputs, or defaults, not as files this source repo must contain.
- The port does not require GOATED root `AGENT.md`, `README.md`, `CONTEXT.md`, issues, or handoffs after installation.
- Public output contains no private context unless the user explicitly requested a private artifact outside public main.
