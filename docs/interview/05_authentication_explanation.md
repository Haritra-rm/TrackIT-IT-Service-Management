# Interview Guide: 05. Authentication & Authorization (JWT + RBAC)

## What is the Auth Architecture?
TrackIT uses stateless **JSON Web Token (JWT)** authentication combined with server-enforced **Role-Based Access Control (RBAC)**. User credentials are encrypted with salted bcrypt hashing, and authorized API calls pass a signed JWT in the `Authorization: Bearer <token>` HTTP header.

## Why was this chosen?
* **Stateless vs. Session Cookies:** In modern web architectures and containerized cloud setups, stateless JWTs eliminate the need for centralized sticky session caches (like Redis) for auth validation. Any backend container instance can independently verify the token signature using the shared `JWT_SECRET_KEY`.
* **FastAPI Dependency Injection:** RBAC is declared cleanly using dependency composition:
  ```python
  @router.patch("/{id}/status")
  def update_status(..., current_user: User = Depends(require_admin)):
  ```
  This keeps routes clean and guarantees authorization rules are not bypassed.

## How it works in TrackIT
1. **Login:** User submits email and password. `AuthService` retrieves the user, calls `bcrypt.checkpw()`, and verifies `is_active == True`.
2. **Token Generation:** A JWT payload is generated containing `sub` (user ID), `role`, `email`, and an expiration timestamp (`exp`). It is signed using `HS256` and the environment `JWT_SECRET_KEY`.
3. **Request Verification:** On incoming requests, `get_current_user` decodes the token, checks signature validity, ensures the token has not expired, and looks up the user.
4. **Role Enforcement:** `require_role([...])` verifies `current_user.role in allowed_roles`, raising `403 ForbiddenException` if unauthorized.

## Potential Interview Questions & Answers

### Q: "Where is the JWT stored on the client, and what are the security trade-offs?"
**Answer:** "In our React client, the JWT is stored in `localStorage` for simplicity and injected into fetch headers by `services/api.js`. The trade-off is that `localStorage` is accessible via JavaScript and therefore vulnerable to Cross-Site Scripting (XSS). The enterprise production alternative is storing the token in an `httpOnly`, `Secure`, `SameSite=Strict` cookie, which prevents client JavaScript from reading it while protecting against CSRF."

### Q: "What happens if a user is deactivated or their role changes after a token is issued?"
**Answer:** "Because JWTs are stateless, a token remains cryptographically valid until its expiration time. In TrackIT, to prevent deactivated users from making requests with existing tokens, the `get_current_user` dependency checks the database on every authenticated request to verify that the user exists and `is_active == True`. If deactivated, a 403 Forbidden exception is immediately returned regardless of the token's remaining validity."
