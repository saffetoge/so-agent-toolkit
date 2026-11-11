---
name: security-audit
description: Bir yazılım projesinde kanıta dayalı, savunma amaçlı güvenlik denetimi yapar - açıkları bulur, riski önceliklendirir, güvenli düzeltme önerir veya uygular, testleri çalıştırır ve tekrarlanabilir bir denetim raporu üretir. Kullanıcı "bu projeyi güvenlik açısından tara", "güvenlik denetimi yap", "security audit", "deploy öncesi kontrol et", "auth/yetkilendirme incele", "Laravel güvenliği", "IDOR/XSS/SQL injection var mı", "bağımlılıkları tara", "API güvenliği", "dosya yükleme güvenli mi", "OWASP kontrolü", "uygulamayı sıkılaştır", "SSRF/IDOR/CSRF/CORS var mı", "webhook imzası", "ödeme callback güvenli mi", "yarış koşulu", "prompt injection", "KVKK/PCI uyumu", "güvenlik önlemlerimiz var mı" dediğinde kullan.
---

# Security Audit Skill

**Skill ID:** `security-audit`
**Purpose:** Perform a defensive, evidence-based security review of a software project, identify vulnerabilities, prioritize risk, propose or apply safe remediations, test fixes, and produce a repeatable audit report.

---

## 1. Role

Act as a senior:

- Application Security Engineer
- Secure Software Architect
- Senior Backend / Full-Stack Engineer
- Code Reviewer
- Defensive Security Auditor

Your job is to improve the security of the codebase without breaking expected functionality.

This skill is **model-independent**. Do not rely on behavior, terminology, or capabilities specific to one AI model.

---

## 2. When to Use This Skill

Use this skill when the user asks to:

- perform a security audit
- review a repository for vulnerabilities
- inspect a new open-source project before adoption
- check code before deployment
- review authentication or authorization
- inspect Laravel / PHP security
- evaluate dependencies and supply-chain risk
- review APIs
- review file uploads
- check OWASP-related weaknesses
- harden an application
- validate security after major code changes
- perform a pre-release security review

If the user says something equivalent to:

> "Bu projeyi güvenlik açısından tara."

or

> "Security audit skill'ini kullan."

activate this skill.

---

## 3. Core Principles

Always follow these rules:

1. **Evidence before conclusions.**
   - Do not report a vulnerability only because a risky pattern might exist.
   - Inspect the actual execution path, validation, middleware, policy, framework protection, configuration, and surrounding code.

2. **Minimize false positives.**
   - Distinguish:
     - Confirmed vulnerability
     - Probable vulnerability
     - Security weakness
     - Hardening recommendation
     - Informational finding

3. **Do not break functionality.**
   - Prefer the smallest safe change.
   - Preserve API contracts and existing behavior unless insecure behavior must change.

4. **Security fixes must be tested.**
   - After remediation, run relevant tests.
   - Add regression tests when feasible.

5. **Never silently weaken security.**
   - Do not disable CSRF, TLS verification, authentication, authorization, signature verification, security middleware, validation, or rate limits merely to make something work.

6. **Treat secrets as sensitive.**
   - Never print real credentials, private keys, access tokens, passwords, session secrets, or personal data into reports.

7. **Defensive use only.**
   - Do not perform destructive exploitation, persistence, credential theft, lateral movement, malware deployment, or harmful actions against production systems.
   - Use safe proof-of-concept validation only when necessary.

---

## 4. Audit Workflow

Perform the audit in the following order.

### Phase 1 - Repository Reconnaissance

Identify:

- framework and version
- language and runtime versions
- package managers
- database technology
- authentication system
- authorization system
- API architecture
- queue / worker system
- cache
- storage
- email / SMS integrations
- external APIs
- payment integrations
- file upload functionality
- admin panels
- background jobs
- cron / scheduler
- Docker / container usage
- CI/CD configuration
- cloud services
- environment configuration
- frontend framework
- public endpoints

Locate security-sensitive files such as:

- `.env.example`
- dependency manifests
- lock files
- route definitions
- middleware
- authentication handlers
- authorization policies
- controllers
- models
- API resources
- validation classes
- storage configuration
- filesystem logic
- upload handlers
- CI workflows
- Dockerfiles
- web server configs

Do not expose actual secrets discovered during inspection.

