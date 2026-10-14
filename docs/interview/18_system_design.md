# 18. System Design & Scalability Principles

### 1. What it is
System Design is the discipline of architecting software components, data stores, network topologies, and caching tiers to satisfy functional requirements while scaling across throughput, latency, reliability, and cost boundaries.

### 2. Why TrackIT uses it
As an enterprise expands from a 100-person startup to a 50,000-employee global corporation, read and write query volume multiplies by orders of magnitude. The system design must accommodate growth without performance bottlenecks or downtime.

### 3. How it works
- **Phase 1: 100 to 1,000 Users (Current Baseline)**:
  - Single modular monolith container.
  - Relational database with B-Tree indexes on foreign keys, status, and creation timestamps.
  - In-process SLA calculations and connection pooling.
- **Phase 2: 10,000 Users (Mid-Market Scale)**:
  - Horizontal scaling of FastAPI stateless API replicas behind an Application Load Balancer.
  - Database connection pooling managed via PgBouncer.
  - Redis cache for frequently accessed read-heavy reference data (active IT categories, user permission roles, static lookups) with 15-minute TTL.
  - Read-Replica offloading: Analytics and Dashboard queries route to an AWS RDS Read Replica, preserving write capacity on the primary DB instance.
- **Phase 3: 1,000,000 Users (Enterprise Global Scale)**:
  - Event-driven asynchronous architecture: Ticket creation and status changes publish domain events to Apache Kafka or RabbitMQ.
  - Dedicated background worker pools consume events to compute SLAs, dispatch email/Slack notifications, and build search indexes.
  - Database sharding by `organization_id` or table partitioning by `created_at` (quarterly partition pruning).
  - OpenSearch / Elasticsearch cluster for full-text search across millions of ticket descriptions and resolution notes.

### 4. Where it exists in the code
- Scalable Repository & Database Pooling: [`backend/app/database/connection.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/database/connection.py)
- Stateless Request Handlers: [`backend/app/routes/`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/routes/)
- System Design Scaling Discussion: [`docs/interview/23_system_design_scaling.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/docs/interview/23_system_design_scaling.md)

### 5. Alternative approach
- Over-engineering from Day 1: Implementing microservices, Kafka event streams, Redis clusters, and database sharding for a fresh system with 500 tickets.

### 6. Why this approach was selected
Premature distributed systems add massive infrastructure bills, distributed transaction failures, network debugging latency, and operational fragility. Designing a clean modular monolith with clear boundaries allows seamless vertical scaling today and evolutionary horizontal migration tomorrow.

### 7. Likely interviewer question
*"What is the first bottleneck TrackIT would hit if ticket volume increased 50x, and how would you resolve it?"*

### 8. Simple fresher-level answer
*"The first bottleneck would be database read contention on the `tickets` table, specifically caused by the Admin Dashboard and reports running aggregate queries (`COUNT`, `GROUP BY`) while users concurrently insert new tickets and comments. I would resolve this by:
1. Adding an AWS RDS Read Replica so dashboard and report reads are routed away from the primary write database.
2. Introducing a Redis cache for summary KPI counts with a 60-second cache invalidation.
3. Adding PgBouncer connection pooling to reuse database connections efficiently without exhausting PostgreSQL's max connection limits."*
