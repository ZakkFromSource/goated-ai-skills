# Security Review Checklist

Use this local checklist when a `code-security-review` pass spans multiple surfaces, has unfamiliar project vocabulary, or needs coverage guidance before finalizing findings. It is a discovery aid, not proof. Promote an item to a finding only when the parent skill's concrete-path and confidence gates are met.

## Evidence Path Vocabulary

Map each candidate issue through the smallest concrete path:

| Surface | Review examples |
| --- | --- |
| Entry points | HTTP routes, UI events, CLI arguments, background jobs, webhooks, RPCs, database policies, storage rules, realtime subscriptions, dependency hooks, file inputs, environment variables, and test or admin tools that can affect production behavior. |
| Trust boundaries | User to server, tenant to tenant, unauthenticated to authenticated, user to admin, client to database, service to service, local file to parser, dependency to app, and app to shell or network. |
| Sensitive assets | User data, tenant data, credentials, tokens, secrets, payment or billing state, audit logs, private files, permissions, admin actions, integrity-critical state, and availability-critical resources. |
| Dangerous sinks | Database writes or reads, policy definitions, HTML or script rendering, command execution, file paths, network requests, deserialization, cryptography, logging, analytics, storage buckets, queues, and privileged APIs. |

## High-Risk Classes

- Access control and identity: broken access control, privilege escalation, IDOR, tenant isolation failure, auth bypass, confused deputy flow, forged identity, missing ownership check, or unsafe admin/service-role use.
- Injection and parser paths: SQL, NoSQL, command, template, LDAP, path traversal, SSRF, unsafe redirect, unsafe deserialization, parser confusion, or user-controlled input reaching an interpreter.
- Web and client exposure: XSS, CSRF, clickjacking-relevant config, insecure CORS, token exposure, unsafe browser storage, origin confusion, or user-controlled markup.
- Data handling: secrets in source, logs, analytics, telemetry, error messages, caches, test fixtures, screenshots, generated artifacts, URLs, or client bundles.
- Persistence and policy: permissive database policies, missing write checks, unsafe migrations, weak row ownership, insecure storage rules, public buckets, cache poisoning, replay under the wrong identity, or non-idempotent destructive operations.
- Execution and platform: sandbox escape, unsafe eval, dynamic import from untrusted input, shelling out with user input, path joins outside the intended root, insecure temp files, weak crypto, insecure randomness, unsafe defaults, or production debug flags.
- Dependency and supply chain: manifest, lockfile, install script, build script, package source, plugin-loading, or CI-secret changes that prove a concrete risk or vulnerable version path.
- Security-relevant reliability: race condition, TOCTOU gap, resource leak, missing cleanup, retry storm, or optimistic update that can cause data corruption, authorization drift, repeated privileged writes, or denial of service.

## Severity Examples

- `CRITICAL`: proven cross-user or cross-tenant data access, auth bypass, arbitrary code execution, secret exposure, destructive privileged action, payment or billing abuse, or production-wide compromise path.
- `HIGH`: exploitable data leak, privilege escalation, stored XSS, SSRF to sensitive resources, unsafe service-role use, policy bypass, sensitive token exposure, or repeatable integrity abuse.
- `MEDIUM`: bounded security flaw, missing context with a proven dangerous pattern, race condition or TOCTOU gap with security impact, partial policy gap, reflected XSS with constraints, or reliability bug that can be triggered to harm data integrity or availability.
- `LOW`: limited-impact security posture issue, defense-in-depth gap, or future-risk pattern tied to a changed security-relevant path.

Omit `LOW` findings unless the user asked for broad bug scanning or the issue is directly tied to a significant reviewed path.
