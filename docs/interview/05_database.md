# 05. Database Design & Relational Modeling

### 1. What it is
Database design is the systematic structuring of enterprise data into normalized tables with defined primary keys, foreign key constraints, indexes, and referential integrity rules in a relational database management system (PostgreSQL).

### 2. Why TrackIT uses it
Support tickets, comments, and audit histories have strict relational dependencies. For instance, a comment cannot exist without an associated ticket and user. Using a normalized relational model prevents data duplication, anomalies, and orphaned records.

### 3. How it works
- **Schema Normalization (3NF)**:
  - `users`: User identity, hashed passwords, roles (`EMPLOYEE`, `SUPPORT_AGENT`, `ADMIN`), active status.
  - `categories`: IT issue domains (`Hardware`, `Software`, `Network`, `Access`, etc.).
  - `tickets`: The core entity containing `category_id`, `created_by`, `assigned_to`, lifecycle timestamps (`created_at`, `due_at`, `resolved_at`, `closed_at`), priority, status, and resolution notes.
  - `comments`: Ticket-level discussion threads (`ticket_id` FK with `CASCADE` delete).
  - `ticket_status_history`: Chronological audit trail of all state transitions (`old_status`, `new_status`, `changed_by`, `changed_at`).
  - `audit_logs`: System-wide forensic trail of actions (`USER_REGISTERED`, `TICKET_ASSIGNED`, etc.).
- **Relationships**:
  - `User` 1:N `Ticket` (as `creator`)
  - `User` 1:N `Ticket` (as `assignee`)
  - `User` 1:N `Comment`
  - `Ticket` 1:N `Comment` (with cascade delete)
  - `Ticket` 1:N `TicketStatusHistory` (with cascade delete)
  - `Category` 1:N `Ticket`
- **Indexing Strategy**:
  - `users.email` (Unique B-tree index for $O(\log N)$ login lookups).
  - `tickets.status` and `tickets.priority` (Indexed for fast filter queries).
  - `tickets.created_by` and `tickets.assigned_to` (Indexed for fast role-scoped queries).
  - `tickets.created_at` and `tickets.due_at` (Indexed for chronological sorting and SLA monitoring).

### 4. Where it exists in the code
- Database Models: [`backend/app/models/`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/models/)
- Alembic Migration Revisions: [`backend/alembic/versions/6467e4d9f142_initial_schema_setup.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/alembic/versions/6467e4d9f142_initial_schema_setup.py)
- Database Documentation: [`DATABASE.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/DATABASE.md)

### 5. Alternative approach
- NoSQL document store (MongoDB).
- Storing entire ticket history and comments as nested JSON blobs inside a single NoSQL document.

### 6. Why this approach was selected
While NoSQL allows rapid schema prototyping, it lacks ACID transactional guarantees, foreign key enforcement, and relational integrity. In an enterprise ticketing system, if a ticket assignment succeeds but the status history fails, the database must roll back atomically. PostgreSQL ensures strict referential integrity and provides powerful indexing and aggregation capabilities.

### 7. Likely interviewer question
*"Why did you put indexes on `tickets.status`, `tickets.created_by`, and `tickets.created_at`?"*

### 8. Simple fresher-level answer
*"Without indexes, whenever an employee opens their dashboard or filters by status, the database performs a sequential full-table scan, reading every row from disk ($O(N)$). By adding B-tree indexes on `status`, `created_by`, and `created_at`, the query engine performs a binary tree lookup in $O(\log N)$ time. This ensures that even with 500,000 tickets, filtering by 'OPEN' or searching for an employee's tickets executes in milliseconds."*