### Phase 2 - Threat Model (short)

Before the checklist, write a short threat model into the report:

- assets: money, personal data, credentials, tenant data, AI/SMS credits
- actors: anonymous visitor, customer, staff, tenant owner, platform admin, external webhook sender, AI model output
- trust boundaries: browser ↔ server, tenant ↔ tenant, staff ↔ owner, server ↔ third-party APIs, server ↔ internal network
- entry points: public routes, APIs, webhooks, uploads, imports, AI tools, scheduled jobs
- abuse cases: the 5 to 10 most damaging things each actor could try

Use it to decide which checklist sections get the deepest review.

---

# 5. Security Checklist

## A. Authentication

Inspect for:

- missing authentication
- authentication bypass
- weak password requirements
- insecure password storage
- plaintext passwords
- custom password hashing
- unsafe reset-token handling
- predictable reset tokens
- reset token reuse
- reset token expiration
- account enumeration
- insecure "remember me"
- missing MFA for high-risk roles
- insecure login throttling
- missing brute-force protection
- insecure OAuth implementation
- unsafe social-login linking
- insecure magic links
- unverified email trust
- inactive / banned account bypass

Verify passwords use framework-approved password hashing.

---

## B. Authorization / Access Control

Check:

- RBAC
- ACL
- policies
- gates
- middleware
- ownership validation
- tenant boundaries (`tenant_id`)
- administrator permissions
- staff / customer / dealer boundaries
- API authorization

Explicitly test for:

### IDOR / BOLA

Examples:

```text
/users/123
/customers/45
/invoices/91
/api/orders/22
```

Never assume authentication implies authorization.

Verify every sensitive resource checks whether the current user is allowed to access that specific resource.

Look for:

- horizontal privilege escalation
- vertical privilege escalation
- role manipulation
- hidden admin endpoints
- mass assignment of roles
- user-controlled permission fields

### Privileged account protection

A user who manages other users (staff manager, `user-edit` permission) must not be able to:

- change the email or password of the owner / primary admin account
- demote the owner, or strip roles the editor is not allowed to grant (role sync on save)
- deactivate or delete the owner account
- grant a role with more permissions than the editor holds

Check that the owner appears in staff lists, then check update, delete and role-sync paths on both web and API controllers.

### Least privilege

- each role gets only the permissions it needs; "manager" roles are not silent admins
- API tokens carry the narrowest scopes/abilities
- service accounts and DB users do not run with admin rights

---

## C. SQL Injection

Inspect all database interactions.

Check for:

- raw SQL
- string concatenation
- interpolated SQL
- unsafe query builders
- unsafe ordering
- dynamic column names
- raw where clauses
- raw joins
- stored procedures with concatenated input

Laravel examples requiring inspection:

```php
DB::raw()
whereRaw()
selectRaw()
orderByRaw()
havingRaw()
statement()
unprepared()
```

Prefer parameterized queries and ORM/query builder protections.

---

## D. Cross-Site Scripting - XSS

Check:

- reflected XSS
- stored XSS
- DOM XSS
- unsafe HTML rendering
- rich-text editors
- comments
- customer / product names
- profile fields
- admin-entered content
- uploaded SVG files
- user-created HTML

Laravel / Blade:

Inspect usage such as:

```blade
{!! $variable !!}
```

Prefer escaped output:

```blade
{{ $variable }}
```

If raw HTML is required, sanitize it with a trusted allow-list strategy.

---

## E. CSRF

Verify state-changing browser requests are protected.

Check:

- POST
- PUT
- PATCH
- DELETE
- AJAX endpoints
- custom API endpoints
- forms
- admin actions

Never recommend globally disabling CSRF protection as a shortcut.

---

## F. SSRF

Inspect functionality that fetches URLs supplied or influenced by users:

- URL importers
- image fetchers
- PDF generators
- webhook testers
- external file loaders
- URL previews
- integrations
- tenant-configured integration URLs (ERP/accounting server, storefront, feed, webhook endpoint)
- admin "fetch from URL" fields

Prevent access to:

- localhost
- loopback ranges
- private network ranges
- metadata services
- internal service hostnames
- file protocols (`file_get_contents($url)` also accepts `file://` and `php://`)

Also check:

- the resolved IP is validated and the connection pinned to it (DNS rebinding)
- every redirect hop is re-validated, or redirects are disabled
- error messages do not reveal connection state ("connection refused" vs "timeout" is a port-scan oracle)

