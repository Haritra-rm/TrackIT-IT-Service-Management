# Contributing to TrackIT

Thank you for contributing to TrackIT! We welcome bug fixes, documentation enhancements, and feature proposals.

---

## Code Standards & Guidelines

1. **Python / Backend:**
   * Adhere to **PEP 8** style guidelines.
   * Provide explicit **Type Hints** for all function parameters and return types.
   * Use **Pydantic v2** models for request/response serialization.
   * Keep route handlers thin; place domain rules in `services/` and database queries in `repositories/`.
   * Add automated tests under `backend/tests/` for any new business logic or endpoints.

2. **Frontend / React:**
   * Use functional React components with Hooks.
   * Keep components modular and reusable under `components/`.
   * Isolate API communications inside `services/`.
   * Follow consistent design system variables defined in `index.css`.

---

## Git Workflow & Commit Guidelines

We follow the **Conventional Commits** specification:

* `feat: <description>`: Introducing new functionality (e.g. `feat: add email notification dispatch on SLA breach`).
* `fix: <description>`: Bug fixes (e.g. `fix: correct timezone disparity in SLA remaining calculation`).
* `test: <description>`: Adding or updating test suites (e.g. `test: add RBAC isolation tests`).
* `docs: <description>`: Documentation changes (e.g. `docs: update API reference`).
* `refactor: <description>`: Code refactoring without changing observable behavior.

### Development Process:
1. Fork and create a feature branch: `git checkout -b feature/my-new-feature`
2. Run test suite: `pytest backend/tests -v`
3. Verify frontend build: `cd frontend && npm run build`
4. Commit your changes: `git commit -m "feat: implement ticket bulk export"`
5. Submit a Pull Request targeting the `main` branch.
