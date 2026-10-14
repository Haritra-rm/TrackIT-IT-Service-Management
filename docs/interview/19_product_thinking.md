# 19. Product Thinking & KPI Metric Strategy

### 1. What it is
Product Thinking is the discipline of analyzing software engineering through the lens of user problems, operational outcomes, business value, and measurable performance indicators (KPIs) rather than just technical implementation.

### 2. Why TrackIT uses it
Building a generic CRUD application demonstrates coding syntax, but an Associate Product Engineer must demonstrate empathy for user personas (Employees, IT Agents, Operations Admins) and understand how technical features move organizational business metrics.

### 3. How it works
- **Persona-Centric User Journeys**:
  - *Employee Persona*: Values speed of reporting, transparency on ticket progress, and confidence that an issue is resolved before closure. Features: Quick-fill category templates, smart blast-radius advisor, self-service Reopen capability.
  - *Support Agent Persona*: Values clean triage queues, clear prioritization, and contextual history. Features: "Assign to Me" 1-click action, internal resolution notes, and SLA countdown visual warnings.
  - *Admin Persona*: Values operational health, capacity planning, and regulatory compliance. Features: Real-time MTTR charts, agent throughput metrics, and tamper-resistant audit logs.
- **Core Operational KPIs**:
  - **SLA Breach Rate (%)**:
    $$\text{Breach Rate} = \frac{\text{Total Breached Tickets}}{\text{Total Active Tickets}} \times 100$$
    *Target: $< 5\%$. Evaluates helpdesk capacity.*
  - **Mean Time to Resolution (MTTR)**:
    $$\text{MTTR} = \frac{\sum (\text{resolved\_at} - \text{created\_at})}{\text{Total Resolved Tickets}}$$
    *Target: $< 8\text{ hours}$. Evaluates resolution velocity.*
  - **First Response Time (FRT)**: Time between ticket creation and first agent assignment or comment.
  - **Reopen Rate**: High reopen rate flags premature or low-quality resolutions by technicians.

### 4. Where it exists in the code
- KPI Metric Calculations: [`backend/app/services/dashboard_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/dashboard_service.py)
- Executive Dashboard: [`frontend/src/pages/AdminDashboard.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/pages/AdminDashboard.jsx)
- User Stories & Business Scenarios: [`USER_STORIES.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/USER_STORIES.md)

### 5. Alternative approach
- Building generic CRUD screens with equal access and no role-tailored dashboards.
- Hardcoding static dashboard KPI numbers or displaying non-actionable vanity metrics (e.g. "Total registered users").

### 6. Why this approach was selected
IT directors do not care about vanity metrics; they care about preventing infrastructure downtime and ensuring technician SLA compliance. Tailoring specific workbenches to each persona eliminates cognitive friction and directly improves Mean Time to Resolution.

### 7. Likely interviewer question
*"If an executive asks you which metric best indicates the health of the IT helpdesk in TrackIT, which would you pick and why?"*

### 8. Simple fresher-level answer
*"I would pick the combined pair of **SLA Breach Rate** and **Reopen Rate**. While SLA Breach Rate measures velocity—ensuring technicians resolve blockers within agreed deadlines—Reopen Rate measures resolution quality. If an agent rapidly closes tickets just to satisfy SLA deadlines without actually fixing the root cause, the Reopen Rate spikes. Tracking both metrics simultaneously gives a balanced view of speed and technical quality."*
