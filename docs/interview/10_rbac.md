# 10. Role-Based Access Control (RBAC) & Security

### 1. What it is
Role-Based Access Control (RBAC) is an access authorization model that assigns system permissions to abstract roles (`EMPLOYEE`, `SUPPORT_AGENT`, `ADMIN`) rather than individual users, restricting system operations according to organizational duties.

### 2. Why TrackIT uses it
In an enterprise IT platform, staff must never view tickets filed by colleagues (which may contain confidential HR or payroll queries), support agents must have operational access across ticket queues but cannot modify system configuration or delete users, and only administrators should alter user privileges or review compliance audit logs.

### 3. How it works
- **FastAPI Role Factories**: We define a higher-order dependency factory `require_role(allowed_roles: List[str])`:
  ```python
  def require_role(allowed_roles: List[str]):
      def role_checker(current_user: User = Depends(get_current_user)) -> User:
          if current_user.role not in allowed_roles:
              raise ForbiddenException(f"Access denied. Required roles: {allowed_roles}")
          return current_user
      return role_checker
  ```
- **Hierarchical Access Levels**:
  - `require_admin`: Only `ADMIN` allowed.
  - `require_support_or_admin`: Both `SUPPORT_AGENT` and `ADMIN` allowed.
  - `require_any_authenticated`: Any active logged-in user.
- **Data-Level Security (Row-Level Tenancy)**: In `ticket_service.py`, even if an employee is authenticated, queries filter strictly by `ticket.created_by == current_user.id`. Accessing another employee's ticket returns `403 Forbidden`.

### 4. Where it exists in the code
- RBAC Dependency Factory: [`backend/app/core/dependencies.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/core/dependencies.py)
- Route Annotations: [`backend/app/routes/users.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/routes/users.py), [`backend/app/routes/tickets.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/routes/tickets.py)
- Domain Ownership Logic: [`backend/app/services/ticket_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/ticket_service.py)
- Comprehensive Matrix: [`docs/interview/rbac.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/docs/interview/rbac.md)

### 5. Alternative approach
- Attribute-Based Access Control (ABAC) evaluating complex dynamic policies (location, time-of-day, department hierarchy).
- Discretionary Access Control (DAC) where creators assign permissions per resource.
- Frontend-only authorization (hiding buttons in React).

### 6. Why this approach was selected
Frontend-only authorization is easily bypassed via direct HTTP calls. ABAC introduces excessive policy engine complexity with high latency for standard three-role enterprise environments. RBAC combined with row-level ownership checks provides the optimal balance of strict security, maintainability, and execution speed.

### 7. Likely interviewer question
*"What prevents an employee from accessing another employee's private ticket by manually altering the ticket ID in the browser URL (`/tickets/99`)?"*

### 8. Simple fresher-level answer
*"Even though the React frontend requests `/api/v1/tickets/99`, the backend independently validates permissions. When `get_ticket(99)` is invoked in `TicketService`, it inspects `current_user.role`. If the user is an `EMPLOYEE` and `ticket.created_by != current_user.id`, the service immediately terminates the request and raises a `ForbiddenException` (403 Forbidden). The user never receives the confidential ticket payload."*
