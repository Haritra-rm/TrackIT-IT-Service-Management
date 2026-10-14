# 22. Architectural Defense & Technology Selection Q&A

This document contains direct, interview-tested answers for common architectural "Why did you choose X?" questions for an Associate Product Engineer interview.

---

### 1. Why FastAPI?
**Answer:** *"I chose FastAPI over Flask and Django because it combines high performance (comparable to Go and NodeJS) with modern Python type hints and Pydantic v2 validation. FastAPI automatically validates incoming request schemas, eliminates boilerplate error-handling code, and auto-generates interactive OpenAPI documentation at `/docs`. Its dependency injection system is uniquely suited for enforcing server-side Role-Based Access Control cleanly before route handlers execute."*

### 2. Why PostgreSQL?
**Answer:** *"TrackIT has strict relational dependencies and ACID transaction requirements. For example, assigning a ticket must atomically update the ticket's assignee, record a row in `ticket_status_history`, and write an entry in `audit_logs` in a single transaction. PostgreSQL provides robust relational integrity, B-Tree indexes for fast pagination, powerful aggregation functions for KPI metrics, and proven enterprise reliability."*

### 3. Why SQLAlchemy?
**Answer:** *"SQLAlchemy 2.0 provides an enterprise-grade Object Relational Mapper that abstracts raw SQL dialect differences while protecting against SQL injection vulnerabilities through automatic parameter binding. More importantly, it provides advanced query optimization tools like `joinedload()`, which allowed me to eliminate the classic N+1 query problem by issuing clean SQL `LEFT OUTER JOIN`s."*

### 4. Why React?
**Answer:** *"TrackIT requires interactive operational workbenches where status badges, countdown timers, search filters, and comments update dynamically without jarring full-page browser reloads. React's virtual DOM reconciliation updates only the specific table row or badge that changed. Its component-driven architecture allowed us to build reusable design tokens (`StatusBadge`, `PriorityBadge`, `StatCard`) shared across Employee, Agent, and Admin dashboards."*

### 5. Why JWT?
**Answer:** *"JSON Web Tokens allow stateless authentication. Unlike traditional session cookies stored in server memory or a centralized Redis instance, a signed JWT carries the user's identity and role claims inside the token itself. This means our FastAPI backend containers remain completely stateless and can scale horizontally behind a load balancer without needing sticky sessions or centralized session cache lookups."*

### 6. Why RBAC?
**Answer:** *"In an IT service platform, employees must never view confidential tickets filed by other staff (such as payroll discrepancies or disciplinary inquiries). Role-Based Access Control provides a clear, maintainable security model that decouples permissions from individual user IDs. By establishing three distinct personas—`EMPLOYEE`, `SUPPORT_AGENT`, and `ADMIN`—we enforce strict access boundaries authoritatively on the backend."*

### 7. Why Repository / Service Layer Separation?
**Answer:** *"Separating Repositories from Services enforces the Single Responsibility Principle. Repositories handle only database queries and persistence details (SQLAlchemy). Services handle only pure business logic (state machine transitions, SLA evaluations, blast-radius scoring). This separation makes unit testing straightforward: we can test business logic by mocking repositories without needing a live database connection."*

### 8. Why Modular Monolith instead of Microservices?
**Answer:** *"Microservices introduce distributed system failure modes: network latency, distributed transaction complexity (two-phase commits / Saga pattern), service discovery overhead, and difficult local debugging. For an internal ITSM platform serving an organization up to 50,000 users, a Modular Monolith offers all the clean boundary benefits of microservices with the deployment simplicity of a single container."*

### 9. Why Docker?
**Answer:** *"Docker eliminates environment discrepancies between Windows, macOS, Linux, and CI/CD runners. By encapsulating Python dependencies, Node build tools, and Nginx configurations into container images, onboarding a new engineer or deploying to a cloud server is reduced to a single command: `docker compose up --build`."*

### 10. Why Pytest?
**Answer:** *"Pytest is the industry standard for Python testing. Its fixture architecture allowed me to build isolated transaction rollback fixtures, ensuring our 48 automated tests execute against an isolated database without polluting test state. It integrates seamlessly with FastAPI's `TestClient` for high-speed API testing."*

### 11. Why GitHub Actions?
**Answer:** *"GitHub Actions provides zero-friction CI/CD directly inside the repository. On every pull request, our workflow automatically validates code formatting, runs the complete Pytest suite, and verifies the frontend production build. This guarantees that broken code or failing tests can never be merged into the `main` branch."*

### 12. How would you deploy TrackIT to Production?
**Answer:** *"I would deploy TrackIT on AWS:
- **Frontend**: Compiled static assets deployed to an Amazon S3 bucket fronted by Amazon CloudFront CDN with SSL termination via ACM.
- **Backend**: Containerized FastAPI service deployed on AWS ECS (Elastic Container Service) with AWS Fargate serverless tasks running behind an Application Load Balancer.
- **Database**: Amazon RDS PostgreSQL in a Multi-AZ deployment for automatic failover.
- **Secrets**: Stored securely in AWS Secrets Manager."*

### 13. How would you scale TrackIT for 100,000 users?
**Answer:** *"For 100,000 users, I would introduce three targeted enhancements:
1. **Read Replicas**: Route all read-heavy dashboard and reporting queries to an AWS RDS Read Replica, preserving 100% of the primary database's I/O capacity for write transactions.
2. **Redis Caching**: Cache static reference data (categories, agent rosters) and summary dashboard counts with a 60-second TTL.
3. **Asynchronous Background Workers**: Offload email/Slack notification dispatch and search indexing to Celery or AWS SQS worker queues so API response times remain under 50 milliseconds."*
