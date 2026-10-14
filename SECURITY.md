# TrackIT — Application Security Architecture & Best Practices

## 1. Threat Model & Security Posture

TrackIT protects internal IT operational telemetry, employee credentials, and sensitive workplace issue reports. The application implements defense-in-depth principles across all tiers.

---

## 2. Authentication Architecture

1. **Password Hashing:**
   * Passwords are never stored in plain text.
   * Stored passwords use the industry-standard **bcrypt** adaptive cryptographic hash function (`passlib[bcrypt]`), utilizing per-user random salts and default 12 work factor rounds.
   * Bcrypt automatically mitigates rainbow table attacks and resists GPU-accelerated brute force.
2. **Stateless JWT Authorization:**
   * Successful logins issue signed **JSON Web Tokens (JWT)** using HMAC-SHA256 (`HS256`).
   * Tokens encode standard claims (`sub` user ID, `email`, `role`, `iat`, `nbf`, `exp`).
   * Token lifetime is configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (defaults to 8 hours).
   * Token expiration (`ExpiredSignatureError`) and tampering (`InvalidTokenError`) are intercepted by custom exception handlers returning clean 401 JSON responses.

---

## 3. Role-Based Access Control (RBAC)

RBAC is enforced **independently and unconditionally on the backend** through FastAPI dependency factories (`require_role([...])` in `app/core/dependencies.py`). Hiding frontend navigation buttons is treated purely as a UI convenience, never as a security boundary.

### Permission Matrix:

| Action | Employee | Support Agent | Administrator |
| :--- | :---: | :---: | :---: |
| Register Account | Yes | No (Admin provisioned) | No |
| View Own Tickets | Yes | Yes | Yes |
| View Other Employees' Tickets | **No (403)** | Yes | Yes |
| Create Ticket | Yes | Yes | Yes |
| Assign / Reassign Ticket | **No (403)** | Yes | Yes |
| Advance Status (Triage/Progress) | **No (403)** | Yes | Yes |
| Resolve Ticket (with notes) | **No (403)** | Yes | Yes |
| Reopen Ticket | Own Only | Yes | Yes |
| Delete Ticket | **No (403)** | **No (403)** | **Yes** |
| Access Admin Dashboard & KPIs | **No (403)** | Yes | Yes |
| Activate / Deactivate Users | **No (403)** | **No (403)** | **Yes** |
| Create / Edit Categories | **No (403)** | **No (403)** | **Yes** |
| Inspect Audit Logs | **No (403)** | **No (403)** | **Yes** |

---

## 4. Injection & Input Sanitization

1. **SQL Injection Protection:**
   * TrackIT uses **SQLAlchemy ORM 2.0**. All queries, filters, joins, and mutations are constructed using parameterized binding (`:param`).
   * Dynamic user input is never concatenated into raw SQL strings, guaranteeing complete immunity against SQL injection vulnerabilities.
2. **Schema Input Validation:**
   * All incoming payloads are strongly typed and validated through **Pydantic v2**.
   * Constraints enforced at boundary:
     * `email`: Validated via RFC 5322 through `email-validator`.
     * `password`: Minimum 6, maximum 128 characters.
     * `title`: Minimum 5, maximum 200 characters.
     * `description`: Minimum 10 characters.
     * `resolution_notes`: Minimum 5 characters.
3. **Cross-Site Scripting (XSS) Prevention:**
   * React automatically escapes variables rendered in JSX templates.
   * Rich user content is sanitized before DOM injection.

---

## 5. Network & Operational Security

1. **Cross-Origin Resource Sharing (CORS):**
   * Configured via `CORS_ORIGINS` environment variable.
   * In production, wildcards (`*`) are disallowed; requests are strictly constrained to authorized company hostnames and CDNs.
2. **Zero Information Leakage:**
   * Global exception middleware intercepts all unhandled errors (`Exception`).
   * Raw Python tracebacks and internal database schema names are never returned to client browsers; clients receive a safe, generic `INTERNAL_SERVER_ERROR` payload while full diagnostic stack traces are written to secure backend logs.
3. **Security Audit Logging:**
   * Key security events (registration, logins, failed authentications, status modifications, user deactivations) generate immutable entries in the `audit_logs` table with actor, target entity, timestamp, and metadata.
4. **Secret Hygiene:**
   * All sensitive keys (`JWT_SECRET_KEY`, database credentials) are injected exclusively through environment variables (`.env`).
   * `.env` is listed in `.gitignore` and `.dockerignore` to prevent accidental commits to source repositories.

---

## 6. Rate Limiting Strategy (Production Blueprint)

In high-volume or public-facing enterprise deployments, TrackIT recommends implementing rate limiting at the reverse proxy or API gateway tier:
* **Token Bucket Algorithm:** Implemented via Nginx `limit_req_zone` or AWS WAF / API Gateway.
* **Suggested Thresholds:**
  * `/api/v1/auth/login`: Maximum 5 requests/minute per IP (prevents credential stuffing).
  * `/api/v1/tickets` (POST): Maximum 10 submissions/minute per user.
  * General read APIs: 100 requests/minute per authenticated user.
