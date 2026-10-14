# 09. Authentication & JWT Security

### 1. What it is
Authentication is the process of verifying a user's claimed identity. TrackIT implements stateless JSON Web Token (JWT) authentication using HMAC-SHA256 signatures and secure password hashing with Bcrypt.

### 2. Why TrackIT uses it
Session-based authentication (server-side session IDs stored in Redis or memory) requires stateful servers and sticky sessions when scaling behind load balancers. JWTs allow stateless, horizontally scalable authentication where each request carries its own cryptographically verified proof of identity.

### 3. How it works
1. **Password Hashing (Salted Bcrypt)**: Passwords are never stored in plaintext. They are salted and hashed using Bcrypt with an adaptive work factor (12 rounds):
   ```python
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   password_hash = pwd_context.hash(raw_password)
   ```
2. **Token Generation on Login (`/api/v1/auth/login`)**: When credentials verify, the server signs a JWT bearer token containing:
   - `sub`: User ID
   - `email`: User email
   - `role`: Role (`EMPLOYEE`, `SUPPORT_AGENT`, `ADMIN`)
   - `exp`: Expiration timestamp (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
   - `iat`: Issued at timestamp
3. **Token Verification**: On subsequent requests, the client sends `Authorization: Bearer <token>`. FastAPI's `HTTPBearer` extracts and decodes the token, verifying the signature against `JWT_SECRET_KEY` and checking expiration. Expired tokens are rejected with `401 TOKEN_EXPIRED`.

### 4. Where it exists in the code
- Cryptographic Hashing & Signing: [`backend/app/core/security.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/core/security.py)
- Auth Router: [`backend/app/routes/auth.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/routes/auth.py)
- Auth Business Service: [`backend/app/services/auth_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/auth_service.py)
- Frontend Interceptor: [`frontend/src/services/api.js`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/services/api.js)

### 5. Alternative approach
- Traditional cookie-based server sessions stored in memory or Redis.
- OAuth2 social login (Google/GitHub SSO).
- API Keys.

### 6. Why this approach was selected
Server-side sessions introduce central database bottlenecks and complicate horizontal pod autoscaling in Docker/Kubernetes. While SSO is standard in large enterprises, standard JWT credentials provide a zero-external-dependency authentication foundation that can easily be extended to SAML or OAuth2 SSO without altering downstream authorization dependencies.

### 7. Likely interviewer question
*"What information is stored inside the JWT, and why shouldn't we store sensitive data like passwords or credit card numbers in the token?"*

### 8. Simple fresher-level answer
*"We only store minimal claims in the JWT payload: the user ID (`sub`), email, role, and expiration timestamp (`exp`). We never store sensitive data like passwords or personal secrets because JWT payloads are merely Base64URL encoded, not encrypted. Anyone who intercepts the token can decode and view the payload. The security of JWT comes from the cryptographic signature (`HS256`), which proves the payload has not been tampered with by an attacker."*
