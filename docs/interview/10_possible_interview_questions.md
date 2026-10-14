# TrackIT — Master Technical & Architectural Interview Guide
### 50+ Comprehensive Interview Questions & In-Depth Answers for Associate Product Engineer & Software Engineer Roles

---

## Part 1: Python & Object-Oriented Programming (OOP)

### 1. What are Python type hints, and why did you use them in TrackIT?
* **Short Answer:** Type hints specify the expected data types for variables, function arguments, and return values to improve code reliability, tooling, and readability.
* **Detailed Explanation:** Introduced in PEP 484 and enhanced in Python 3.10+, type hints allow static analysis tools (like Mypy or Ruff) to detect bugs before runtime. In FastAPI and Pydantic, type hints serve a dual purpose: they are evaluated at runtime via reflection to enforce request validation and generate OpenAPI documentation.
* **How it applies to TrackIT:** Used extensively across schemas and services (e.g. `def list_tickets(...) -> Tuple[List[TicketResponse], int]:`) ensuring predictable method contracts and automated Swagger docs.

### 2. How did you demonstrate OOP Encapsulation in TrackIT?
* **Short Answer:** By keeping internal state, business rules, and helper methods internal to dedicated service classes while exposing clean public interfaces.
* **Detailed Explanation:** Encapsulation bundles data and the methods that operate on that data within a single unit while restricting direct external access to internal state. In TrackIT, `TicketService` encapsulates the allowed status transition matrix (`VALID_TRANSITIONS`) and response enrichment logic (`_enrich_ticket_response`), preventing route handlers from arbitrarily mutating tickets.
* **How it applies to TrackIT:** External code cannot force an invalid transition or bypass SLA evaluation because the state transitions are strictly governed inside `TicketService`.

### 3. What is Abstraction, and how is it used in the Repository pattern?
* **Short Answer:** Abstraction hides complex implementation details and exposes only essential operations through a simplified interface.
* **Detailed Explanation:** Abstraction allows developers to interact with a system at a higher conceptual level. By implementing `UserRepository` and `TicketRepository`, business logic layers do not know or care whether the underlying persistence layer is PostgreSQL, SQLite, or an external API.
* **How it applies to TrackIT:** Route handlers invoke `service.get_ticket(id)` without writing SQL joins or managing database sessions directly.

### 4. What is Inheritance, and how is `BaseRepository[T]` structured?
* **Short Answer:** Inheritance allows a class to derive attributes and methods from a parent class to promote code reuse and adhere to the DRY principle.
* **Detailed Explanation:** TrackIT defines `BaseRepository[ModelType]` which provides generic `get_by_id`, `create`, `update`, `delete`, and `count` methods using Python typing generics (`TypeVar`). Specialized repositories like `CategoryRepository` inherit these capabilities and add domain-specific queries (`get_active_categories`).
* **How it applies to TrackIT:** Avoids writing duplicate boilerplate CRUD logic across 5 different repository classes.

### 5. What is Polymorphism, and where does TrackIT employ it?
* **Short Answer:** Polymorphism enables entities of different types to be handled through a uniform interface while exhibiting specialized behavior.
* **Detailed Explanation:** Polymorphism allows one function or interface to behave differently depending on the input or context. In `DashboardService.get_summary(user: User)`, the summary metric query dynamically scopes ticket calculations based on the user's role: an Employee sees only their own tickets, an Agent sees their assigned queue, and an Admin receives enterprise-wide metrics.
* **How it applies to TrackIT:** A single endpoint `GET /api/v1/dashboard/summary` polymorphically responds with the exact context appropriate for the calling role.

### 6. What are Python Decorators, and how are they used in FastAPI?
* **Short Answer:** Decorators are functions that take another function as an argument, extend its behavior without modifying it, and return the modified function.
* **Detailed Explanation:** Decorators use the `@decorator` syntax. In FastAPI, `@router.get("/tickets")` registers route handlers with the underlying Starlette router, inspects type signatures, and attaches route metadata.
* **How it applies to TrackIT:** Used for route declarations, exception handlers (`@app.exception_handler`), and dependency injection.

