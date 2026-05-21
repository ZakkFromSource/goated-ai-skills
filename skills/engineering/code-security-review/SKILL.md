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
    - session-start-progressive-disclosure before reviewing an unfamiliar target project
    - standards-and-spec-review before this review when the originating issue, changed files, or intended behavior are unclear
    - tdd before this review when security-relevant behavior changed and should have regression proof
    - project-standards-calibration when local security, dependency, logging, privacy, or configuration standards affect the review
    - doc-sync after this review when security assumptions, public behavior, configuration, or threat-model docs may have drifted
    - verification-before-completion before claiming the security review is complete, clean, or ready for closeout
  fallback: If companion skills, git history, project security docs, dependency metadata, or runnable checks are unavailable, inspect the smallest relevant local evidence, state lower confidence, and report residual risk instead of speculative findings.
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
   - For each security-relevant change, trace a concrete path from entry point to trust boundary to sensitive asset or dangerous sink.
   - Entry points include HTTP routes, UI events, CLI arguments, background jobs, webhooks, RPCs, database policies, storage rules, realtime subscriptions, dependency hooks, file inputs, environment variables, and test or admin tools that can affect production behavior.
   - Trust boundaries include user to server, tenant to tenant, unauthenticated to authenticated, user to admin, client to database, service to service, local file to parser, dependency to app, and app to shell or network.
   - Sensitive assets include user data, tenant data, credentials, tokens, secrets, payment or billing state, audit logs, private files, permissions, admin actions, integrity-critical state, and availability-critical resources.
   - Dangerous sinks include database writes or reads, policy definitions, HTML or script rendering, command execution, file paths, network requests, deserialization, cryptography, logging, analytics, storage buckets, queues, and privileged APIs.
   - Do not proceed from a vague concern to a finding. If no path can be traced, keep it as residual risk or a validation note.

3. Review high-risk classes:
   - Broken access control, privilege escalation, IDOR, tenant isolation failures, auth bypass, confused deputy flows, forged identity, missing ownership checks, and unsafe admin/service-role use.
   - Injection paths including SQL, NoSQL, command, template, LDAP, path traversal, SSRF, unsafe redirects, unsafe deserialization, and parser confusion.
   - Web and client risks including XSS, CSRF, clickjacking-relevant config, insecure CORS, token exposure, unsafe storage, origin confusion, and user-controlled markup.
   - Data handling risks including secrets in source, logs, analytics, telemetry, error messages, caches, test fixtures, screenshots, generated artifacts, URLs, or client bundles.
   - Persistence and policy risks including permissive database policies, missing write checks, unsafe migrations, weak row ownership, insecure storage rules, public buckets, cache poisoning, replay under the wrong identity, and non-idempotent destructive operations.
   - Execution and platform risks including sandbox escapes, unsafe eval, dynamic imports from untrusted input, shelling out with user input, path joins outside the intended root, insecure temp files, weak crypto, insecure randomness, unsafe defaults, and production debug flags.
   - Dependency and supply-chain risks when the diff changes manifests, lockfiles, install scripts, build scripts, package sources, plugin loading, or CI secrets exposure. Report only when the changed evidence proves a concrete risk or vulnerable version path.
   - Security-relevant reliability risks such as race conditions, time-of-check/time-of-use gaps, resource leaks, missing cleanup, retry storms, or optimistic updates when they can cause data corruption, authorization drift, repeated privileged writes, or denial of service.

4. Validate context and false positives:
   - Report only findings with strong static evidence, roughly 80% confidence or higher.
   - Strong evidence means the review can name the reachable trigger, affected path, missing or broken guard, impacted asset, and why existing framework or project behavior does not neutralize the issue.
   - Cross-check framework defaults, type safety, existing middleware, validation, ownership checks, policies, transaction behavior, test fixtures, and deployment config before reporting.
   - If a pattern is suspicious but exploitability depends on missing facts, do not promote it to a finding. Record the missing validation under residual risk.
   - If validation needs runtime access, production-like config, captured logs, request traces, or human interaction, ask for that artifact or permission for a safe validation environment instead of guessing.
   - If static evidence proves a dangerous flaw but one external fact could change severity, report it at the lower defensible severity and include `[CONTEXT NEEDED]` with the exact validation needed.
   - Remove duplicate findings. When multiple paths share one root cause, report one finding with representative evidence and affected paths.

5. Classify severity:
   - `CRITICAL`: proven cross-user or cross-tenant data access, auth bypass, arbitrary code execution, secret exposure, destructive privileged action, payment or billing abuse, or production-wide compromise path.
   - `HIGH`: exploitable data leak, privilege escalation, stored XSS, SSRF to sensitive resources, unsafe service-role use, policy bypass, sensitive token exposure, or repeatable integrity abuse.
   - `MEDIUM`: bounded security flaw, missing context with a proven dangerous pattern, race condition or TOCTOU gap with security impact, partial policy gap, reflected XSS with constraints, or reliability bug that can be triggered to harm data integrity or availability.
   - `LOW`: limited-impact security posture issue, defense-in-depth gap, or future-risk pattern tied to a changed security-relevant path.
   - Omit `LOW` findings unless the user asked for broad bug scanning or the issue is directly tied to a significant reviewed path.

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

The main agent owns scope selection, trust-boundary judgment, finding classification, false-positive filtering, and user communication.

When subagents are available, use them only for bounded evidence gathering or independent review passes, such as:

- identifying changed files, fixed point, and dependency manifest changes;
- mapping entry points, privileged operations, and sensitive assets for one source area;
- checking auth, tenant isolation, data exposure, injection, unsafe execution, or config along one concrete path;
- verifying whether a candidate finding has enough evidence and belongs in security review instead of standards/spec review;
- summarizing project security docs, policies, permissions, or framework defaults relevant to one candidate issue.

Require every subagent result to include:

- `Status`: `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`;
- paths inspected;
- commands run or deliberately skipped;
- evidence found with source paths and line references when possible;
- assumptions, confidence, and residual risk;
- candidate findings with severity, impact, recommended fix, and false-positive notes.

Handle delegated status this way: `DONE` means integrate high-evidence findings or no-finding coverage into the security judgment; `DONE_WITH_CONCERNS` means inspect concerns about exploitability, false-positive control, severity, scope, or unverified trust boundaries before reporting; `NEEDS_CONTEXT` means provide the missing diff, fixed point, policy, route, config, dependency, or runtime assumption and re-dispatch; `BLOCKED` means narrow the trust path, split the review, choose a safer verification route, use stronger model/tooling, or escalate to the user.

If subagents are unavailable, perform the same work sequentially with a narrower context budget.

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
- Do not require this source repo's root docs after installation. The skill may rely only on its own instructions and target-project evidence.

## References

This skill is self-contained after installation. These external references are optional lookup aids, not runtime dependencies:

- [MITRE CWE List](https://cwe.mitre.org/data/index.html) - use for CWE IDs and weakness definitions when an exact CWE label matters.
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/Glossary.html) - use for practical security topic guidance and remediation context.
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/) - use for broad web-application risk categories when they clarify a finding.
