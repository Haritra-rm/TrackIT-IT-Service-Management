# 04. Data Structures & Algorithms (DSA) Concepts

### 1. What it is
Data Structures and Algorithms (DSA) are the foundational principles of organizing data efficiently in memory and designing computational procedures with optimal time and space complexity ($O(1)$, $O(\log N)$, $O(N)$).

### 2. Why TrackIT uses it
Enterprise issue tracking involves state transitions, priority calculations, full-text searching, and dashboard analytics. Applying deliberate DSA choices prevents performance degradation as the ticket volume scales.

### 3. How it works
- **Finite State Machine (Directed Graph / Adjacency List)**: The ticket lifecycle is represented as a directed graph where vertices are ticket statuses (`OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `REOPENED`) and edges are valid transitions. We use an in-memory hash map (dictionary) where key lookup is $O(1)$ to validate whether transition from $S_1$ to $S_2$ is valid:
  ```python
  allowed_next = VALID_TRANSITIONS.get(ticket.status, [])
  if target_status not in allowed_next:
      raise InvalidTransitionException(...)
  ```
- **Rule-Based Scoring Algorithm**: Computes priority using a weighted blast-radius formula in $O(1)$ constant time:
  $$\text{Score} = \text{Impact} + \text{UserBlastBonus} + \text{CategoryWeight} + \text{BlockerPenalty}$$
- **Time Complexity in Sorting and Paging**: Repository queries use SQL B-Tree indexes ($O(\log N)$) on `created_at`, `status`, and `priority`, ensuring limit/offset pagination runs in bounded time rather than scanning all rows ($O(N)$).
- **In-Memory Hash Sets for RBAC**: Allowed roles are represented as Python lists and sets for $O(1)$ authorization membership checks (`user.role in allowed_roles`).

### 4. Where it exists in the code
- State Machine Directed Graph: [`backend/app/services/ticket_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/ticket_service.py#L43-L52)
- Constant-Time Priority Scoring: [`backend/app/services/priority_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/priority_service.py)
- Aggregation Math & Ratios: [`backend/app/services/dashboard_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/dashboard_service.py)

### 5. Alternative approach
- Storing allowed transitions in database tables and performing dynamic relational joins on every status change.
- Hardcoded procedural `if/else` ladders sprawled across multiple controller functions.

### 6. Why this approach was selected
An in-memory dictionary acting as an adjacency list provides instantaneous $O(1)$ time complexity with zero database I/O latency. It centralizes the lifecycle rules in a single immutable constant, preventing transition bugs and race conditions.

### 7. Likely interviewer question
*"How did you model the ticket lifecycle, and what is the time complexity of validating a status transition?"*

### 8. Simple fresher-level answer
*"I modeled the ticket lifecycle as a Directed Graph using an Adjacency List implemented as a Python dictionary. The vertices represent the statuses (such as OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, and REOPENED), and the dictionary values are lists of allowed next states. Checking if a status change is permitted is an $O(1)$ dictionary key lookup followed by an $O(K)$ array search, where $K \le 3$. This makes transition validation practically instantaneous and guarantees invalid jumps like CLOSED to IN_PROGRESS are rejected."*
