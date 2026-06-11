---
name: code-security-review
category: engineering
classification: portable
status: wip
description: Use when reviewing a diff, PR, patch, source area, auth flow, trust boundary, or data path for security issues and exploitable behavior.
triggers:
  - user asks for a security review, static security scan, vuln review, exploitability review, trust-boundary review, auth review, or data-leak review
  - implementation work touches user data, auth, permissions, persistence, network calls, file handling, command execution, secrets, config, dependencies, or sandboxing
  - standards-and-spec-review is complete and the change needs a security-focused review gate before doc sync, commit, PR, or handoff
  - a reviewer needs high-confidence security findings separated from standards, style, spec fit, architecture, or general cleanup concerns
outputs:
  - security review scope with fixed point, changed files, review surface, and evidence inspected
  - trust-boundary map covering entry points, privileged operations, sensitive assets, and sinks
  - severity-classified findings with affected paths, evidence, impact, recommended fix, confidence, and false-positive control
  - explicit no-findings statement when no high-evidence security findings are detected
  - assumptions, skipped areas, residual risk, and a clear statement that this is not full audit coverage
depends_on:
  hard: []
  soft:
    - session-start-progressive-disclosure for unfamiliar target projects
    - standards-and-spec-review when issue, changed files, or intended behavior are unclear
    - tdd when security-relevant behavior changed and needs regression proof
    - project-standards-calibration when security, dependency, logging, privacy, or config standards affect review
    - doc-sync when security assumptions, public behavior, config, or threat-model docs may drift
    - verification-before-completion before complete/clean/closeout-ready security claims
  fallback: If companion skills, git history, security docs, dependency metadata, or checks are unavailable, inspect minimal local evidence, state lower confidence, and report residual risk instead of speculative findings.
adapters:
  codex: usable
  claude-code: usable
  hermes: usable
  opencode: usable
  generic-agent: usable
---

# Code Security Review

## Purpose

Perform a focused static security review of a change or source area before closeout. The goal is to catch high-evidence exploitable risks: broken access control, unsafe trust-boundary crossings, data leaks, auth mistakes, injection paths, unsafe execution, unsafe configuration, secret exposure, and security-relevant reliability bugs.

This is a review gate, not a full security audit, penetration test, dependency audit, compliance review, standards review, or spec review. Absence of findings means no high-evidence issue was found in the reviewed scope; it does not prove the system is secure.

## Inputs

- User request and target-project root path.
- Fixed point for the review, such as a base commit, branch, tag, PR base, issue-start commit, or supplied patch.
- Changed files, diffs, commits, staged changes, unstaged changes, generated files, migrations, config changes, or source area under review.
- Originating issue, PRD, ticket, accepted plan, standards/spec review, TDD evidence, or user-stated intent when available.
- Relevant source files, tests, schemas, permissions, policies, routes, controllers, services, repositories, UI surfaces, CLI commands, jobs, deployment config, dependency manifests, lockfiles, and security docs.
- Project security model when present: roles, tenants, auth providers, data classification, secrets policy, sandbox policy, threat model, privacy constraints, compliance notes, or documented trusted boundaries.

## Workflow

1. Confirm the review scope:
   - Identify the target-project root and whether the review covers committed changes, staged changes, unstaged changes, a supplied patch, or a named source area.
   - Identify the fixed point. Prefer an explicit user-provided base, PR metadata, branch upstream, merge-base with the likely trunk branch, or the issue-start commit.
   - List changed files before reviewing. In git projects, use an equivalent of `git status --short`, `git diff --name-status <fixed-point>...HEAD`, and working-tree diff commands as appropriate for the requested scope.
   - Identify the originating issue, standards/spec review, PRD, ticket, or explicit request when it helps determine intended behavior.
   - Use non-mutating commands by default. Do not format, generate, migrate, rewrite, auto-fix, or upgrade dependencies during the review unless the user separately asks for implementation.