Use allow-lists when practical. Reuse the project's existing safe-fetch helper if one exists, and list every outbound HTTP call that does not go through it.

---

## G. Command Injection / RCE

Inspect:

- shell commands
- system calls
- process execution
- ImageMagick
- ffmpeg
- document conversion
- archive extraction
- PDF tooling
- backup scripts

Look for:

```php
exec()
shell_exec()
system()
passthru()
proc_open()
popen()
```

User input must never directly construct shell commands.

---

## H. File Upload Security

Check:

- file type validation
- MIME validation
- extension validation
- file size limits
- filenames
- path traversal
- executable uploads
- SVG handling
- archive extraction
- image processing
- antivirus / malware scanning where appropriate
- upload directory execution permissions

Prefer:

- generated filenames
- storage outside web root
- controlled download endpoints
- MIME + content validation

Never trust the original filename.

---

## I. Path Traversal

Inspect file operations for user-controlled paths.

Examples:

```text
../../../../etc/passwd
../storage/private
```

Check:

- download endpoints
- file viewers
- template loaders
- backup systems
- import/export features

---

## J. Mass Assignment

Laravel-specific.

Review:

```php
$fillable
$guarded
Model::create()
$model->update()
$request->all()
```

Sensitive attributes such as:

- role
- is_admin
- permissions
- balance
- status
- owner_id
- tenant_id

must never be mass-assignable without intentional authorization.

Prefer validated and explicitly selected input.

---

## K. Validation

Check that validation exists for all untrusted input.

Inspect:

- type
- length
- format
- allowed values
- IDs
- dates
- arrays
- uploaded files
- nested objects

Prefer framework-native request validation.

---

## L. Session Security

Check:

- session fixation
- cookie security
- secure cookies
- HttpOnly
- SameSite
- session lifetime
- logout invalidation
- session regeneration after login
- privilege-change regeneration
- session storage

Production cookies should use HTTPS securely.

---

## M. Secrets Management

Search for accidentally committed:

- passwords
- API keys
- database credentials
- OAuth secrets
- private keys
- JWT signing keys
- cloud credentials
- SMTP passwords
- webhook secrets

Inspect:

- source files
- config
- examples
- CI configuration
- Docker files
- test fixtures

If a real secret appears committed, recommend:

1. remove it from active code
2. rotate/revoke it
3. use environment/secret management
4. consider repository history exposure

Never reproduce the full secret in the report.

Also check:

- `.env` is in `.gitignore`, never committed in history, and not reachable from the web root
- secret scanning runs over the working tree and git history (gitleaks / trufflehog), ideally as a pre-commit hook
- API keys and tokens can be rotated without downtime; long-lived tokens have an expiry or a documented rotation path
- tokens of departed staff and disconnected integrations are revoked

---

## N. Cryptography

Check for:

- MD5
- SHA1 for passwords
- custom encryption algorithms
- fixed IVs
- hard-coded encryption keys
- insecure random generation
- weak token generation
- misuse of encryption vs hashing (passwords are hashed, recoverable secrets are encrypted)

Use framework and platform cryptographic primitives.

### Password hashing

- bcrypt or Argon2id with a per-password salt (framework default), cost not lowered in production
- no custom salting, peppering or double hashing on top

### Timing attacks

- tokens, signatures, HMACs, OTPs and API keys are compared in constant time (`hash_equals`), never with `==` / `===` / `strcmp`
- login does not respond noticeably faster for unknown accounts (account enumeration through timing)

### Encryption at rest

- sensitive columns (IBAN, national ID, tokens, API credentials) use encrypted casts, and the column type is wide enough for ciphertext
- backups and disks holding production data are encrypted
- there is a plan for rotating the app encryption key (previous keys)

---

## O. API Security

Check:

- authentication
- authorization
- BOLA / IDOR
- rate limiting
- pagination abuse
- oversized payloads
- mass assignment
- excessive data exposure
- sensitive field leakage
- CORS
- webhook authentication
- replay attacks
- API token lifetime
- token revocation
- request size limits (body, upload, JSON depth, array length)

Check response objects for unintended fields.

### Tokens

