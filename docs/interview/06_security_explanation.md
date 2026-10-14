# Interview Guide: 06. Security Practices & Defense in Depth

## What Security Practices are Implemented?
TrackIT implements defense-in-depth principles:
1. **Password Hashing:** Salted bcrypt with 12 rounds.
2. **SQL Injection Protection:** SQLAlchemy ORM parameterized statements.
3. **Input Sanitization:** Pydantic v2 boundary schema validation.
4. **Error Masking:** Global exception handler hides internal stack traces.
5. **CORS Hardening:** Whitelist of allowed origins.
6. **Audit Trail:** Immutable logging of security-critical mutations.
7. **Secret Hygiene:** Environment variable isolation without hardcoded keys in Git.

## Why are these practices critical?
In an enterprise IT service desk, tickets often contain sensitive internal operational details: server IP addresses, software version vulnerabilities, access credentials, and employee personal info. A vulnerability like SQL injection or an unauthenticated IDOR (Insecure Direct Object Reference) could allow an attacker to dump the entire company ticket database.

## How TrackIT Protects Against Common OWASP Top 10 Vulnerabilities:
* **Broken Access Control (OWASP #1):** Solved through independent backend RBAC. Even if an employee guesses the URL of another employee's ticket or sends a direct API call to `/api/v1/tickets/101`, `TicketService.get_ticket` verifies `ticket.created_by == current_user.id` and throws `403 FORBIDDEN`.
* **Cryptographic Failures (OWASP #2):** Bcrypt with individual salts prevents rainbow table matching. Strong secret keys protect JWT signatures.
* **Injection (OWASP #3):** Parameterized ORM queries prevent SQL injection.
* **Security Misconfiguration (OWASP #5):** Global error handlers catch unhandled exceptions and prevent leaking server paths, database credentials, or stack traces.

## Interview Questions & Answers

### Q: "How does TrackIT prevent Insecure Direct Object References (IDOR)?"
**Answer:** "An IDOR occurs when an application exposes a direct reference to an internal object (e.g. `GET /api/v1/tickets/42`) without validating whether the authenticated user owns or has permission to view that object. TrackIT prevents IDOR inside `TicketService.get_ticket`: after fetching the ticket by ID, it explicitly checks the user's role. If the caller has the `EMPLOYEE` role and `ticket.created_by != current_user.id`, it immediately raises a `403 ForbiddenException`."

### Q: "Why should we avoid logging user passwords and JWT tokens?"
**Answer:** "Application logs are often aggregated, indexed, and visible to multiple developers, DevOps engineers, and monitoring tools (e.g. Datadog, CloudWatch). If passwords or raw tokens are written to logs, anyone with log viewer access can steal active sessions or impersonate accounts. TrackIT's structured logging explicitly scrubs credentials and logs only user IDs, action names, and request correlation IDs."