2. Build an evidence path before judging:
   - For each security-relevant change, TRACE a concrete path from reachable trigger or entry point to trust boundary to sensitive asset or dangerous sink.
   - A finding needs a reachable trigger, crossed trust boundary, missing or broken guard, affected asset or sink, and impact.
   - Read [Security Review Checklist](references/security-review-checklist.md) when the scope spans multiple surfaces or you need entry point, trust-boundary, asset, sink, risk-class, or severity examples.
   - Use the checklist as coverage guidance, not as proof.
   - Do not proceed from a vague concern to a finding. If no path can be traced, keep it as residual risk or a validation note.

3. Review high-risk classes:
   - ANALYZE access control, injection and parser paths, web or client exposure, data handling, persistence and policy, execution and platform behavior, dependency or supply-chain changes, and security-relevant reliability.
   - Use the local checklist to avoid missed classes in non-trivial reviews.
   - Report only when changed evidence proves a concrete exploitability path, concrete exposure, or vulnerable version path.

4. Validate context and false positives:
   - Report only findings with strong static evidence, roughly 80% confidence or higher.
   - Strong evidence means the review can name the reachable trigger, affected path, missing or broken guard, impacted asset, and why existing framework or project behavior does not neutralize the issue.
   - Cross-check framework defaults, type safety, existing middleware, validation, ownership checks, policies, transaction behavior, test fixtures, and deployment config before reporting.
   - If a pattern is suspicious but exploitability depends on missing facts, do not promote it to a finding. Record the missing validation under residual risk.
   - If validation needs runtime access, production-like config, captured logs, request traces, or human interaction, ask for that artifact or permission for a safe validation environment instead of guessing.
   - If static evidence proves a dangerous flaw but one external fact could change severity, report it at the lower defensible severity and include `[CONTEXT NEEDED]` with the exact validation needed.
   - Remove duplicate findings. When multiple paths share one root cause, report one finding with representative evidence and affected paths.

5. Classify severity:
   - Classify conservatively: `CRITICAL` for proven systemic, cross-user, cross-tenant, destructive, or code-execution compromise; `HIGH` for exploitable leak, escalation, policy bypass, sensitive token exposure, or repeatable integrity abuse; `MEDIUM` for bounded exploitability, dangerous patterns missing one external fact, or triggerable integrity or availability harm; `LOW` for limited posture, defense-in-depth, or future-risk issues tied to the reviewed path.
   - Use the local checklist for severity examples when classification is uncertain.
   - Omit `LOW` findings unless the user asked for broad scanning or the issue is directly tied to a significant reviewed path.

6. Report and route next work:
   - Keep this review separate from standards/spec review. Do not report style, naming, test coverage, architecture, or unrequested-scope concerns unless they directly create exploitable risk.
   - Include precise affected paths and line references when possible.
   - Include CWE or OWASP labels only when they fit confidently.
   - If web access is available and the label matters for reviewer clarity, verify the label against the optional references below.
   - If no exact label is known, use a plain vulnerability category instead of inventing an ID.
   - Recommend concrete remediation that matches the project architecture and framework defaults.
   - State assumptions, skipped checks, unavailable evidence, and residual risk.
   - Recommend implementation fixes for findings, `doc-sync` for changed security assumptions or public docs, and a fuller audit only when the reviewed scope leaves material unexamined risk.
   - Use `verification-before-completion` before claiming no high-evidence findings, review completion, security-review readiness, or closeout readiness; for draft reviews or best-effort scans, verify only the claim being made and state residual risk.

## Output Contract

Return a compact review shaped like this:

```markdown
## Review Scope

- Fixed point: <ref/commit/source and confidence>
- Changed files: <paths or summary>
- Review surface: <auth, data, config, dependencies, execution, storage, UI, or other areas>
- Evidence inspected: <files, commands, docs, diffs, assumptions>
- Coverage note: Static review gate only; not full audit coverage.

## Trust-Boundary Map

- Entry points: <paths, routes, commands, jobs, policies, or "none found in scope">
- Sensitive assets: <data, secrets, permissions, privileged operations, or "none found in scope">
- Dangerous sinks: <DB, shell, HTML, network, storage, logs, analytics, config, or "none found in scope">
- Existing guards: <middleware, validation, policies, framework defaults, tests, or "not verified">

## Security Findings

- <No high-evidence security findings detected in the reviewed scope, or one finding per bullet>
  - Severity: <CRITICAL, HIGH, MEDIUM, or LOW>
  - Affected path: <path and lines when available>
  - Category: <CWE/OWASP label when known, or concise vulnerability class>
  - Evidence: <specific source evidence proving the path>
  - Impact: <what an attacker or failure mode can do>
  - Recommended fix: <specific remediation>
  - Confidence: <high or medium, with a short reason>
  - False-positive control: <why existing context does not neutralize it, or exact context needed>

## Assumptions And Residual Risk

- <skipped files, unavailable fixed point, missing runtime config, unverified policies, dependency audit gaps, or lower-confidence concerns not reported as findings>

## Next Step

- <fix findings, doc-sync, fuller audit, commit-message, handoff, or none>
```

When no findings exist, still include the review scope, trust-boundary map, explicit no-findings statement, assumptions or residual risk, and the coverage note.

## Delegation

Main owns scope selection, trust-boundary judgment, finding classification, false-positive filtering, and user communication.

Delegate only bounded evidence or review passes: identify changed files/fixed point/manifests, map entry points/privileged operations/assets for one area, check one concrete auth/isolation/exposure/injection/execution/config path, validate a candidate finding, or summarize relevant security docs, policies, permissions, and framework defaults.

Require `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`; paths inspected; commands run or skipped; evidence with source paths and line refs when possible; assumptions, confidence, residual risk; and candidate findings with severity, impact, fix, and false-positive notes.

Status handling: `DONE` integrates high-evidence findings or no-finding coverage; `DONE_WITH_CONCERNS` requires review of exploitability, false-positive control, severity, scope, or unverified trust boundaries before reporting; `NEEDS_CONTEXT` gets the missing diff, fixed point, policy, route, config, dependency, or runtime assumption before re-dispatch; `BLOCKED` narrows the trust path, splits the review, changes verification route/model/tooling, or escalates.

If subagents are unavailable, run the same work sequentially with a narrower context budget.

## Guardrails

- Do not claim full security audit coverage, penetration-test coverage, compliance signoff, or absence of vulnerabilities.
- Do not report speculative vulnerabilities. Without a concrete trigger, boundary, missing guard, affected asset, and impact, record residual risk instead.
- Do not mix standards/spec findings into this review. Route missed requirements, unrequested scope, style, naming, and local convention issues to `standards-and-spec-review`.
- Do not rely solely on automated scanners, grep hits, dependency warnings, or pattern matching. Treat tools as triage; verify the execution path before reporting.
- Do not run mutating commands such as formatters, generators, migrations, dependency upgrades, auto-fixers, exploit scripts against live systems, or destructive proof-of-concept actions unless the user explicitly asks for implementation and approves the risk.
- Do not copy secrets, tokens, private user data, customer data, or sensitive logs into the report. Identify the path and exposure class without repeating the secret.
- Do not invent CWE, OWASP, or CVE labels. Use `Category` when an exact identifier is not necessary or not known.
- Do not treat missing project security docs, absent tests, or no dependency audit tooling as findings by themselves. Report them as residual risk unless they create a proven exploitable path.
- Do not broaden into architecture redesign, dependency modernization, doc-sync, commit writing, or handoff unless the user separately requests that work.
- Do not include private notes, ignored local scratch files, credentials, client data, sensitive personal context, or real user data in review output.
- Do not require this source repo's root docs after installation. The skill may rely only on its own folder files and target-project evidence.

## References

This skill is self-contained after installation. The local checklist is packaged with the skill; external references are optional lookup aids, not runtime dependencies.

- Local support file, read at the workflow gate above: [Security Review Checklist](references/security-review-checklist.md).
- [MITRE CWE List](https://cwe.mitre.org/data/index.html) - use for CWE IDs and weakness definitions when an exact CWE label matters.
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/Glossary.html) - use for practical security topic guidance and remediation context.
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/) - use for broad web-application risk categories when they clarify a finding.