### 7. What is a Context Manager in Python, and how is `get_db()` implemented?
* **Short Answer:** A context manager safely allocates and releases resources using the `with` statement or Python generators (`yield`).
* **Detailed Explanation:** Context managers guarantee cleanup even if exceptions occur. `get_db()` yields a SQLAlchemy `Session` to the route handler and runs `db.close()` in a `finally` block, preventing database connection leaks.
* **How it applies to TrackIT:** Every incoming HTTP request receives an isolated database session that automatically closes upon request termination.

---

## Part 2: Data Structures & Algorithms (DSA)

### 8. What is the algorithmic time complexity of searching a ticket by ID in TrackIT?
* **Short Answer:** $O(\log N)$ in the database using a B-Tree primary key index, compared to $O(N)$ for an unindexed table scan.
* **Detailed Explanation:** Primary keys are indexed with B-Trees by PostgreSQL. B-Trees have a logarithmic search depth $O(\log_B N)$ where branch factor $B \approx 100$. On a table of 1,000,000 tickets, finding a specific ticket takes $\le 4$ block reads.
* **How it applies to TrackIT:** Fast retrieval on `/api/v1/tickets/{id}` regardless of database size.

### 9. Why are dictionary hash maps used for state machine transitions?
* **Short Answer:** Dictionary lookups have an average-case time complexity of $O(1)$.
* **Detailed Explanation:** In `TicketService.VALID_TRANSITIONS`, keys are current statuses and values are lists of permitted target statuses. Validating whether `target_status in VALID_TRANSITIONS[current_status]` executes in constant time $O(1)$ without scanning arrays or executing database queries.
* **How it applies to TrackIT:** Fast, deterministic status transition validation before database mutation.

### 10. How does TrackIT sort tickets, and what is the underlying complexity?
* **Short Answer:** Sorting is pushed to the database engine using indexed ordering (`ORDER BY created_at DESC`), executing in $O(M \log M)$ or $O(1)$ when traversing an index.
* **Detailed Explanation:** Because `created_at` has a B-Tree index, fetching sorted records with a `LIMIT` executes by traversing the index backward, requiring no expensive in-memory Quicksort or Timsort.
* **How it applies to TrackIT:** `GET /api/v1/tickets?sort_by=created_at&sort_order=desc` serves paginated lists with sub-10ms response times.

### 11. How is a Queue data structure conceptually applied in TrackIT?
* **Short Answer:** Unassigned tickets in the `OPEN` state form a First-In, First-Out (FIFO) triage work queue for support agents.
* **Detailed Explanation:** When support agents view the unassigned queue (`GET /api/v1/tickets?status=OPEN&sort_by=created_at&sort_order=asc`), tickets submitted earliest are triaged first, ensuring fair FIFO processing and preventing SLA starvation.
* **How it applies to TrackIT:** The Agent Workbench provides an "Unassigned Incoming" tab sorted chronologically to process tickets in queue order.

### 12. What is the space and time complexity of the Priority Recommendation Engine?
* **Short Answer:** Time complexity is $O(1)$ and auxiliary space complexity is $O(1)$.
* **Detailed Explanation:** The recommendation engine executes a fixed set of conditional checks against blast radius thresholds (e.g. `users >= 20`) and impact strings. It requires no recursive calls, loops, or auxiliary memory structures.
* **How it applies to TrackIT:** Instant priority calculation on `POST /api/v1/tickets/recommend-priority`.

---

## Part 3: Databases & SQL

### 13. What is Database Normalization, and what normal form does TrackIT use?
* **Short Answer:** Normalization organizes database columns and tables to eliminate data redundancy and anomalies; TrackIT is in Third Normal Form (3NF).
* **Detailed Explanation:** In 3NF, all columns depend on the key, the whole key, and nothing but the key. TrackIT stores user names and emails in `users` and references them via `user_id` in `tickets`, `comments`, and `audit_logs`.
* **How it applies to TrackIT:** If a user updates their name or email, only one row in `users` is updated; ticket history and comments remain intact.

