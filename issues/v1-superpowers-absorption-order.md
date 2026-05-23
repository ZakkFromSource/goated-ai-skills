# V1 Superpowers Absorption Issue Order

Last updated: 2026-05-23.

Use this document after reading `issues/prd-goated-ai-skills-v1-superpowers-absorption.md`. For each issue, future agents should read the issue itself, inspect the current source files named there, and use `grill-with-docs` before implementation when the work is more than a tiny mechanical edit.

## Recommended Order

1. `issues/archive/033-update-skill-authoring-contract-superpowers-conventions.md`
   - Establish the shared conventions before new skill work depends on them. Done.

2. `issues/archive/029-expand-framework-agnostic-skill-creator.md`
   - Upgrade the skill creation path early so later skills can use the improved authoring and evaluation contract. Done.

3. `issues/archive/034-add-using-goated-ai-skills-router.md`
   - Add the portable router skill after the authoring contract is clear. Done.

4. `issues/archive/035-decide-runtime-bootstrap-and-adapter-automation.md`
   - Make the HITL runtime decision after the router exists conceptually, before anyone tries to automate it. Done.

5. `issues/archive/036-add-verification-before-completion-skill.md`
   - Add the shared closeout gate before wiring it through other skills. Done.

6. `issues/archive/037-wire-verification-through-goated-stack.md`
   - Update already implemented relevant skills to soft-depend on the verification gate. Done.

7. `issues/archive/038-add-writing-plans-skill.md`
   - Add the executable-plan contract after verification exists, so plans know what proof to request. Done.

8. `issues/archive/039-add-subagent-driven-development-skill.md`
   - Add subagent-driven development after planning and verification contracts exist. Done.

9. `issues/archive/040-upgrade-prd-to-issues-zero-context-handoffs.md`
   - Upgrade issue handoffs to route future implementers to `grill-with-docs` and `writing-plans`. Done.

10. `issues/archive/041-upgrade-tdd-superpowers-contracts.md`
    - Strengthen TDD after verification is available and before diagnose relies on the improved loop. Done.

11. `issues/archive/027-add-diagnose-skill.md`
    - Implement diagnose with Superpowers `systematic-debugging` inspiration and clear routing to TDD. Done.

12. `issues/archive/042-add-receiving-code-review-skill.md`
    - Add review feedback handling after verification exists. Done.

13. `issues/archive/043-research-skill-trigger-eval-harnesses.md`
    - Research trigger harnesses after the router and runtime decision issue are in place. Done; archived.

14. `issues/archive/028-fold-zoom-out-into-architecture-design-map.md`
    - This existing addition is mostly independent and finished before `032`. Done.

15. `issues/archive/030-defer-triage-workflow.md`
    - This existing deferral was handled before `032`. Done.

16. `issues/archive/031-add-caveman-skill.md`
    - This existing addition can be handled anytime after the authoring contract is stable. Done.

17. `issues/archive/032-v1-additions-doc-sync-and-acceptance-recheck.md`
    - Run after all V1 additions and Superpowers absorption issues are complete or explicitly deferred. Done.

18. `issues/archive/021-v1-acceptance-public-boundary-pass.md`
    - Final V1 public-boundary and acceptance pass. Done.

## Notes For Future Agents

- Treat archived issue `035` as the accepted narrow-adapter-note decision, and treat `043` as research rather than implementation permission for runtime automation.
- Keep worktree lifecycle, finish-branch lifecycle, marketplace manifests, release-note machinery, strong PR gates, and full adapter automation out of V1 unless a later PRD changes scope.
- Preserve GOATED's lean schema and public boundary in every new skill.
- If this order conflicts with a newer issue or PRD, read the newer source and surface the conflict before editing.
