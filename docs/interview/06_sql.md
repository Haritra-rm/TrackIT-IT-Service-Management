# 06. SQL & Database Query Optimization

### 1. What it is
SQL (Structured Query Language) is the declarative language used to define schemas, manipulate data, and query relational databases using filtering, aggregation, grouping, and relational joins.

### 2. Why TrackIT uses it
The analytics dashboards, KPI computations (Mean Time to Resolution, SLA breach rates), and search filters require complex aggregations and joins across multiple tables (`tickets`, `comments`, `users`, `categories`).

### 3. How it works
- **Solving the N+1 Query Problem**: In basic ORM queries, fetching 20 tickets and then accessing `ticket.creator.name` or `ticket.category.name` in a loop triggers 1 initial query + 20 secondary queries (21 roundtrips). TrackIT eliminates this using SQLAlchemy's `joinedload()`:
  ```python
  self.db.query(Ticket).options(
      joinedload(Ticket.category),
      joinedload(Ticket.creator),
      joinedload(Ticket.assignee),
  )
  ```
  This generates a single `LEFT OUTER JOIN` in SQL, reducing network roundtrips from $N+1$ to 1.
- **Aggregations & Grouping (`GROUP BY`)**: Status and category distributions are computed directly in SQL using `func.count()`:
  ```sql
  SELECT status, COUNT(id) AS count
  FROM tickets
  WHERE created_by = :user_id
  GROUP BY status;
  ```
- **Parameterized Queries**: All ORM calls and dynamic filters use SQL bind parameters (`:param_1`), guaranteeing 100% protection against SQL injection attacks.

### 4. Where it exists in the code
- Eager Loading Queries: [`backend/app/repositories/ticket_repository.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/repositories/ticket_repository.py)
- Aggregation & KPI SQL: [`backend/app/services/dashboard_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/dashboard_service.py)

### 5. Alternative approach
- Fetching all database rows into Python memory and doing loops, list comprehensions, and dictionary grouping inside Python.
- Writing raw concatenated SQL strings (`f"SELECT * FROM tickets WHERE title = '{search}'"`).

### 6. Why this approach was selected
Fetching raw tables into Python memory causes severe memory bloat and high network transfer times when scaling to hundreds of thousands of tickets. Running `COUNT()` and `GROUP BY` directly on the database engine takes advantage of PostgreSQL's optimized C query planner and cached buffer pools. Raw string concatenation creates dangerous SQL injection vulnerabilities.

### 7. Likely interviewer question
*"What is the N+1 query problem, and how did you prevent it in TrackIT?"*

### 8. Simple fresher-level answer
*"The N+1 problem occurs when an application executes 1 query to fetch a list of parent records (e.g. 20 tickets), and then executes N additional individual queries to fetch each ticket's foreign relations (such as creator and category). In TrackIT, I prevented this by using SQLAlchemy's `joinedload()`, which instructs the ORM to issue a single SQL `LEFT OUTER JOIN`. This fetches the tickets and their related creator and category rows in a single network round-trip."*