### 14. What are Foreign Keys and `ON DELETE CASCADE` constraints?
* **Short Answer:** Foreign keys enforce referential integrity between tables; `CASCADE` automatically deletes child rows when the parent row is deleted.
* **Detailed Explanation:** In `comments`, `ticket_id` references `tickets.id` with `ON DELETE CASCADE`. If a ticket is purged by an administrator, PostgreSQL automatically deletes all corresponding comments and status histories in the same transaction.
* **How it applies to TrackIT:** Guarantees zero orphaned comments in the database.

### 15. What is the N+1 query problem, and how is it eliminated in SQLAlchemy?
* **Short Answer:** The N+1 problem occurs when fetching $N$ records causes $N$ additional sub-queries to fetch related entities; eliminated via eager loading (`joinedload`).
* **Detailed Explanation:** Without eager loading, fetching 20 tickets and accessing `ticket.creator.name` executes 1 query for the tickets and 20 individual queries for each creator. Using `joinedload(Ticket.creator)` generates an SQL `LEFT OUTER JOIN`, reducing 21 round trips to 1 single query.
* **How it applies to TrackIT:** Implemented in `TicketRepository.get_by_id_with_relations` and `search_and_filter`.

### 16. What is the difference between SQLite and PostgreSQL?
* **Short Answer:** SQLite is a serverless, file-based database ideal for local development and testing; PostgreSQL is a client-server relational DBMS built for high-concurrency production.
* **Detailed Explanation:** SQLite lacks multi-writer concurrency and fine-grained network access controls. PostgreSQL provides robust connection pooling, parallel query execution, write-ahead logging (WAL), and ACID compliance under high load.
* **How it applies to TrackIT:** TrackIT supports both: developers run locally with zero-configuration SQLite, while Docker Compose and AWS run PostgreSQL 16.

### 17. What is an Index, and why not index every single column?
* **Short Answer:** An index is an auxiliary data structure (usually a B-Tree) that speeds up reads; over-indexing degrades write performance and consumes extra disk space.
* **Detailed Explanation:** Every time a row is inserted, updated, or deleted, every index on that table must also be updated. Indexing rarely-filtered columns creates write latency and memory bloat.
* **How it applies to TrackIT:** Only high-cardinality filter columns (`email`, `status`, `priority`, `created_by`, `due_at`) are indexed.

### 18. What are Alembic migrations, and why are they necessary?
* **Short Answer:** Alembic is a database migration tool for SQLAlchemy that tracks schema evolution over time.
* **Detailed Explanation:** Without migrations, modifying a table column requires manual SQL DDL scripts or dropping and recreating tables (which destroys data). Alembic scripts provide version-controlled, reversible `upgrade()` and `downgrade()` methods.
* **How it applies to TrackIT:** Migrations live in `backend/alembic/versions/` and run automatically in CI and production.

---

## Part 4: FastAPI & REST APIs

### 19. What makes FastAPI faster than traditional Python frameworks like Django or Flask?
* **Short Answer:** FastAPI is built on Starlette and Uvicorn (ASGI) using asynchronous Python (`async/await`) and Pydantic compilation.
* **Detailed Explanation:** Unlike WSGI servers that block worker threads during I/O operations, ASGI handles non-blocking network requests concurrently on an event loop. FastAPI also pre-compiles validation schemas with C-accelerated `pydantic-core`.
* **How it applies to TrackIT:** Provides sub-10ms response times and high throughput for concurrent ticket updates.

### 20. How does Pydantic perform request validation?
* **Short Answer:** Pydantic validates incoming JSON request bodies against declared Python type annotations and field constraints before calling route handlers.
* **Detailed Explanation:** If a payload violates constraints (e.g. title $< 5$ characters or invalid email), Pydantic raises a `RequestValidationError`. TrackIT's global exception handler transforms this into a clean 422 JSON error response without executing controller code.
* **How it applies to TrackIT:** Guarantees that invalid data never reaches services or the database.

