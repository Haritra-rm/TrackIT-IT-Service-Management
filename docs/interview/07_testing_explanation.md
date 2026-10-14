# Interview Guide: 07. Automated Testing & Verification

## What is the Testing Strategy?
TrackIT employs an automated test suite implemented with **pytest** and FastAPI's `TestClient`. It contains 31 test cases spanning unit logic (SLA formulas, password hashing, priority recommendation) and end-to-end API integration tests (registration, ticket lifecycle workflow, state transitions, and RBAC security gates).

## Why was this testing methodology used?
* **Confidence in Refactoring:** As business logic evolves (e.g. modifying SLA hours or changing transition rules), automated tests ensure existing functionality does not silently break.
* **Security Validation:** RBAC tests explicitly verify that unauthorized roles cannot access restricted endpoints, acting as continuous security regression testing.
* **Isolated Database Fixtures:** Tests run against an isolated SQLite test database with transaction rollbacks via `conftest.py`, ensuring test runs are deterministic and leave no persistent side effects.

## How it works in TrackIT
* `conftest.py` configures a scoped test database and overrides FastAPI's `get_db` dependency.
* Helper fixtures (`admin_user`, `agent_user`, `employee_user`, `sample_category`) provision pre-seeded entities.
* `get_token_header(user)` generates signed JWT headers on the fly.
* Tests verify HTTP response codes, JSON body shapes, database state updates, and specific error codes.

## Interview Questions & Answers

### Q: "What is the difference between unit tests and integration tests in your project?"
**Answer:** "In TrackIT, unit tests verify isolated logic in pure Python without HTTP or database overhead—for example, testing that `SLAService.calculate_due_date` returns exactly 4 hours for `CRITICAL` priority, or testing `PriorityRecommendationEngine` rules. Integration tests, on the other hand, exercise the entire stack: sending HTTP requests via `TestClient`, passing through middlewares, authentication dependencies, service layers, and verifying database commits."

### Q: "How do you test negative and edge cases in TrackIT?"
**Answer:** "I test failure cases as rigorously as happy paths:
1. Rejection of duplicate registration emails (`409 Conflict`).
2. Verification that invalid status transitions (e.g. `CLOSED -> IN_PROGRESS` without reopening) fail with `400 INVALID_STATUS_TRANSITION`.
3. Verification that non-admins cannot deactivate users (`403 INSUFFICIENT_PERMISSIONS`).
4. Rejection of malformed requests with missing required fields (`422 VALIDATION_ERROR`)."
