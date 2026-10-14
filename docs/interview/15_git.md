# 15. Git Version Control & Engineering Practices

### 1. What it is
Git is a distributed version control system for tracking changes in source code across branches, commits, tags, and pull requests.

### 2. Why TrackIT uses it
Professional engineering requires granular version history, atomic commits, branch protection, and reproducible collaboration. It ensures that changes can be audited, bisected, and rolled back if bugs are introduced.

### 3. How it works
- **Conventional Commits Specification**: Commits follow structured semantic prefixes:
  - `feat:` for new capabilities (e.g. `feat(api): implement ticket lifecycle state machine`).
  - `fix:` for bug fixes (e.g. `fix(sla): adjust SLA hours and proportional at-risk calculation`).
  - `test:` for test suites (e.g. `test(rbac): add authorization boundary tests`).
  - `docs:` for documentation updates.
  - `chore:` for dependency and build configuration.
- **Strict `.gitignore` Boundaries**:
  Local virtual environments (`venv/`), Node dependencies (`node_modules/`), SQLite database files (`*.db`), environment secrets (`.env`), and build artifacts (`dist/`, `__pycache__/`) are strictly ignored to prevent credential leaks and repository bloat.
- **Clean Branching Strategy (GitHub Flow)**: Feature branches are developed off `main`, tested in GitHub Actions CI, and merged via PR after tests pass.

### 4. Where it exists in the code
- Repository Git Log: Viewable via `git log --oneline`
- Ignored Paths: [`.gitignore`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/.gitignore)
- Contribution Guidelines: [`CONTRIBUTING.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/CONTRIBUTING.md)

### 5. Alternative approach
- Storing code in Google Drive / Zip files.
- Committing giant monolithic changes with messages like "fixed stuff" or "updated code".

### 6. Why this approach was selected
Conventional commits allow automated changelog generation and simplify `git bisect` when hunting for regressions. Clear semantic history proves to an interviewer that the candidate operates with real-world enterprise engineering discipline.

### 7. Likely interviewer question
*"Why is it critical to keep `.env` out of your Git repository, and what should you commit instead?"*

### 8. Simple fresher-level answer
*"A `.env` file contains sensitive secrets such as JWT signing keys and database passwords. If committed to a public or private Git repository, those credentials are permanently baked into the commit history and can be scraped by automated bots. Instead, we add `.env` to `.gitignore` and commit a sanitized `.env.example` file that documents the required variable names with safe dummy placeholder values."*
