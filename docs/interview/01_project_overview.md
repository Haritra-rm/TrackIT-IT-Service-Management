# 01. Project Overview & Product Thinking

### 1. What it is
TrackIT is a production-grade IT Service Management (ITSM) platform engineered with Python (FastAPI), React, and PostgreSQL. It standardizes how organizations log, triage, assign, investigate, resolve, and audit internal technical support issues.

### 2. Why TrackIT uses it
Without a dedicated ITSM platform, employees report technical failures over informal channels (Slack, email, WhatsApp), leading to lost tickets, SLA breaches, zero operational visibility, and untracked infrastructure downtime. TrackIT replaces this chaos with structured accountability and real-time SLA metrics.

### 3. How it works
1. **Employee Reports Issue**: Employee logs in and files a structured ticket specifying title, description, category, and impact.
2. **Blast-Radius Assessment**: Rule-based priority engine evaluates affected user count and severity, suggesting a priority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and setting a deterministic SLA deadline.
3. **Queue Assignment**: Support Agent claims or is assigned the ticket (`OPEN -> ASSIGNED`).
4. **Investigation**: Agent starts work (`ASSIGNED -> IN_PROGRESS`), collaborating via timestamped comments.
5. **Resolution & Verification**: Agent resolves the issue with mandatory resolution notes (`IN_PROGRESS -> RESOLVED`). Employee reviews the outcome and either confirms closure (`RESOLVED -> CLOSED`) or reopens the ticket (`RESOLVED -> REOPENED`).
6. **Executive Governance**: Admin monitors real-time dashboards (MTTR, breach rates, agent throughput) and immutable audit logs.

### 4. Where it exists in the code
- Main Application Flow: [`backend/app/main.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/main.py)
- Domain Lifecycle Service: [`backend/app/services/ticket_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/ticket_service.py)
- Frontend Workbenches: [`frontend/src/pages/EmployeeDashboard.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/pages/EmployeeDashboard.jsx), [`frontend/src/pages/AgentDashboard.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/pages/AgentDashboard.jsx), [`frontend/src/pages/AdminDashboard.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/pages/AdminDashboard.jsx)

### 5. Alternative approach
- **Option A:** Off-the-shelf commercial enterprise tool (ServiceNow or Jira Service Management).
- **Option B:** Generic low-code Kanban board (Trello or Notion).

### 6. Why this approach was selected
ServiceNow has exorbitant per-agent licensing fees and heavy onboarding friction for mid-sized organizations. Generic Kanban boards lack automated SLA deadline calculation, strict state machines, database-enforced RBAC, and tamper-resistant audit logs. Building TrackIT provides complete operational customization, zero per-seat license costs, and tight enterprise integration.

### 7. Likely interviewer question
*"What was your primary product objective when designing TrackIT, and how did you prevent priority inflation?"*

### 8. Simple fresher-level answer
*"My main product objective was turning unorganized workplace complaints into structured, measurable operational workflows. To prevent priority inflation—where every employee claims their issue is Critical—I built a rule-based blast radius recommender. The engine calculates priority based on objective inputs (affected users count, service outage blockers) rather than user emotion, ensuring critical SLA response times are reserved for genuine organization-wide blockers."*
