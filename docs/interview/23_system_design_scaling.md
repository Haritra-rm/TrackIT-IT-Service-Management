# 23. System Design & Evolutionary Scaling Strategy

This document outlines the evolutionary scaling roadmap for TrackIT across three tiers:
1. **Tier 1: 100 to 1,000 Users** (Internal Startup / Mid-Sized Enterprise — Current State)
2. **Tier 2: 10,000 to 50,000 Users** (Growing Enterprise / Multi-Office Organization)
3. **Tier 3: 1,000,000+ Users** (Global Enterprise / Multi-Tenant SaaS Platform)

---

## High-Level Architectural Comparison Table

| Dimension | Tier 1 (100–1,000 Users) | Tier 2 (10,000–50,000 Users) | Tier 3 (1,000,000+ Users) |
| :--- | :--- | :--- | :--- |
| **Architecture** | Modular Monolith | Modular Monolith + Read Replicas | Microservices / Event-Driven |
| **Compute** | Single container / VM | Horizontal ECS Fargate Tasks | Kubernetes (EKS) Auto-scaled pods |
| **Load Balancing**| Nginx Reverse Proxy | AWS Application Load Balancer (ALB) | Cloudflare / AWS Global Accelerator + ALB |
| **Database** | PostgreSQL Single Instance | PostgreSQL Multi-AZ + Read Replicas | Sharded PostgreSQL / Table Partitioning |
| **Connection Pool**| SQLAlchemy In-Process Pool | PgBouncer Dedicated Pooler | Distributed PgBouncer Cluster |
| **Caching Tier** | In-Memory Python Caches | Redis Cluster (Lookups & Sessions) | Multi-Region Redis / Memcached + Edge Cache |
| **Static Assets** | Local Nginx Container | AWS S3 + Amazon CloudFront CDN | Multi-region CDN with Edge Compute |
| **Async Jobs** | Synchronous within FastAPI | Celery / Redis Worker Pool | Apache Kafka / AWS SQS Event Consumers |
| **Attachments** | Local disk storage | Amazon S3 with Pre-signed URLs | S3 Multi-Region Replication + ClamAV Virus Scan |
| **Search** | SQL `ILIKE` with B-Tree indexes | PostgreSQL Full-Text Search (tsvector) | Elasticsearch / OpenSearch Distributed Cluster |
| **Rate Limiting** | None / Basic Nginx limits | Redis Token Bucket Algorithm | Cloudflare WAF + API Gateway Throttling |
| **Observability** | Structured console logs | AWS CloudWatch + Prometheus/Grafana | Datadog / OpenTelemetry Distributed Tracing |

---

## Detailed Architectural Evolution

### Tier 1: 100 to 1,000 Users (The Baseline)
- **Bottlenecks**: None at this scale.
- **Implementation**:
  - A single FastAPI container running with 2–4 Uvicorn workers.
  - PostgreSQL instance with B-Tree indexes on `tickets(status, priority, created_by, created_at)`.
  - SQLAlchemy connection pool sized to 20 connections with `pool_pre_ping=True` to detect dropped connections.
  - React frontend served via Nginx.

---

### Tier 2: 10,000 to 50,000 Users (Scaling the Monolith)
- **Bottlenecks Encountered**:
  1. Database connection exhaustion when multiple backend containers spawn.
  2. Heavy reporting and dashboard queries degrading transactional write performance.
  3. Slow asset delivery for international remote workers.
- **Architectural Enhancements**:
  1. **Horizontal Backend Scaling**: Deploy multiple stateless FastAPI container tasks behind an AWS Application Load Balancer (ALB) with CPU/Memory auto-scaling policies.
  2. **Dedicated Connection Pooling**: Deploy **PgBouncer** in front of PostgreSQL. Instead of each backend container maintaining 20 persistent connections, PgBouncer multiplexes thousands of virtual client connections into a compact pool of 50 physical database connections.
  3. **Read Replicas**: Configure an AWS RDS Read Replica. In `database/connection.py`, route `SELECT` queries from `dashboard_service.py` to the read replica, reserving the primary database purely for `INSERT`, `UPDATE`, and `DELETE` transactions.
  4. **Redis Caching**:
     - Cache the active categories list (`GET /api/v1/categories`) with a 1-hour TTL.
     - Cache dashboard aggregate summaries with a 60-second TTL.
  5. **Static CDN**: Offload React assets to AWS S3 and serve them via CloudFront CDN at edge locations globally.

---

### Tier 3: 1,000,000+ Users (Global SaaS Scale)
- **Bottlenecks Encountered**:
  1. Monolithic PostgreSQL table hitting tens of millions of rows, slowing down sequential scans.
  2. Synchronous notifications (emails, webhooks) slowing down API latency.
  3. Complex multi-word search queries overwhelming relational indexes.
- **Architectural Enhancements**:
  1. **Event-Driven Asynchronous Pipeline**:
     - When an issue is filed, the API writes to PostgreSQL and immediately publishes a `ticket.created` domain event to **Apache Kafka**.
     - Specialized worker microservices consume the event asynchronously to:
       - Send Slack and email alerts.
       - Index the ticket into an **OpenSearch** cluster for sub-50ms typo-tolerant full-text search.
       - Evaluate external SLA escalation policies.
  2. **Database Table Partitioning & Sharding**:
     - Partition the `tickets` table by date (`PARTITION BY RANGE (created_at)`). Queries filtering for recent tickets only scan the current quarter's partition, ignoring millions of historical archived records.
     - For multi-tenant SaaS, shard data horizontally by `organization_id` using Citus Data or tenant isolation databases.
  3. **Rate Limiting & DDoS Protection**:
     - Enforce a Token Bucket algorithm via Redis at the API Gateway level (e.g., maximum 100 requests per minute per IP) to prevent denial-of-service scraping.
  4. **Distributed Tracing**:
     - Implement OpenTelemetry with Jaeger or Datadog, injecting a trace ID across HTTP requests, Kafka events, and database spans to track latency anomalies across distributed services.
