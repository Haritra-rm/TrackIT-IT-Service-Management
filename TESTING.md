# TrackIT — Automated Testing Suite & Strategy

TrackIT enforces rigorous automated testing using **pytest**, **HTTPX**, and **FastAPI TestClient**. Every major business rule, authorization guard, and lifecycle transition is backed by executable tests.

---

## 1. Test Architecture & Directory Structure

```
backend/tests/
├── conftest.py             # Shared fixtures: test database, test client, user & token helpers
├── test_auth.py            # Registration, login, password hashing, JWT decoding, profile
├── test_rbac.py            # Role-Based Access Control: permission boundaries between roles
├── test_tickets.py         # Ticket creation, validation, lifecycle transitions, reopen loop
├── test_sla.py             # SLA deadline calculation, status evaluation (on track, at risk, breached, met)
├── test_priority.py        # Rule-based priority recommendation engine
└── test_dashboard.py       # Operational KPI calculations, aggregations, agent performance
```

---

## 2. Test Scope & Coverage Breakdown

### `test_auth.py`
* Salted bcrypt password hashing uniqueness and verification.
* Signed JWT token payload integrity, expiration, and decoding.
* Successful user registration with role default assignment.
* Conflict rejection (`409 EMAIL_ALREADY_EXISTS`) on duplicate email.
* Login success returning valid bearer token.
* Rejection of invalid credentials (`401 INVALID_CREDENTIALS`).
* Access to `/auth/me` with valid JWT header.

### `test_rbac.py`
* **Employee Isolation:** Employees cannot access other employees' tickets (`403 FORBIDDEN`).
* **Support Agent & Admin Visibility:** Support agents and administrators can inspect any organization ticket.
* **Assignment Authorization:** Employees attempting to assign tickets are blocked (`403 FORBIDDEN`).
* **Account Deactivation:** Only administrators can toggle user active status; non-admins receive `403 INSUFFICIENT_PERMISSIONS`.

### `test_tickets.py`
* Validation errors on short titles ($< 5$ characters) or invalid category IDs (`422 VALIDATION_ERROR`).
* Full linear lifecycle workflow:
  $$\text{OPEN} \longrightarrow \text{ASSIGNED} \longrightarrow \text{IN\_PROGRESS} \longrightarrow \text{RESOLVED} \longrightarrow \text{CLOSED}$$
* Comment creation on ticket threads with author metadata.
* Enforcing mandatory resolution notes when transitioning to `RESOLVED`.
* State machine transition guard: invalid status transitions (e.g. `OPEN` directly to `RESOLVED`) are rejected with `400 INVALID_STATUS_TRANSITION`.
* **Reopen Loop:** Employee reopening resolved ticket when an issue persists, verifying timestamp reset and history update.

### `test_sla.py`
* Verifying correct SLA target durations:
  * `CRITICAL` $\rightarrow$ 4 hours
  * `HIGH` $\rightarrow$ 24 hours
  * `MEDIUM` $\rightarrow$ 48 hours
  * `LOW` $\rightarrow$ 72 hours
* Real-time SLA status evaluation:
  * `ON_TRACK`: Remaining time $> 4$ hours.
  * `AT_RISK`: Remaining time $\le 4$ hours.
  * `BREACHED`: Target deadline exceeded.
  * `MET`: Ticket resolved before target deadline.

### `test_priority.py`
* Security incidents or core infrastructure outages escalate immediately to `CRITICAL`.
* Large blast radius (20+ users on network/access) recommends `CRITICAL`.
* Departmental/team impact (5+ users) recommends `HIGH`.
* Individual issues recommend `LOW` or `MEDIUM`.

### `test_dashboard.py`
* KPI calculation accuracy: total tickets, open tickets, resolution rate, and SLA breach rate.
* Status breakdown distribution.
* Priority breakdown distribution.
* Agent throughput and SLA compliance metrics calculation.

---

## 3. Running the Tests Locally

Activate your virtual environment and run:

```bash
# Run all tests with verbose output
pytest backend/tests -v

# Run with test execution durations (identifies slow tests)
pytest backend/tests -v --durations=10

# Run specific test module
pytest backend/tests/test_rbac.py -v

# Generate code coverage report
pytest backend/tests --cov=app --cov-report=term-missing
```
