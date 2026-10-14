# Interview Guide: 03. Database Design & Optimization

## What is the Database Design?
TrackIT utilizes a normalized **PostgreSQL** relational schema containing 6 core tables: `users`, `categories`, `tickets`, `comments`, `ticket_status_history`, and `audit_logs`. The database is modeled in **Third Normal Form (3NF)** with explicit foreign key constraints, cascading deletes where appropriate, and performance B-Tree indexes.

## Why was PostgreSQL chosen?
PostgreSQL was selected for its robust ACID compliance, advanced indexing capabilities (B-Tree, Hash, GIN), rich timestamp with timezone support, and strong relational integrity guarantees. For local zero-dependency testing, SQLAlchemy enables interchangeable fallback to SQLite without changing schema code.

## How it works in TrackIT
* **Normalization:** User information is normalized in `users`, preventing redundant email and name strings in tickets, comments, and audit tables.
* **Referential Integrity:** `comments` and `ticket_status_history` reference `tickets.id` with `ON DELETE CASCADE`. If a ticket is pruned, orphaned comments are automatically cleaned up by the database engine.
* **History Auditing:** Rather than only overwriting `status` in the ticket record, every transition is written to `ticket_status_history` (`old_status`, `new_status`, `changed_by`, `changed_at`), providing an immutable historical log.

## Indexing Rationale & Algorithmic Complexity

| Column | Index Type | DSA Complexity | Practical Benefit |
| :--- | :--- | :--- | :--- |
| `users.email` | B-Tree Unique | $O(\log N)$ | Instant authentication seeks during user login. |
| `tickets.status` | B-Tree | $O(\log N)$ | Accelerates agent workbench queue queries (`WHERE status = 'OPEN'`). |
| `tickets.created_by` | B-Tree | $O(\log N)$ | Enforces fast employee filtering without full table scan ($O(N)$). |
| `tickets.due_at` | B-Tree | $O(\log N)$ | Optimizes SLA breach warning scans. |
| `tickets.created_at` | B-Tree | $O(\log N)$ | Enables indexed pagination (`ORDER BY created_at DESC`). |

## Interview Questions & Answers

### Q: "What is the N+1 problem, and how did you prevent it in TrackIT?"
**Answer:** "The N+1 problem occurs when fetching a list of $N$ parent records (e.g. 20 tickets) causes the ORM to trigger $N$ additional separate SQL queries to load related child records (e.g. the creator or category for each ticket). In TrackIT, I solved this by using SQLAlchemy's `joinedload` option in `TicketRepository`. This compiles a single SQL `LEFT OUTER JOIN`, reducing 41 database round trips down to 1 single network query."

### Q: "Why is the schema in 3NF instead of NoSQL/Document DB?"
**Answer:** "IT Service Management data is inherently relational: users create tickets, tickets have categories, agents are assigned tickets, and comments belong to tickets. In a document store like MongoDB, denormalizing user data inside tickets would require updating multiple documents if an agent changes their name or email. 3NF prevents data anomalies, eliminates redundancy, and ensures strong ACID consistency."