### 21. What is Dependency Injection in FastAPI, and how is it used?
* **Short Answer:** A software design pattern where objects or dependencies are provided to a function rather than created inside it.
* **Detailed Explanation:** In FastAPI, `Depends(...)` declares dependencies. FastAPI resolves them hierarchically: opening database sessions, validating JWT headers, checking user roles, and injecting the resolved instances into route parameters.
* **How it applies to TrackIT:** Used for `db: Session = Depends(get_db)` and `current_user = Depends(require_admin)`.

### 22. What are the essential HTTP status codes used in TrackIT?
* **Short Answer:**
  * `200 OK`: Successful retrieval or update.
  * `201 Created`: Ticket, user, or category created.
  * `204 No Content`: Successful ticket deletion.
  * `400 Bad Request`: Invalid lifecycle state transition.
  * `401 Unauthorized`: Missing or invalid JWT.
  * `403 Forbidden`: Insufficient role permissions.
  * `404 Not Found`: Ticket or user ID does not exist.
  * `409 Conflict`: Duplicate email registration.
  * `422 Unprocessable Content`: Validation failure.
  * `500 Internal Server Error`: Unhandled server exception.

### 23. What is CORS, and how is it configured in TrackIT?
* **Short Answer:** Cross-Origin Resource Sharing is a browser security mechanism that restricts web pages from making API calls to a different domain.
* **Detailed Explanation:** When React runs on `http://localhost:5173` and FastAPI runs on `http://localhost:8000`, the browser issues an `OPTIONS` preflight request. FastAPI's `CORSMiddleware` checks `settings.CORS_ORIGINS` and responds with allowed headers and methods.
* **How it applies to TrackIT:** Configured in `backend/app/main.py` via `CORSMiddleware`.

---

## Part 5: React & Frontend Architecture

### 24. What is the Virtual DOM, and how does React optimize rendering?
* **Short Answer:** The Virtual DOM is an in-memory representation of the real DOM; React diffs it against the previous tree and batches minimal real DOM updates.
* **Detailed Explanation:** Directly mutating browser DOM nodes is slow. When state changes in a React component, React creates a new virtual DOM tree, computes the diff (reconciliation), and updates only the changed HTML elements.
* **How it applies to TrackIT:** Status badges and countdown timers re-render smoothly without flickering the entire ticket table.

### 25. How is global state managed in TrackIT without Redux?
* **Short Answer:** Using React's built-in **Context API (`AuthContext`)** and custom hooks (`useAuth`).
* **Detailed Explanation:** Redux introduces significant boilerplate for small-to-medium applications. TrackIT uses `AuthContext` to manage user identity, authentication tokens, and role permissions globally, making them accessible via `useAuth()`.
* **How it applies to TrackIT:** Sidebar, Navbar, and protected route guards share authenticated user state seamlessly.

### 26. What are React Hooks, and which ones are used in TrackIT?
* **Short Answer:** Functions that allow functional components to use state and lifecycle features; TrackIT uses `useState`, `useEffect`, `useContext`, `useParams`, and `useNavigate`.
* **Detailed Explanation:**
  * `useState`: Manages local component state (form inputs, modal toggles, loading indicators).
  * `useEffect`: Executes side effects (fetching tickets from API on page load or filter changes).
  * `useParams`: Extracts route parameters (`ticket_id` from `/tickets/:id`).
  * `useNavigate`: Programmatically redirects users between routes.

### 27. How does TrackIT protect private routes in React Router?
* **Short Answer:** Using a custom `<ProtectedRoute allowedRoles={[...]} />` wrapper component.
* **Detailed Explanation:** The `ProtectedRoute` checks `useAuth()`. If the user is unauthenticated, it renders `<Navigate to="/login" replace />`. If their role is not included in `allowedRoles`, it redirects to the home dashboard.
* **How it applies to TrackIT:** Prevents employees from opening Admin routes like `/users` or `/audit-logs`.