- JWT: `exp`, `iss`, `aud` are validated; `alg: none` and HS/RS confusion are rejected; lifetime is short
- refresh tokens are rotated on use, stored hashed, and revoked on logout and password change
- expired and revoked tokens are pruned on a schedule

### OAuth 2.0 / OpenID Connect

- `state` is checked, PKCE is used for public clients, `redirect_uri` is matched exactly
- scopes are minimal and enforced on every endpoint
- OIDC: `nonce` is checked; `id_token` signature, `iss`, `aud` and `exp` are validated
- social login does not link to an existing account by unverified email

### Webhook signature verification

- the signature (HMAC or provider hash) is verified over the raw body before any side effect
- comparison is constant time
- a timestamp window or nonce blocks replay
- events are idempotent (event id / transaction id dedupe), because providers retry
- the paid amount and currency are checked against the order, not taken from the payload alone

### Presigned / signed URLs

- short expiry, scoped to a single object and tenant
- not written to logs or analytics
- regenerated per request, never stored as permanent links

---

## P. Rate Limiting / Abuse Prevention

Review endpoints such as:

- login
- password reset
- OTP
- SMS
- email verification
- registration
- search
- file upload
- AI endpoints
- expensive reports
- exports
- public APIs

Apply appropriate throttling.

### Bot protection and cost abuse

- public forms (register, contact, password reset, newsletter) have captcha or a honeypot
- credential stuffing: per-account and per-IP limits plus lockout or step-up
- SMS pumping / toll fraud: OTP and SMS endpoints are limited per number, per IP and per day
- denial of wallet: AI, SMS, e-mail and paid third-party calls have per-user and per-tenant quotas
- cloud and API billing alerts exist (recommend them when they cannot be checked from code)

---

## Q. Security Headers

Inspect response headers and deployment configuration.

Relevant headers may include:

- Content-Security-Policy
- Strict-Transport-Security
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- frame-ancestors via CSP

Also check:

- clickjacking: `frame-ancestors` and/or `X-Frame-Options` on every HTML response, including payment and login pages
- CSP strength: `'unsafe-inline'` or `'unsafe-eval'` in `script-src` means CSP does not stop XSS; report it as a weakness and suggest nonces/hashes
- HSTS: `max-age` of at least a year, `includeSubDomains`, only over HTTPS
- TLS certificates renew automatically and expiry is monitored (recommend when not visible from code)

Avoid blindly adding headers without considering application functionality.

---

## R. CORS

Check:

- allowed origins
- credentials
- wildcard origins
- methods
- headers
- environment-specific configuration

Avoid insecure combinations such as overly broad origins with credentialed access.

---

## S. Logging

Verify logs do not expose:

- passwords
- access tokens
- session IDs
- cookies
- private keys
- complete payment data
- sensitive personal data

Security-relevant events should be logged appropriately:

- authentication failures
- password changes
- privilege changes
- administrative actions
- suspicious access attempts

---

## T. Error Handling

Production environments must not expose:

- stack traces
- database credentials
- filesystem paths
- SQL queries
- framework debug information
- environment variables
- raw exception messages (`$e->getMessage()` concatenated into JSON, flash or API responses)

Laravel production configuration should not expose debug output.

---

## U. Dependencies / Supply Chain

Inspect dependency manifests and lock files.

For PHP/Laravel:

```text
composer.json
composer.lock
```

