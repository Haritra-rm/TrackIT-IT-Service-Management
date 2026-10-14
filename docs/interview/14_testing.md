# 14. Automated Testing & Quality Engineering

### 1. What it is
Automated testing is the practice of validating software correctness using automated test scripts across Unit, Integration, and API levels using Pytest, Starlette TestClient, and HTTP assertion frameworks.

### 2. Why TrackIT uses it
An issue tracking platform with strict role-based access control and lifecycle state transitions cannot rely on manual testing. A regression in RBAC could expose confidential salary tickets to general staff, or an error in SLA calculation could cause missed customer commitments.

### 3. How it works
- **Organized Test Hierarchy**:
  - `backend/tests/unit/`: Tests algorithmic and mathematical units in isolation (`test_sla.py` testing the 6 SLA scenarios, `test_priority.py` testing blast-radius scoring).
  - `backend/tests/integration/`: Tests multi-table SQL queries, status aggregations, and dashboard KPIs (`test_dashboard.py`).
  - `backend/tests/api/`: Tests end-to-end HTTP request flows, authorization rejections (403), state machine rules, validation errors (422), and token rejections (`test_auth.py`, `test_rbac.py`, `test_tickets.py`, `test_errors_api.py`).
- **Database Isolation via Fixtures**:
  In `conftest.py`, each test receives an isolated SQLite database connection with a transaction rollback fixture (`db_session`). Tests cannot pollute each other's data, ensuring 100% repeatability.
- **Negative / Failure Testing**:
  Tests deliberately exercise invalid credentials, expired JWTs, missing tokens, malformed headers, illegal status transitions (e.g. `CLOSED -> IN_PROGRESS`), and unauthorized role calls.

### 4. Where it exists in the code
- Test Suites: [`backend/tests/`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/tests/)
- Pytest Fixtures: [`backend/tests/conftest.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/tests/conftest.py)
- Testing Guide: [`TESTING.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/TESTING.md)

### 5. Alternative approach
- Manual testing using Postman or manual browser clicks.
- Writing tests that only test happy paths (200 OK) without validating failure scenarios.

### 6. Why this approach was selected
Manual testing is slow, error-prone, and cannot catch subtle regressions when refactoring. Pytest with FastAPI's `TestClient` executes 48 comprehensive end-to-end integration and unit tests in under 18 seconds, giving immediate confidence before deployment or CI merge.

### 7. Likely interviewer question
*"How do you ensure automated tests don't leave dirty data in the database between test runs?"*

### 8. Simple fresher-level answer
*"I use a Pytest fixture in `conftest.py` that wraps each test execution inside a SQLAlchemy database transaction. Before the test runs, it opens a transaction; after the test completes (whether it passes or fails), it executes `transaction.rollback()`. This guarantees that every test starts with a completely pristine database state and tests never interfere with one another."*
