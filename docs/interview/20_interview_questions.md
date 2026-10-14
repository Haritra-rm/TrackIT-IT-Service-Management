# 20. Comprehensive Technical Interview Questions & Answers

### 1. What it is
A curated compendium of 30+ rigorous, high-yield technical and behavioral interview questions designed for an Associate Product Engineer / Software Engineer Fresher interview, mapped directly to TrackIT's codebase.

### 2. Why TrackIT uses it
To give the candidate complete confidence in explaining every design decision, trade-off, security mechanism, and algorithmic model in real-time under interview conditions.

### 3. High-Yield Interview Questions & Strong Answers

#### Architecture & Backend
1. **Q: Walk me through the architecture of TrackIT.**
   - **Answer:** *"TrackIT is built as a Clean Architecture Modular Monolith. The presentation layer is a React 18 SPA built with Vite. The API tier is FastAPI, using Pydantic v2 for request validation and serialization. The business logic lives in dedicated service classes like `TicketService` and `SLAService`. Data access is abstracted using the Repository Pattern with SQLAlchemy 2.0 ORM over a PostgreSQL database. Authentication is handled statelessly via JWT bearer tokens and verified at the route level via FastAPI's dependency injection."*

2. **Q: How does the ticket lifecycle Finite State Machine work, and how do you prevent invalid jumps?**
   - **Answer:** *"The lifecycle follows a directed graph: `OPEN -> ASSIGNED -> IN_PROGRESS -> RESOLVED -> CLOSED`, with a `RESOLVED -> REOPENED -> IN_PROGRESS` loop. In `TicketService`, we maintain a `VALID_TRANSITIONS` dictionary mapping each status to its allowed next states. If someone attempts an illegal transition—such as `OPEN -> CLOSED` or `CLOSED -> IN_PROGRESS`—the service catches the invalid edge and raises an `InvalidTransitionException` returning a 400 Bad Request. Every valid transition writes an immutable record into `ticket_status_history`."*

3. **Q: What is the N+1 query problem, and how did you resolve it?**
   - **Answer:** *"The N+1 problem occurs when fetching a list of parent entities (e.g. 20 tickets) and then querying related entities (creator and category) inside a loop, resulting in 1 + 20 queries. In `TicketRepository`, I used SQLAlchemy's `joinedload(Ticket.category)` and `joinedload(Ticket.creator)`, which generates a single SQL `LEFT OUTER JOIN` and fetches all data in 1 network roundtrip."*

#### Security & RBAC
4. **Q: How do you enforce Role-Based Access Control?**
   - **Answer:** *"RBAC is enforced authoritatively on the backend using FastAPI's dependency injection factory `require_role(allowed_roles)`. Even if an employee bypasses the frontend and issues a direct curl request to an administrative endpoint like `PATCH /api/v1/users/1/status`, the dependency intercepts the request, verifies the JWT claims, and terminates with an HTTP 403 Forbidden before reaching the route handler."*

5. **Q: How do you protect passwords and sensitive credentials?**
   - **Answer:** *"Passwords are never stored in plaintext. They are salted and hashed using Bcrypt with an adaptive work factor (12 rounds). Secrets like JWT keys are stored in environment variables, excluded from Git via `.gitignore`, and documented with safe placeholders in `.env.example`."*

#### Algorithms & Product Thinking
6. **Q: Explain your Smart Priority Recommendation Algorithm.**
   - **Answer:** *"To prevent priority inflation, I built a deterministic blast-radius scoring engine: $\text{Score} = \text{Impact Weight} + \text{Affected Users Bonus} + \text{Category Bonus} + \text{Blocker Penalty}$. If a ticket reports 25 affected users on a Network category with Department Blocked, the score reaches 50 ($\ge 35$), recommending `HIGH` priority with an 8-hour SLA deadline. The engine provides transparent, bulleted reasoning explaining the score."*

7. **Q: How is the SLA calculated, and how do you test it without waiting for hours?**
   - **Answer:** *"SLA thresholds are 4h for Critical, 8h for High, 24h for Medium, and 72h for Low. The engine calculates deadlines deterministically and evaluates real-time status (`ON_TRACK`, `AT_RISK`, `BREACHED`, `MET`) based on the ratio of elapsed time to total duration. For testing, `SLAService.evaluate_sla_status` accepts an optional `current_time` parameter, allowing our unit tests to simulate any point in time deterministically without fragile sleeps or system clock dependencies."*

#### Database & Scalability
8. **Q: How do you handle database migrations?**
   - **Answer:** *"We use Alembic for version-controlled database migrations. Every schema modification is recorded in a revision script in `backend/alembic/versions/` with explicit `upgrade()` and `downgrade()` functions, allowing seamless forward migrations and zero-downtime rollbacks in CI/CD pipelines."*

9. **Q: What happens to the dashboard if there are zero tickets in the database?**
   - **Answer:** *"Our `DashboardService` uses safe-division guards (`count / total * 100 if total > 0 else 0.0`), preventing any `ZeroDivisionError` or `NaN` outputs. The React frontend includes clean empty-state UI components with actionable prompts."*

10. **Q: How would you scale TrackIT from 100 to 100,000 users?**
    - **Answer:** *"I would scale in three steps: First, add an AWS RDS Read Replica to offload heavy dashboard analytics queries from the primary write instance. Second, introduce Redis caching for category lookups and session metadata with a 60-second TTL. Third, introduce PgBouncer for database connection pooling and deploy stateless FastAPI backend containers on AWS ECS Fargate behind an Application Load Balancer."*
