# Future Automation And Validation

These ideas are intentionally out of scope for V1.

## Deferred Upgrades

- Machine-readable skill manifests beyond lean `SKILL.md` frontmatter.
- Framework-specific plugin manifests and marketplace packaging.
- Generated skill indexes.
- Automated schema validators.
- Runtime bootstrap or automatic prompt/session-context injection.
- Hook-based skill activation.
- Automatic skill loading or automatic activation behavior.
- Automatic framework detection and setup automation.
- Adapter repair scripts.
- Adapter sync, release, version, or drift automation.
- Cross-agent compatibility test suites.
- Skill-trigger evaluation harnesses or trigger-test frameworks; revisit through a future PRD after real usage reveals recurring trigger-selection or skill-compliance failures, per [archived issue 043](../issues/archive/043-research-skill-trigger-eval-harnesses.md).
- Installer tooling.
- Full security audit workflows.
- Dependency, secret, and SAST scanner integrations.
- Generated pipeline diagrams from metadata.
- Remote issue tracker variants for local-first planning skills, such as publishing `prd-to-issues` slices to GitHub Issues, Linear, Jira, or similar systems.

## Why Deferred

V1 should prove the workflow and artifact shapes first. Automation should follow stable conventions, not force premature complexity.
