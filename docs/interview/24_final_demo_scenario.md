# 24. Live Interview Demo Script & Scenario Walkthrough

This document provides a rock-solid, step-by-step interview demonstration script. Follow these exact steps during a live coding interview to showcase the full end-to-end capabilities of TrackIT.

---

## The Demo Scenario Specification

- **Persona**: Alice Morgan (Employee)
- **Problem**: *"VPN connectivity drops every 10 minutes"*
- **Category**: `Network`
- **Blast Radius**: 25 affected users
- **Business Impact**: `Department blocked`
- **Expected Recommendation**: **`HIGH`** priority with **8-hour SLA deadline**
- **Lifecycle Sequence**:
  $$\text{OPEN} \longrightarrow \text{ASSIGNED} \longrightarrow \text{IN\_PROGRESS} \longrightarrow \text{RESOLVED} \longrightarrow \text{CLOSED}$$

---

## Step-by-Step Live Demo Execution

### Step 1: Log In as Employee
1. Open the web browser at [http://localhost:5173](http://localhost:5173).
2. On the login card, click the **Employee** button (auto-fills `emp.alice@trackit.internal` / `Employee@123`).
3. Click **Sign In to Workspace**.
4. You are directed to the **Employee Portal** showing your personal tickets.

---

### Step 2: Create Ticket with Smart Priority Recommendation
1. Click the **+ New Ticket** button in the sidebar or top header.
2. Fill out the ticket form:
   - **Title**: `VPN connectivity drops every 10 minutes`
   - **Category**: Select `Network`
   - **Description**: `WireGuard client disconnects every 10 minutes on macOS across our entire engineering squad.`
3. Click the **Smart Recommend** button next to Priority.
4. In the modal dialog:
   - Set **Affected Users**: `25`
   - Set **Business Impact**: Select `Department Blocked`
   - Leave Security and System Outage toggles unchecked.
5. The recommendation engine displays:
   - **Recommended Priority**: **`HIGH`**
   - **SLA Resolution Target**: **8 Hours**
   - **Algorithmic Reason**:
     ```
     - Network category
     - 25 affected users
     - Department blocked
     ```
6. Click **Apply Recommendation** to populate the form.
7. Click **Create Support Ticket**.
8. The ticket appears immediately in the table with an **`OPEN`** badge, **`HIGH`** priority badge, and a green **`ON_TRACK`** SLA timer badge.

---

### Step 3: Triage & Assignment as Support Agent
1. In the top navbar, click **Sign Out**.
2. Click the **Agent** demo login button (`agent.sarah@trackit.internal` / `Agent@123`) and sign in.
3. You are directed to the **Support Agent Workspace**.
4. Navigate to **All Tickets** and click the newly created ticket `#1` (`VPN connectivity drops every 10 minutes`).
5. Click the **Assign to Me** button:
   - The ticket updates instantly: Assignee becomes `Sarah Jenkins`.
   - The status automatically advances from **`OPEN`** to **`ASSIGNED`**.

---

### Step 4: Investigation & Collaboration
1. Under Ticket Actions, click **Start Investigation**:
   - Status advances from **`ASSIGNED`** to **`IN_PROGRESS`**.
2. Scroll to the **Internal Comments** section:
   - Type: `Investigating MTU packet sizing and gateway routing on internal WireGuard node.`
   - Click **Post Comment**.
   - The timestamped comment appears in the discussion stream.

---

### Step 5: Resolution with Technical Notes
1. Click the **Resolve Ticket** button.
2. Enter the mandatory resolution summary:
   - *Resolution Notes*: `Adjusted MTU packet size from 1500 to 1420 on WireGuard corporate gateway and restarted service daemon.`
3. Click **Confirm Resolution**:
   - The status moves to **`RESOLVED`**.
   - The SLA badge records the milestone as **`MET`** (resolved well before the 8-hour deadline).

---

### Step 6: Employee Verification & Closure
1. Sign out of the agent account.
2. Sign back in as the Employee (`emp.alice@trackit.internal`).
3. Open the resolved ticket.
4. Notice the prompt: *"The support team has marked this ticket as resolved. If the solution resolved your problem, confirm and close this ticket."*
5. Click **Close Ticket**:
   - The status transitions to **`CLOSED`**.
   - The ticket is finalized with a complete status history audit trail.

---

### Step 7: Executive KPI Verification (Admin Dashboard)
1. Sign out of the employee account.
2. Click the **Admin** demo button (`admin@trackit.internal` / `Admin@123`) and sign in.
3. Observe the **Executive Analytics Dashboard**:
   - **Total Tickets**: `1`
   - **Closed Tickets**: `1`
   - **Resolution Rate**: `100.0%`
   - **SLA Breach Rate**: `0.0%`
   - **Mean Time to Resolution (MTTR)**: Real-time calculation in hours.
   - **Tickets by Category**: Chart displays 100% `Network`.
   - **Tickets by Priority**: Chart displays 100% `HIGH`.
   - **Agent Performance**: Shows `Sarah Jenkins` with 1 resolved ticket and 100% SLA compliance.
4. Click **Audit Logs** in the sidebar:
   - Inspect the immutable chronological audit log verifying every action: `TICKET_CREATED`, `TICKET_ASSIGNED`, `TICKET_STATUS_CHANGED`, `TICKET_RESOLVED`, and `TICKET_STATUS_CHANGED` to `CLOSED`.