### 28. How does `services/api.js` intercept HTTP 401 errors?
* **Short Answer:** It centralizes `fetch` calls, checks `response.status === 401`, purges `localStorage`, and triggers a `trackit_logout` custom window event.
* **Detailed Explanation:** If a token expires while an agent is working, the next API request receives a 401 response. `services/api.js` automatically clears expired credentials and redirects the user to the login screen.
* **How it applies to TrackIT:** Prevents stale session errors and ensures seamless re-authentication.

---

## Part 6: Authentication, Authorization & Security

### 29. What is the difference between Authentication and Authorization?
* **Short Answer:** Authentication verifies **who you are**; Authorization verifies **what you are allowed to do**.
* **Detailed Explanation:** Logging in with an email and password is *authentication*. Checking whether the authenticated user has permission to delete a ticket or deactivate another user is *authorization* (RBAC).
* **How it applies to TrackIT:** `auth_service.py` handles authentication; `dependencies.py` (`require_role`) handles authorization.

### 30. Why is bcrypt better than MD5 or SHA256 for passwords?
* **Short Answer:** MD5 and SHA256 are fast general-purpose hash functions vulnerable to brute-force and rainbow table attacks; bcrypt is intentionally slow and salted.
* **Detailed Explanation:** Fast hashes allow attackers to calculate billions of guesses per second on modern GPUs. Bcrypt incorporates a salt (preventing pre-computed rainbow table lookups) and a configurable cost factor (work rounds) that slows down attackers exponentially.
* **How it applies to TrackIT:** TrackIT hashes all passwords using `passlib[bcrypt]` with salted hashing.

### 31. What is an Insecure Direct Object Reference (IDOR), and how does TrackIT prevent it?
* **Short Answer:** An IDOR occurs when an application exposes a direct database ID without validating user ownership; prevented via backend role verification.
* **Detailed Explanation:** If Employee A creates ticket #10 and Employee B requests `GET /api/v1/tickets/10`, a naive backend might return it. TrackIT's `TicketService` checks `if current_user.role == 'EMPLOYEE' and ticket.created_by != current_user.id: raise ForbiddenException(...)`.
* **How it applies to TrackIT:** Fully tested in `test_rbac.py::test_employee_cannot_view_other_employees_ticket`.

### 32. What is SQL Injection, and how does SQLAlchemy ORM prevent it?
* **Short Answer:** SQL injection occurs when untrusted user input is concatenated into an SQL string; SQLAlchemy uses parameterized queries to treat input strictly as literals.
* **Detailed Explanation:** Instead of executing `f"SELECT * FROM tickets WHERE title = '{title}'"`, SQLAlchemy compiles `SELECT * FROM tickets WHERE title = :title_1` and sends data values separately from the SQL statement structure to the database driver.
* **How it applies to TrackIT:** All user queries and filters are safely parameterized.

### 33. Why shouldn't sensitive credentials be committed to Git?
* **Short Answer:** Committing secrets to version control exposes them to anyone with repository access and makes them permanently accessible in commit history.
* **Detailed Explanation:** Automated bots continuously scan public and private GitHub repositories for secrets. TrackIT uses `.env.example` as a template and adds `.env` to `.gitignore`.
* **How it applies to TrackIT:** Zero credentials or JWT secret keys are hardcoded in the codebase.

---

## Part 7: DevOps, Docker & CI/CD

### 34. What is Docker, and how does it differ from a Virtual Machine (VM)?
* **Short Answer:** Docker containers share the host OS kernel and package only application code and dependencies, making them lightweight and fast compared to full VMs.
* **Detailed Explanation:** A VM runs a full guest operating system with virtualized hardware, consuming gigabytes of memory and minutes to boot. Docker containers isolate processes at the kernel level using namespaces and cgroups, booting in seconds with minimal overhead.
* **How it applies to TrackIT:** The entire TrackIT platform (PostgreSQL, FastAPI backend, React frontend) runs in lightweight containers.

### 35. What is a Docker Volume, and why is it used for PostgreSQL?
* **Short Answer:** A Docker volume persists data outside the container lifecycle so database state is not lost when containers restart or rebuild.
* **Detailed Explanation:** Containers are ephemeral by default; any file written inside a container disappears when the container is removed. In `docker-compose.yml`, `postgres_data:/var/lib/postgresql/data` mounts a persistent host volume.
* **How it applies to TrackIT:** Tickets, users, and comments survive container restarts.

