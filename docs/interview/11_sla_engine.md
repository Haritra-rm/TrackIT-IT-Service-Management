# 11. Service Level Agreement (SLA) Engine

### 1. What it is
The SLA (Service Level Agreement) Engine is the business subsystem responsible for calculating ticket resolution deadlines and evaluating real-time compliance states (`ON_TRACK`, `AT_RISK`, `BREACHED`, `MET`).

### 2. Why TrackIT uses it
In IT Service Management, organizations commit to resolution targets based on issue criticality. Without an automated SLA engine, tickets languish indefinitely without accountability, leading to downtime and breached customer agreements.

### 3. How it works
- **SLA Windows by Priority**:
  - `CRITICAL`: 4 hours
  - `HIGH`: 8 hours
  - `MEDIUM`: 24 hours
  - `LOW`: 72 hours
- **Deterministic Due Date Calculation**:
  $$\text{due\_at} = \text{created\_at} + \Delta t_{\text{priority}}$$
- **Dynamic Real-Time Evaluation Algorithm**:
  Rather than running asynchronous cron pollers that drift out of sync, SLA compliance is computed dynamically on read:
  $$\text{Total Duration} = \text{due\_at} - \text{created\_at}$$
  $$\text{Elapsed Ratio} = \frac{\text{Current Time} - \text{created\_at}}{\text{Total Duration}}$$
  - **`MET`**: Ticket is `RESOLVED` or `CLOSED`, and $\text{resolved\_at} \le \text{due\_at}$.
  - **`BREACHED`**: Ticket is unresolved and $\text{Current Time} > \text{due\_at}$, or resolved after $\text{due\_at}$.
  - **`AT_RISK`**: Ticket is unresolved, $\text{Current Time} \le \text{due\_at}$, and $\text{Elapsed Ratio} \ge 75\%$ (or $\le 1$ hour remaining).
  - **`ON_TRACK`**: Ticket is unresolved and $\text{Elapsed Ratio} < 75\%$.
- **Controllable Clock**: The engine accepts an optional `current_time` parameter, allowing 100% deterministic unit testing without fragile sleep or mocking real system clocks.

### 4. Where it exists in the code
- SLA Service: [`backend/app/services/sla_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/sla_service.py)
- Configured SLA Hours: [`backend/app/core/config.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/core/config.py)
- SLA Unit Tests: [`backend/tests/unit/test_sla.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/tests/unit/test_sla.py)
- Frontend SLA Badge: [`frontend/src/components/SlaBadge.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/components/SlaBadge.jsx)

### 5. Alternative approach
- Running a background Celery / Redis cron job every 5 minutes that iterates through all tickets and writes static `sla_status` strings into the database table.

### 6. Why this approach was selected
Periodic background polling creates stale data latency (a ticket could breach 4 minutes before a cron job detects it), introduces database write lock contention across thousands of rows, and requires Redis and Celery worker infrastructure. Computing SLA status dynamically on read guarantees 100% real-time accuracy with zero background infrastructure overhead.

### 7. Likely interviewer question
*"Why calculate SLA status dynamically on read instead of storing it as a static column in the database?"*

### 8. Simple fresher-level answer
*"Because SLA status is a function of time relative to the current moment. If we stored it as a static database column, a ticket created at 9:00 AM with a 4-hour SLA would say 'ON_TRACK' in the database even at 3:00 PM unless an external cron job continuously ran and updated it. By computing it dynamically on retrieval, the user always sees real-time, accurate compliance metrics with zero background worker lag."*
