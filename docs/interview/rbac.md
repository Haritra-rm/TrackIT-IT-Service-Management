# TrackIT — Role-Based Access Control (RBAC) Security Matrix

This document details the backend-authoritative Role-Based Access Control (RBAC) security enforcement across TrackIT. Permissions are verified cryptographically in FastAPI route dependencies and service business logic—never relying solely on frontend UI hiding.

---

## 1. System Roles Overview

| Role | Target Persona | Scope of Authority |
| :--- | :--- | :--- |
| **`EMPLOYEE`** | Organization staff | Self-service issue reporting. Can create, view, comment on, and reopen their own tickets. Cannot view other users' tickets, assign tickets, manage users, or modify system settings. |
| **`SUPPORT_AGENT`** | IT Helpdesk technicians | Operational ticket triage, investigation, troubleshooting, status updates, and resolution notes. Access to company-wide ticket queues and operational reports. |
| **`ADMIN`** | IT Operations managers | Full administrative governance: user lifecycle management, category administration, queue management, reassignments, hard deletes, system KPI dashboards, and immutable audit logs. |

---

## 2. Comprehensive RBAC Authorization Matrix

| Endpoint / Action | Method | Role | Allowed? | Enforcement Mechanism & Rationale |
| :--- | :---: | :--- | :---: | :--- |
| `/api/v1/auth/register` | `POST` | Public / Any | **YES** | Allows employee self-registration. Defaults to `EMPLOYEE` role. |
| `/api/v1/auth/login` | `POST` | Public / Any | **YES** | Validates credentials and returns JWT bearer token. |
| `/api/v1/auth/me` | `GET` | All Authenticated | **YES** | Returns calling user's own profile identity. Rejects inactive accounts with 403. |
| `/api/v1/users` | `GET` | `EMPLOYEE` | **NO (403)** | `require_support_or_admin` blocks staff from scraping enterprise employee directories. |
| `/api/v1/users` | `GET` | `SUPPORT_AGENT` | **YES** | Needed to identify staff when triaging and resolving issues. |
| `/api/v1/users` | `GET` | `ADMIN` | **YES** | Full user management and staff directory inspection. |
| `/api/v1/users/agents` | `GET` | `EMPLOYEE` | **NO (403)** | `require_support_or_admin` prevents exposure of internal agent roster. |
| `/api/v1/users/agents` | `GET` | `SUPPORT_AGENT` | **YES** | Required for internal ticket assignment and queue handoffs. |
| `/api/v1/users/agents` | `GET` | `ADMIN` | **YES** | Required for agent oversight and workload distribution. |
| `/api/v1/users/{id}` | `GET` | `EMPLOYEE` | **Conditional** | Can view own profile; viewing other profiles blocked if employee. |
| `/api/v1/users/{id}` | `GET` | `SUPPORT_AGENT` | **YES** | Can inspect user details of ticket creators. |
| `/api/v1/users/{id}` | `GET` | `ADMIN` | **YES** | Full user inspection. |
| `/api/v1/users/{id}` | `PUT` | `EMPLOYEE` | **Conditional** | Can update own name/email; cannot change role or active status (403). |
| `/api/v1/users/{id}` | `PUT` | `SUPPORT_AGENT` | **Conditional** | Can update own profile; cannot modify other agents or elevate role. |
| `/api/v1/users/{id}` | `PUT` | `ADMIN` | **YES** | Can update any profile, assign new roles, or modify account details. |
| `/api/v1/users/{id}/status` | `PATCH` | `EMPLOYEE` | **NO (403)** | `require_admin` dependency blocks account activation/deactivation. |
| `/api/v1/users/{id}/status` | `PATCH` | `SUPPORT_AGENT` | **NO (403)** | `require_admin` dependency prevents agents from disabling peer accounts. |
| `/api/v1/users/{id}/status` | `PATCH` | `ADMIN` | **YES** | Admin privilege to deactivate or re-enable employee accounts. |
| `/api/v1/tickets` (Create) | `POST` | `EMPLOYEE` | **YES** | Primary employee function to file support tickets. |
| `/api/v1/tickets` (Create) | `POST` | `SUPPORT_AGENT` | **YES** | Support agents can file internal support tickets. |
| `/api/v1/tickets` (Create) | `POST` | `ADMIN` | **YES** | Admins can file support tickets on behalf of IT infrastructure. |
| `/api/v1/tickets` (List) | `GET` | `EMPLOYEE` | **Filtered** | SQL automatically filters `created_by == current_user.id`. Other tickets inaccessible. |
| `/api/v1/tickets` (List) | `GET` | `SUPPORT_AGENT` | **YES** | Full visibility into unassigned and team ticket queues. |
| `/api/v1/tickets` (List) | `GET` | `ADMIN` | **YES** | Global visibility across all organization tickets. |
| `/api/v1/tickets/{id}` (Detail) | `GET` | `EMPLOYEE` | **Conditional** | Allowed only if `ticket.created_by == current_user.id`. Otherwise returns 403 Forbidden. |
| `/api/v1/tickets/{id}` (Detail) | `GET` | `SUPPORT_AGENT` | **YES** | Allowed for operational triage and resolution. |
| `/api/v1/tickets/{id}` (Detail) | `GET` | `ADMIN` | **YES** | Full read authority. |
| `/api/v1/tickets/{id}` (Update) | `PUT` | `EMPLOYEE` | **Conditional** | Allowed only for own tickets while still in `OPEN` state. Cannot modify priority (403). |
| `/api/v1/tickets/{id}` (Update) | `PUT` | `SUPPORT_AGENT` | **YES** | Can update title, description, category, and priority on open/active tickets. |
| `/api/v1/tickets/{id}` (Update) | `PUT` | `ADMIN` | **YES** | Can update all ticket fields. |
| `/api/v1/tickets/{id}` (Closed) | `PUT` | Any Role | **NO (422)** | Modifying a closed ticket is strictly prohibited (`TICKET_CLOSED`). Must reopen first. |
| `/api/v1/tickets/{id}` (Delete) | `DELETE` | `EMPLOYEE` | **NO (403)** | `require_admin` blocks employees from deleting tickets. |
| `/api/v1/tickets/{id}` (Delete) | `DELETE` | `SUPPORT_AGENT` | **NO (403)** | `require_admin` blocks agents from deleting tickets to preserve audit trails. |
| `/api/v1/tickets/{id}` (Delete) | `DELETE` | `ADMIN` | **YES** | Hard delete authorized only for administrators with audit logging. |
| `/api/v1/tickets/{id}/assign` | `POST` | `EMPLOYEE` | **NO (403)** | `require_support_or_admin` prevents employees from cherry-picking assignees. |
| `/api/v1/tickets/{id}/assign` | `POST` | `SUPPORT_AGENT` | **YES** | Can assign ticket to self or delegate to another active support agent. |
| `/api/v1/tickets/{id}/assign` | `POST` | `ADMIN` | **YES** | Can assign ticket to any agent or admin. |
| `/api/v1/tickets/{id}/status` | `POST` | `EMPLOYEE` | **Conditional** | Can only transition `RESOLVED -> CLOSED` for own tickets. All other transitions return 403. |
| `/api/v1/tickets/{id}/status` | `POST` | `SUPPORT_AGENT` | **YES** | Can advance statuses according to valid FSM transitions (`OPEN -> ASSIGNED -> IN_PROGRESS`). |
| `/api/v1/tickets/{id}/status` | `POST` | `ADMIN` | **YES** | Full status advance permissions according to valid FSM transitions. |
| `/api/v1/tickets/{id}/resolve` | `POST` | `EMPLOYEE` | **NO (403)** | Only IT technicians can mark issues as technically resolved. |
| `/api/v1/tickets/{id}/resolve` | `POST` | `SUPPORT_AGENT` | **YES** | Technicians provide mandatory resolution notes and mark `RESOLVED`. |
| `/api/v1/tickets/{id}/resolve` | `POST` | `ADMIN` | **YES** | Admin resolution override with mandatory resolution notes. |
| `/api/v1/tickets/{id}/reopen` | `POST` | `EMPLOYEE` | **Conditional** | Allowed on own tickets in `RESOLVED` or `CLOSED` status with mandatory reason. |
| `/api/v1/tickets/{id}/reopen` | `POST` | `SUPPORT_AGENT` | **YES** | Can reopen resolved tickets if customer confirms recurrence. |
| `/api/v1/tickets/{id}/reopen` | `POST` | `ADMIN` | **YES** | Can reopen any resolved or closed ticket. |
| `/api/v1/tickets/{id}/comments` | `POST` | All Authenticated | **Conditional** | Employees can comment on their own tickets; Agents/Admins on any ticket. |
| `/api/v1/categories` (Create/Update) | `POST/PUT` | `EMPLOYEE` | **NO (403)** | `require_admin` restricts category taxonomy management. |
| `/api/v1/categories` (Create/Update) | `POST/PUT` | `SUPPORT_AGENT` | **NO (403)** | `require_admin` restricts category taxonomy management. |
| `/api/v1/categories` (Create/Update) | `POST/PUT` | `ADMIN` | **YES** | Admins create and modify corporate IT issue categories. |
| `/api/v1/dashboard/summary` | `GET` | All Roles | **YES (Scoped)** | Employee gets personal ticket stats; Agent gets personal queue; Admin gets company KPI. |
| `/api/v1/dashboard/agent-performance` | `GET` | `EMPLOYEE` | **NO (403)** | `require_support_or_admin` prevents staff from inspecting technician performance metrics. |
| `/api/v1/dashboard/agent-performance` | `GET` | `SUPPORT_AGENT` | **YES** | Technicians inspect queue velocity and peer MTTR. |
| `/api/v1/dashboard/agent-performance` | `GET` | `ADMIN` | **YES** | Helpdesk operational oversight and resource planning. |
| `/api/v1/audit-logs` | `GET` | `EMPLOYEE` | **NO (403)** | `require_admin` dependency protects immutable audit logs. |
| `/api/v1/audit-logs` | `GET` | `SUPPORT_AGENT` | **NO (403)** | `require_admin` dependency protects immutable audit logs. |
| `/api/v1/audit-logs` | `GET` | `ADMIN` | **YES** | Admin compliance inspection for security and forensic audits. |

---

## 3. Interview Explanation: Why Backend RBAC Matters

> **Interviewer Question**: *"Why can't we simply hide the 'Delete' and 'Assign' buttons in the React UI for normal employees?"*
>
> **Fresher Answer**:
> *"Hiding UI elements in React is merely a user-experience convenience, not security. Any user can open Chrome DevTools, inspect network traffic, copy the JWT bearer token, and issue direct HTTP `curl` or Postman requests to `/api/v1/tickets/1/assign` or `/api/v1/users/2/status`.
>
> In TrackIT, security is authoritative at the API gateway layer using FastAPI's dependency injection (`require_roles([UserRole.ADMIN])`) and database queries parameterized by `current_user.id`. Even if an attacker bypasses the frontend entirely, the backend intercepts the request, verifies the JWT claims, and terminates unauthorized calls with an HTTP 403 Forbidden."*