### 36. What is Continuous Integration (CI), and what does TrackIT's CI pipeline do?
* **Short Answer:** CI automatically builds, lints, and tests code changes on every Git commit or pull request to detect regressions early.
* **Detailed Explanation:** Configured in `.github/workflows/ci.yml`, TrackIT's GitHub Actions pipeline installs dependencies, runs pytest across all 31 unit and integration tests, verifies linting, and runs `npm run build` on the React frontend.
* **How it applies to TrackIT:** Prevents broken code or failing tests from merging into the main branch.

### 37. What is a Health Check in Docker, and why is it important?
* **Short Answer:** A health check periodically runs a command inside the container to verify whether the application is genuinely responsive.
* **Detailed Explanation:** A container can be in the "Running" state while the internal web server is deadlocked or initializing. TrackIT's backend Dockerfile includes `HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1`.
* **How it applies to TrackIT:** Docker Compose waits for PostgreSQL to be healthy (`pg_isready`) before launching the backend.

---

## Part 8: Cloud & System Design

### 38. How would you scale TrackIT to handle 100,000 active employees?
* **Short Answer:** By scaling the stateless backend horizontally across ECS Fargate tasks, placing a read-replica on RDS PostgreSQL, and caching read-heavy endpoints in Redis.
* **Detailed Explanation:**
  1. **Stateless Compute:** Scale FastAPI containers horizontally behind an Application Load Balancer.
  2. **Database Read/Write Splitting:** Route write operations (ticket creation, status updates) to the primary PostgreSQL instance and read operations (dashboard metrics, ticket listings) to read-replicas.
  3. **Caching:** Cache category lists and user profiles in Redis with TTLs.
  4. **CDN:** CloudFront serves static React frontend assets from edge locations.
* **How it applies to TrackIT:** The modular architecture makes introducing Redis caching or read replicas trivial without refactoring domain logic.

### 39. What is a Deadlock in relational databases, and how do you prevent it?
* **Short Answer:** A deadlock occurs when two concurrent transactions hold locks and each waits for the other to release its lock; prevented by acquiring locks in a consistent order.
* **Detailed Explanation:** If Transaction 1 updates Ticket A then Ticket B, while Transaction 2 updates Ticket B then Ticket A, a circular wait occurs. In TrackIT, ticket updates always operate on a single ticket ID per transaction with short-lived locks, avoiding distributed lock contention.

### 40. How does AWS CloudFront improve frontend performance?
* **Short Answer:** CloudFront is a Content Delivery Network (CDN) that caches static frontend files at hundreds of Edge Locations globally close to the end user.
* **Detailed Explanation:** Instead of every employee's browser requesting `index.html` and JavaScript bundles from an S3 bucket in a single region, CloudFront serves cached assets from the closest edge server, reducing latency from 200ms to $< 20\text{ms}$.

---

## Part 9: Product Thinking, KPIs & Business Logic

### 41. What is an SLA (Service Level Agreement), and how does TrackIT calculate it?
* **Short Answer:** An SLA is a committed deadline for issue resolution; TrackIT calculates `due_at` by adding configured priority hours to the creation timestamp.
* **Detailed Explanation:** Configured in `app/core/config.py`:
  * `CRITICAL`: 4 hours
  * `HIGH`: 24 hours
  * `MEDIUM`: 48 hours
  * `LOW`: 72 hours
  `SLAService.evaluate_sla_status` checks current time against `due_at` and dynamically marks tickets as `ON_TRACK`, `AT_RISK` ($\le 4\text{h}$ left), `BREACHED`, or `MET`.
* **How it applies to TrackIT:** Color-coded badges and countdowns alert support agents before breaches occur.

