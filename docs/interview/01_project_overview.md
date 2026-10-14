# Interview Guide: 01. Project Overview & Product Thinking

## What is TrackIT?
TrackIT is a production-style, full-stack IT Service Management (ITSM) platform engineered with Python (FastAPI), React, and PostgreSQL. It streamlines how modern organizations manage, prioritize, assign, and resolve internal IT technical blockers (hardware failures, VPN outages, permission requests, security alerts).

## Why was TrackIT built?
In fast-growing organizations, IT issues are often reported over chat (Slack/Teams) or ad-hoc emails. This leads to lost tickets, lack of accountability, missed deadlines, and zero executive visibility into infrastructure reliability. TrackIT addresses this by establishing structured ticket lifecycles, automated SLA tracking, intelligent blast-radius triage, and role-based operational workbenches.

## How it works in TrackIT
1. An employee reports an issue.
2. The Rule-Based Priority Engine assesses impact and recommends a priority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), calculating a dynamic SLA target deadline.
3. A support agent accepts or is assigned the ticket.
4. The ticket progresses through a strict finite state machine: `OPEN` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED` $\rightarrow$ `CLOSED`.
5. If an issue is not satisfactorily resolved, the employee can invoke the `REOPENED` loop.
6. The entire workflow is backed by real-time SLA countdowns and immutable status history logs.

## Alternative Approaches & Why TrackIT Won
* **Alternative 1: Commercial SaaS (Jira Service Management / ServiceNow).**
  * *Why custom solution was chosen:* High licensing cost per agent, vendor lock-in, and excessive complexity for mid-market internal operations where streamlined, purpose-built workflows are preferred.
* **Alternative 2: Off-the-shelf basic ticketing templates.**
  * *Why custom solution was chosen:* Lacks strict server-side state machines, dynamic SLA calculations, and customized RBAC logic required for enterprise compliance.

## Potential Interview Questions & Strong Answers

### Q: "Can you describe TrackIT in two sentences?"
**Answer:** "TrackIT is an enterprise IT Service Management platform built with FastAPI, React, and PostgreSQL that automates ticket lifecycles, enforces strict role-based access control, and tracks real-time SLA compliance. It transforms informal workplace technical complaints into accountable, measurable operational resolutions."

### Q: "What was your approach to Product Thinking during development?"
**Answer:** "I prioritized business outcomes and persona workflows over generic CRUD features. I defined three distinct personas—Employee, Support Agent, and Administrator—and designed specific capabilities for each. For instance, rather than letting users choose arbitrary priorities, I built a smart priority advisor that analyzes blast radius to prevent priority inflation and protect SLA integrity."