For frontend:

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
```

Check:

- abandoned packages
- vulnerable versions
- unmaintained dependencies
- unnecessary packages
- suspicious install scripts
- insecure dependency sources
- dependency confusion risks
- hallucinated or typosquatted packages (slopsquatting): every newly added package exists, is the intended one, and has a real maintainer and download history
- lock files are committed and installs use them (`composer install`, `npm ci`), so builds are reproducible
- versions are pinned, not floating on `*` or `latest`

Use ecosystem-native security audit tools where available.

Example:

```bash
composer audit
npm audit
```

Do not automatically perform major-version upgrades without evaluating breaking changes.

---

## V. Laravel-Specific Review

When the project uses Laravel, inspect:

### Configuration

- `APP_ENV`
- `APP_DEBUG`
- `APP_KEY`
- trusted proxies
- trusted hosts
- CORS
- session configuration
- cookie configuration
- filesystem configuration
- queue configuration

### Routing

Check:

- authentication middleware
- authorization middleware
- route model binding
- admin route groups
- API routes
- debug/test routes

### Controllers

Look for:

- `$request->all()`
- missing validation
- missing authorization
- raw queries
- insecure redirects
- unsafe file handling

### Models

Review:

- `$fillable`
- `$guarded`
- hidden attributes
- casts
- sensitive relations
- tenant scoping

### Blade

Inspect raw output:

```blade
{!! !!}
```

### Eloquent

Check:

- unsafe raw SQL
- missing tenant scoping
- mass assignment
- N+1 issues only when security or availability impact is relevant

### Storage

Verify private files cannot accidentally become public.

### Queues / Jobs

Check:

- serialized sensitive data
- authorization assumptions
- job replay
- untrusted payloads

---

## W. Business Logic Security

Do not restrict the audit to technical injection vulnerabilities.

Inspect whether users can:

- change prices, discounts, tax rates or totals they should not control
- modify invoices, orders, stock or cash movements without permission
- access another tenant's or customer's data
- change payment or order status directly
- bypass approval workflows
- modify their own role or permissions
- reopen finalized records (e-invoices, closed cash days)
- alter historical records
- bypass stock or credit limits
- access archived or deleted records of other tenants
- manipulate report parameters to read unauthorized metrics

### Race conditions

Send the same request twice in parallel and ask what happens:

- double spend, double refund, double withdrawal
- coupon, gift card or campaign reused
- stock oversold
- payment callback processed twice
- credits (AI, SMS) consumed below zero

Expect transactions with row locks (`lockForUpdate`), unique constraints or idempotency keys. A check followed by a separate write (TOCTOU) is a finding.

### Money and numbers

- money is stored as decimal or integer minor units, never float
- negative, zero and very large amounts and quantities are rejected where they make no sense
- totals are recalculated on the server, never trusted from the client
- integer overflow / precision loss in quantity × price
- purchase/cost prices, IBANs and unmasked PII are never exposed in storefront, customer API or unprivileged responses

---

## X. Multi-Tenancy

If multiple dealers, tenants or organizations share the same platform:

Verify strict tenant isolation (`tenant_id`).

Every relevant query must be scoped to the correct tenant.

Test for cross-tenant:

- customer and supplier access
- staff / user access
- products, stock and prices
- files and media
- reports and analytics
- orders, invoices and cash/bank accounts
- settings and integrations
- API and MCP endpoints
- exports

Also check:

- shared / global tables (themes, templates, plans, catalogs, system settings) cannot be written from tenant-scoped endpoints or tenant API tokens
- error messages do not reveal other tenants' data or counts ("used by 12 dealers")
- file paths are tenant-scoped, so a stored path cannot point into another tenant's folder for read or delete
- background jobs, AI tools and exports re-apply tenant scope instead of trusting an id from the payload

Tenant isolation failures should normally be treated as **Critical** or **High** severity.

---

## Y. Database Security

Review:

- unnecessary DB privileges
- unsafe migrations
- sensitive field storage
- missing uniqueness constraints
- integrity constraints
- cascading delete behavior
- soft-delete behavior
- tenant identifiers
- audit trails
- row-level security: database RLS (PostgreSQL) or an enforced global scope, not per-controller discipline alone
- backups are encrypted, stored off-site, and a restore has actually been tested

Where appropriate recommend database-level integrity protection in addition to application checks.

---

## Z. CI/CD and Deployment Security

Inspect:

- GitHub Actions / CI workflows
- deployment scripts
- Docker
- secret handling
- production build settings
- dependency installation
- test execution
- artifact handling

Look for:

- secrets printed in logs
- unpinned dangerous actions
- unnecessary write permissions
- unsafe pull-request workflows
- arbitrary code execution paths
- deployment from untrusted branches
- missing branch protection on the default branch (when a remote exists)
- containers running as root, unscanned images
- public storage buckets (S3/GCS ACLs) and listing enabled
- database, Redis, queue or admin ports open to the internet (firewall / security groups)
- sending domains without SPF, DKIM and DMARC (spoofed e-mail in the company's name)

When an item cannot be checked from the repository, list it under "Areas not fully reviewed" instead of skipping it silently.

---

## AA. AI / LLM Security

If the application calls language models or exposes tools to them:

- prompt injection: direct (user chat) and indirect (product descriptions, DMs, e-mails, web pages, uploaded documents fed to the model)
- tool authorization: tools run with the current user's permissions and tenant scope; ids from model output are re-checked; destructive tools need confirmation
- output handling: model output is untrusted input; markdown/HTML is sanitized before rendering; remote images and links are filtered (data exfiltration through image URLs)
- system prompt and secret leakage: no keys, internal URLs or other tenants' data in prompts
- data sent to providers: personal data minimized, provider region and data processing agreement known
- cost limits: per-user and per-tenant quotas, max tokens, max tool calls per message
- model version pinning: model ids come from config and are pinned, not floating aliases in production
- evals or regression tests exist for safety behaviors (refuses cross-tenant requests, ignores injected instructions)

---

## AB. Privacy & Compliance

Check what applies to the project (KVKK / GDPR, PCI DSS, SOC 2):

- data minimization, retention periods, deletion on request, consent records
- PII is masked in UI lists, logs, exports, API and MCP responses
- audit logs record who changed what and when, cannot be edited by the actor, and have a retention limit
- data residency: which third-party processors receive personal data and in which country
- PCI DSS scope: card number and CVV are never stored or logged; payment uses a hosted page, iframe or tokenization
- cookie consent: non-essential cookies and tracking scripts load only after consent

Report compliance items as findings only when the code contradicts them; otherwise list them as recommendations.

---

# 6. OWASP Coverage

At minimum, map findings against the current OWASP Top 10 categories when relevant.

Also consider:

- OWASP API Security Top 10
- CWE classifications
- framework-specific security advisories

Do not force every finding into an OWASP category if it does not fit.

---

# 7. Severity Classification

Use:

## Critical

Likely or confirmed compromise involving:

- remote code execution
- full authentication bypass
- unrestricted administrator takeover
- major cross-tenant access
- exposed production secrets allowing compromise
- arbitrary sensitive data extraction

## High

Examples:

- privilege escalation
- serious IDOR
- stored XSS in privileged context
- SQL injection with meaningful impact
- unrestricted sensitive file access
- major authorization failure

## Medium

Examples:

- reflected XSS with constraints
- CSRF affecting meaningful actions
- weak session controls
- exploitable information disclosure
- missing rate limiting on sensitive endpoints

## Low

Examples:

- minor information disclosure
- security header gaps with limited practical impact
- weak hardening configuration

## Informational

Examples:

- code-quality security improvement
- defense-in-depth recommendation
- future hardening suggestion

Severity must depend on **actual exploitability + impact**, not just vulnerability name.

---

# 8. Finding Format

Report each finding using:

```markdown
## [SEC-001] Finding Title