### 42. Why is the Smart Priority Advisor rule-based instead of an LLM/Black-box AI?
* **Short Answer:** Rule-based engines are deterministic, auditable, fast ($< 1\text{ms}$), zero-cost, and explainable in regulated enterprise environments.
* **Detailed Explanation:** Large Language Models can hallucinate, suffer from non-deterministic outputs, and introduce network latency and per-token API costs. In ITSM, priority criteria (blast radius, security flags) follow defined business policies that are best expressed via deterministic rules.
* **How it applies to TrackIT:** `PriorityRecommendationEngine` provides transparent explanations: *"High blast radius (25 users) affecting core infrastructure qualifies as CRITICAL priority."*

### 43. What is the business purpose of the `REOPENED` ticket status?
* **Short Answer:** It empowers employees to reject premature closures and ensures resolved issues genuinely fixed the reported problem.
* **Detailed Explanation:** In many IT departments, support agents mark tickets as resolved to meet SLA metrics even if the fix was partial. The `REOPENED` loop ensures accountability: only the employee who created the ticket (or an admin) can reopen it, restarting SLA tracking and logging the recurrence reason.
* **How it applies to TrackIT:** Directly addresses user satisfaction and service quality.

### 44. What is Mean Time to Resolution (MTTR), and how is it calculated in TrackIT?
* **Short Answer:** MTTR is the average elapsed time from ticket creation to verified resolution across all resolved tickets.
* **Detailed Explanation:**
  $$\text{MTTR} = \frac{\sum (\text{resolved\_at} - \text{created\_at})}{\text{Total Resolved Tickets}}$$
  In `DashboardService.get_summary`, TrackIT computes this in hours and displays it on the executive dashboard to measure operational efficiency.

### 45. Why does TrackIT record ticket status changes in a separate history table?
* **Short Answer:** To maintain an immutable audit trail of who changed status, what the previous state was, and when the change occurred.
* **Detailed Explanation:** Simply updating `status` on the `tickets` table overwrites prior state. If an agent prematurely closes a ticket, managers have no visibility into how long the ticket spent in triage versus active investigation. `ticket_status_history` provides complete transparency.
* **How it applies to TrackIT:** Rendered as an interactive timeline on the Ticket Details page.

---

## Part 10: Project-Specific & Behavioral Questions

### 46. What was the most technically challenging part of building TrackIT?
* **Answer:** "Designing the real-time SLA calculation engine combined with timezone consistency across database queries. In testing, I encountered an edge case where local system datetimes compared against UTC timestamps caused false-positive SLA breach flags. I resolved this by standardizing naive and timezone-aware datetime normalizations inside `SLAService.evaluate_sla_status`, backing it with comprehensive automated unit tests."

### 47. If you had another sprint, what feature would you build next?
* **Answer:** "I would implement automated Webhook integrations for Slack and Microsoft Teams so that when a `CRITICAL` ticket is raised or an SLA is `AT_RISK`, on-call engineers receive immediate notifications on their chat channels. I would also add file attachment support using AWS S3 presigned URLs for uploading diagnostic screenshots."

### 48. How do you ensure your REST APIs don't break frontend clients?
* **Answer:** "First, by versioning endpoints (`/api/v1`). Second, by enforcing strict Pydantic response models that guarantee consistent field names and types. Third, by writing integration tests with `TestClient` that validate the exact JSON response envelope contract (`success`, `data`, `error`)."

### 49. How did you structure your Git commits during development?
* **Answer:** "I followed the Conventional Commits specification with atomic, meaningful commit messages such as `feat: implement JWT authentication and RBAC guards`, `fix: resolve timezone disparity in SLA calculations`, and `test: add end-to-end ticket lifecycle test suite`. Each commit represents a single logical unit of work that passes tests."

### 50. Why are you interested in an Associate Product Engineer role?
* **Answer:** "Because I bridge both technical engineering and product thinking. In TrackIT, I didn't just write FastAPI routes and React tables; I researched the business problem of IT service management, identified persona pain points, designed SLA compliance formulas, and built a smart priority advisor to solve real organizational bottlenecks. I enjoy building software that solves concrete user problems with clean, scalable architecture."
