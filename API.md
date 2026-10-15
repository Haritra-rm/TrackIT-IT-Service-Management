# TrackIT — REST API Reference (v1)

Base URL: `/api/v1`  
Interactive OpenAPI UI: `http://localhost:8000/docs`  
ReDoc Reference: `http://localhost:8000/redoc`

---

## 1. Response Envelope Format

### Successful Response
All successful responses return HTTP `200 OK` or `201 Created` with standard envelope:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional descriptive status message"
}
```

### Standard Error Response
Errors follow a consistent structure matching the contract specified in Section 9:
```json
{
  "success": false,
  "error": {
    "code": "TICKET_NOT_FOUND",
    "message": "Ticket with ID 101 was not found",
    "details": null
  }
}
```

### Common HTTP Status Codes
* `200 OK`: Successful resource query or mutation.
* `201 Created`: Resource successfully created.
* `204 No Content`: Successful deletion.
* `400 Bad Request`: Invalid status transition or domain rule violation.
* `401 Unauthorized`: Missing, expired, or invalid JWT bearer token.
* `403 Forbidden`: Insufficient role permissions for target operation.
* `404 Not Found`: Target resource does not exist.
* `409 Conflict`: Unique constraint violation (e.g. duplicate email).
* `422 Unprocessable Content`: Schema validation error (e.g. short password, invalid email format).
* `500 Internal Server Error`: Unhandled system failure (trace logged internally).

---

## 2. Authentication Endpoints

| Method | Endpoint | Required Role | Summary |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Public | Register an employee account |
| `POST` | `/api/v1/auth/login` | Public | Authenticate credentials and receive JWT |
| `GET` | `/api/v1/auth/me` | Authenticated | Inspect current user identity and permissions |

#### Sample Login Request:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@trackit.internal", "password": "your_secure_password"}'
```

---

## 3. Tickets Endpoints

| Method | Endpoint | Required Role | Summary |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/tickets` | Authenticated | Create a new ticket (initial status `OPEN`) |
| `GET` | `/api/v1/tickets` | Authenticated | List tickets (search, filter, sort, paginate) |
| `POST` | `/api/v1/tickets/recommend-priority` | Authenticated | Rule-based priority advisor |
| `GET` | `/api/v1/tickets/{id}` | Authenticated* | Get ticket details (*Employee scoped to own) |
| `PUT` | `/api/v1/tickets/{id}` | Authenticated* | Update details (*Employee only if `OPEN`) |
| `DELETE` | `/api/v1/tickets/{id}` | `ADMIN` | Permanently remove ticket |
| `POST` | `/api/v1/tickets/{id}/assign` | `AGENT`, `ADMIN`| Assign ticket to agent (advances to `ASSIGNED`) |
| `POST` | `/api/v1/tickets/{id}/status` | `AGENT`, `ADMIN`| Advance ticket lifecycle status |
| `POST` | `/api/v1/tickets/{id}/resolve`| `AGENT`, `ADMIN`| Resolve ticket (requires `resolution_notes`) |
| `POST` | `/api/v1/tickets/{id}/close`  | Creator Only   | Verify and close resolved ticket |
| `POST` | `/api/v1/tickets/{id}/reopen` | Creator/Admin  | Reopen resolved/closed ticket |
| `GET` | `/api/v1/tickets/{id}/history`| Authenticated* | Get chronological status change history |
| `GET` | `/api/v1/tickets/{id}/comments`| Authenticated* | Get conversation thread messages |
| `POST` | `/api/v1/tickets/{id}/comments`| Authenticated* | Post comment to ticket thread |

#### Filter Query Parameters on `GET /api/v1/tickets`:
* `search`: Substring search across title, description, or ticket ID.
* `status`: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`, `REOPENED`.
* `priority`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
* `category_id`: Integer ID of category.
* `assigned_to`: Filter by support agent user ID.
* `sort_by`: `created_at`, `priority`, `due_at`, `status`.
* `sort_order`: `asc` or `desc`.
* `page`: Page number (1-indexed, default `1`).
* `page_size`: Number of items per page (default `20`, max `100`).

---

## 4. Users Endpoints

| Method | Endpoint | Required Role | Summary |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/users` | `AGENT`, `ADMIN`| List all users with filtering and pagination |
| `GET` | `/api/v1/users/agents` | `AGENT`, `ADMIN`| Get active support agents list for assignment |
| `GET` | `/api/v1/users/{id}` | Authenticated | Get user by ID |
| `PUT` | `/api/v1/users/{id}` | Authenticated* | Update user (*Non-admin can only update own name) |
| `PATCH`| `/api/v1/users/{id}/status` | `ADMIN` | Activate or deactivate user account |

---

## 5. Categories Endpoints

| Method | Endpoint | Required Role | Summary |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/categories` | Authenticated | List all categories (`?active_only=true`) |
| `POST` | `/api/v1/categories` | `ADMIN` | Create new category |
| `PUT` | `/api/v1/categories/{id}` | `ADMIN` | Update category details or active toggle |

---

## 6. Dashboard & Analytics Endpoints

| Method | Endpoint | Required Role | Summary |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/dashboard/summary` | Authenticated* | Get summary metrics (*scoped by role) |
| `GET` | `/api/v1/dashboard/tickets-by-status` | Authenticated | Distribution of tickets across statuses |
| `GET` | `/api/v1/dashboard/tickets-by-priority` | `AGENT`, `ADMIN` | Volume by severity priority |
| `GET` | `/api/v1/dashboard/tickets-by-category` | `AGENT`, `ADMIN` | Volume by issue category |
| `GET` | `/api/v1/dashboard/agent-performance` | `AGENT`, `ADMIN` | Individual agent throughput and SLA rating |
| `GET` | `/api/v1/audit-logs` | `ADMIN` | Chronological security audit logs |