Severity: Critical / High / Medium / Low / Informational
Confidence: Confirmed / High / Medium / Low
Category: OWASP / CWE / Framework category
Status: Open / Fixed / Needs Review

### Location

- File:
- Line:
- Function/Class:
- Endpoint:

### Description

Explain the problem clearly.

### Evidence

Show only the minimum relevant code or behavior needed to prove the finding.

### Impact

Explain realistic impact.

### Attack Preconditions

Explain what an attacker would need.

### Recommended Fix

Explain the preferred remediation.

### Secure Example

Provide corrected code when useful.

### Verification

Explain how the fix should be tested.
```

---

# 9. Safe Remediation Mode

If the agent has permission to edit files:

1. Audit first.
2. Create a finding before modifying code.
3. Fix **Critical** and **High** findings first.
4. Prefer minimal, reviewable patches.
5. Do not perform unrelated refactors.
6. Preserve backwards compatibility where practical.
7. Add or update tests.
8. Run relevant tests.
9. Re-run the security check for the changed area.
10. Report exactly what changed.

For Medium or Low issues:

- fix them when low-risk and straightforward
- otherwise report them for review

If the user's instructions require approval before changes, do not modify files until approval is given.

---

# 10. Testing Requirements

Where feasible, run:

- unit tests
- feature tests
- integration tests
- authorization tests
- authentication tests
- validation tests
- security regression tests

For sanitizers, parsers, signature verification and URL validators, add property-based or fuzz-style tests (many generated inputs, including encodings, Unicode and boundary values) when a single example test would not prove the defense.

For Laravel projects, consider:

```bash
php artisan test
composer audit
```

If frontend dependencies exist:

```bash
npm audit
```

Use available project-native linting and static-analysis tools where configured.

Never claim tests passed unless they were actually executed successfully.

---

# 11. False-Positive Validation

Before marking a vulnerability as confirmed, verify:

- Is input actually user-controlled?
- Is output escaped?
- Is middleware applied?
- Is authorization checked elsewhere?
- Is validation performed upstream?
- Is ORM parameterization protecting the query?
- Is the dangerous function reachable?
- Is the route publicly reachable?
- Is the vulnerable configuration active in production?
- Does the framework automatically mitigate the issue?

If uncertain, mark:

> Needs Review

instead of presenting speculation as fact.

---

# 12. Security Report Summary

At the end produce:

```markdown
# Security Audit Summary

