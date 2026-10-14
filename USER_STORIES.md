# TrackIT — Product Requirements & User Stories

## 1. Product Vision & Problem Statement

In modern corporate environments, technical issues—ranging from VPN lockouts and dock connectivity failures to security breaches—are frequently reported through informal, fragmented channels such as direct Slack messages, WhatsApp, or unstructured emails. This creates significant operational liabilities:
* Issues get lost without ownership or tracking.
* No service level agreements (SLAs) exist to guarantee timely resolution.
* IT management lacks visibility into recurring root causes, asset failures, and team performance metrics.

**TrackIT** resolves this by delivering a structured, enterprise-grade IT Service Management (ITSM) platform. TrackIT streamlines the end-to-end lifecycle:
$$\text{Employee Report} \longrightarrow \text{Automated SLA/Priority Triage} \longrightarrow \text{Agent Investigation} \longrightarrow \text{Resolution} \longrightarrow \text{Verified Closure}$$

---

## 2. User Personas

| Persona | Role in Platform | Core Needs |
| :--- | :--- | :--- |
| **Alice (Software Engineer)** | **Employee** | Quick issue submission, visibility on ticket progress, ability to reopen unresolved issues. |
| **Sarah (IT Support Specialist)** | **Support Agent** | Centralized queue, clear SLA deadlines, fast assignment, customer communication thread. |
| **Alexander (IT Director)** | **Administrator** | System oversight, SLA breach alerts, agent performance ratings, user and category controls. |

---

## 3. Epics & User Stories

### Epic 1: Authentication & Identity Management
* **US-1.1 (Registration):** *As an employee*, I want to register an account with my corporate email so that I can report and track workplace technology problems.
  * **Acceptance Criteria:** Email must be valid and unique; password minimum 6 characters; default role set to `EMPLOYEE`.
* **US-1.2 (Authentication):** *As a user*, I want to log in using my email and password to receive a signed JWT bearer token.
  * **Acceptance Criteria:** Password verified against salted bcrypt hash; inactive accounts rejected; returns token with expiration.
* **US-1.3 (Identity Inspection):** *As an authenticated user*, I want to view my profile details and role permissions via `/api/v1/auth/me`.

### Epic 2: Ticket Creation & Intelligent Triage
* **US-2.1 (Issue Submission):** *As an employee*, I want to create a ticket with title, description, category, and priority so that the IT team can solve my blocker.
  * **Acceptance Criteria:** Title $\ge 5$ characters; description $\ge 10$ characters; active category required; initial status set to `OPEN`.
* **US-2.2 (Smart Priority Advisor):** *As an employee or agent*, I want rule-based recommendations for ticket priority based on blast radius (affected users) and system impact so that SLAs are accurately assigned.
  * **Acceptance Criteria:** 20+ users or infrastructure failure recommends `CRITICAL` (4h SLA); 5+ users recommends `HIGH` (24h SLA); individual issues recommend `LOW` or `MEDIUM`. Does not silently overwrite user choice.

### Epic 3: Ticket Lifecycle & Workflow State Machine
* **US-3.1 (Assignment):** *As a support agent or admin*, I want to accept or assign tickets to qualified support agents.
  * **Acceptance Criteria:** Only `SUPPORT_AGENT` or `ADMIN` can assign; assigning an `OPEN` ticket automatically transitions it to `ASSIGNED`; status change is logged in history.
* **US-3.2 (Investigation & Progress):** *As a support agent*, I want to transition tickets from `ASSIGNED` to `IN_PROGRESS` while working on them.
  * **Acceptance Criteria:** Invalid transitions (e.g. `OPEN` directly to `RESOLVED` or modifying `CLOSED` tickets) are rejected by backend validation with code `INVALID_STATUS_TRANSITION`.
* **US-3.3 (Issue Resolution):** *As a support agent*, I want to mark tickets as `RESOLVED` by entering mandatory resolution notes.
  * **Acceptance Criteria:** `resolution_notes` field required ($\ge 5$ characters); timestamps `resolved_at` with current time.
* **US-3.4 (Reopen Ticket Loop):** *As an employee*, I want to reopen a resolved or closed ticket if the technical issue resurfaces.
  * **Acceptance Criteria:** Employees can only reopen their own tickets; status changes to `REOPENED`; SLA deadline recalculates; history notes reopen reason.
* **US-3.5 (Ticket Closure):** *As an administrator*, I want to close resolved tickets for final administrative sign-off.

### Epic 4: Collaboration & Auditability
* **US-4.1 (Comment Thread):** *As a ticket stakeholder*, I want to post messages and diagnostic logs to a ticket thread.
  * **Acceptance Criteria:** Employees can only comment on own tickets; agents/admins can comment on any ticket; messages stored with author role and timestamp.
* **US-4.2 (Audit Trail):** *As an administrator*, I want to inspect chronological status transitions and audit logs to verify accountability and compliance.

### Epic 5: SLA Management & Analytics
* **US-5.1 (Real-Time SLA Tracking):** *As an agent*, I want to see countdown timers and SLA badges (`ON_TRACK`, `AT_RISK`, `BREACHED`, `MET`) so that urgent deadlines are prioritized.
  * **Acceptance Criteria:** Tickets within 4 hours of breach marked `AT_RISK`; expired tickets marked `BREACHED`.
* **US-5.2 (Executive KPIs):** *As an administrator*, I want to track total tickets, breach rates, average resolution hours, and agent performance rankings.

---

## 4. Key Performance Indicators (KPIs) & Formulas

1. **Resolution Rate:**
   $$\text{Resolution Rate (\%)} = \left(\frac{\text{Resolved Tickets} + \text{Closed Tickets}}{\text{Total Tickets}}\right) \times 100$$
2. **SLA Breach Rate:**
   $$\text{SLA Breach Rate (\%)} = \left(\frac{\text{Breached Tickets}}{\text{Total Applicable Tickets}}\right) \times 100$$
3. **Average Turnaround Time (Mean Time to Resolution - MTTR):**
   $$\text{MTTR} = \frac{1}{N} \sum_{i=1}^{N} \left(\text{resolved\_at}_i - \text{created\_at}_i\right)$$
4. **Agent SLA Compliance:**
   $$\text{Compliance Rate (\%)} = \left(\frac{\text{Tickets Resolved On-Time}}{\text{Total Resolved Tickets}}\right) \times 100$$