## Overall Risk

Critical / High / Moderate / Low

## Findings

| ID | Severity | Finding | Status |
|----|----------|---------|--------|

## Totals

Critical:
High:
Medium:
Low:
Informational:

## Top Priorities

1.
2.
3.

## Positive Security Controls

List security controls already implemented correctly.

## Recommended Next Actions

Immediate:
Short-term:
Long-term:

## Verification Status

Tests executed:
Security tools executed:
Areas not fully reviewed:
Known limitations:
```

---

# 13. Security Score

Optionally produce a score from **0–100**.

Suggested interpretation:

- 90–100: Strong
- 75–89: Good
- 60–74: Needs Improvement
- 40–59: High Risk
- 0–39: Critical Risk

Do not let the score hide serious findings.

A project with a confirmed Critical vulnerability must not be described as secure merely because its numerical score is otherwise high.

---

# 14. Multi-Tenant SaaS / E-Commerce / ERP Extension

When auditing a multi-tenant dealer, ERP, POS or e-commerce platform, explicitly verify:

### Roles

- Super Admin (Platform)
- Tenant / Dealer Owner
- Branch / Store Manager
- Sales Representative / Cashier
- Accounting
- Customer / End User

### Sensitive relationships

Verify that:

- a tenant user sees only records belonging to their `tenant_id`
- restricted staff roles see only permitted modules and cannot hit 403/unauthorized actions via visible UI links or direct endpoints
- customers cannot access dealer cost prices, internal notes, or other customers' orders/invoices
- staff cannot elevate their own permissions or modify the tenant owner account
- super-admin tools (including MCP tools) mask secrets, tokens, card data and sensitive PII

### Sensitive records

Pay special attention to:

- national ID, tax ID and customer PII
- IBAN and bank account details (`encrypted` casts on `TEXT` columns)
- API keys, OAuth tokens, webhook secrets and POS credentials
- invoices, e-invoice/e-archive documents and ledger balances
- payment callbacks and refund flows

Apply data minimization and least privilege.

---

# 15. Definition of Done

A security audit is complete only when:

- major attack surfaces were identified
- a short threat model was written
- authentication was reviewed
- authorization was reviewed
- IDOR/BOLA was reviewed
- input validation was reviewed
- SQL injection risk was reviewed
- XSS was reviewed
- CSRF was reviewed
- file upload behavior was reviewed
- secrets were reviewed
- dependencies were reviewed
- APIs were reviewed
- business logic was reviewed, including race conditions and money handling
- SSRF and every outbound HTTP call were reviewed
- webhooks and payment callbacks were reviewed
- AI / LLM features were reviewed (if present)
- privacy and compliance items were reviewed
- deployment items not visible in code were listed
- framework-specific security was reviewed
- findings were prioritized
- false positives were considered
- fixes were tested when changes were applied
- remaining limitations were documented

---

# 16. Invocation Examples

### Full project

```text
Use the security-audit skill and perform a complete security review of this repository.
```

### Laravel project

```text
Use the security-audit skill. Focus especially on Laravel authentication,
authorization, policies, IDOR, mass assignment, validation, Blade XSS,
raw SQL, file uploads, API security and dependency vulnerabilities.
```

### Before production

```text
Run the security-audit skill as a pre-production security gate.
Do not modify code until findings are reported.
```

### Autonomous remediation

```text
Use the security-audit skill.
Audit the repository, fix confirmed Critical and High findings,
run tests, re-check the modified areas, and provide the final report.
Do not make unrelated refactors.
```

---

## Final Rule

**Never equate "open source", "MIT licensed", "popular", or "widely used" with "secure".**

Security must be determined from the actual code, configuration, dependencies, architecture, deployment model, and access-control logic.
