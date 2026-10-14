# 12. Smart Priority Recommendation & Blast-Radius Engine

### 1. What it is
The Smart Priority Recommendation Engine is a deterministic, rule-based algorithmic model that calculates an appropriate IT ticket priority (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) based on business blast radius, infrastructure downtime, and affected employee scale.

### 2. Why TrackIT uses it
Employees reporting IT issues almost always claim their issue is "CRITICAL" because they are personally blocked. If unchecked, this causes "priority inflation," overwhelming the IT helpdesk queue and pushing genuine enterprise outages down the priority list. The engine provides transparent, objective recommendations.

### 3. How it works
- **Scoring Formula**:
  $$\text{Total Score} = \text{Impact Score} + \text{Blast Radius Bonus} + \text{Category Bonus} + \text{Blocker Score}$$
- **Scoring Weights**:
  - **Impact Weight**:
    - `LOW`: 5 pts
    - `MEDIUM`: 15 pts
    - `HIGH` / `DEPARTMENT_BLOCKED`: 25 pts
    - `CRITICAL` / `ORGANIZATION_BLOCKED`: 45 pts
  - **Blast Radius (Affected Users)**:
    - 1 user: 0 pts
    - 2–4 users: 5 pts
    - 5–19 users: 10 pts
    - 20–49 users: 15 pts
    - 50–99 users: 25 pts
    - $\ge 100$ users: 35 pts
  - **Category Weight**:
    - `Security`: +20 pts
    - `Network` / `Access`: +10 pts
    - Other: 0 pts
  - **Critical Blocker Override**:
    - `is_security_incident`: +50 pts (immediate CRITICAL)
    - `is_system_down`: +50 pts (immediate CRITICAL)
- **Thresholds**:
  - Score $\ge 75$ or Active Outage/Security: $\implies$ **`CRITICAL`**
  - Score $\ge 35$ or $\ge 20$ affected users on Network/Access: $\implies$ **`HIGH`**
  - Score $\ge 20$ or $> 1$ users or Medium impact: $\implies$ **`MEDIUM`**
  - Score $< 20$: $\implies$ **`LOW`**
- **Explainability**:
  The engine generates a structured bulleted rationale explaining exactly why a priority was chosen:
  ```
  - Network category
  - 25 affected users
  - Department blocked
  ```

### 4. Where it exists in the code
- Recommendation Engine: [`backend/app/services/priority_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/priority_service.py)
- API Endpoint: `POST /api/v1/tickets/recommend-priority` in [`backend/app/routes/tickets.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/routes/tickets.py)
- Unit Tests: [`backend/tests/unit/test_priority.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/tests/unit/test_priority.py)
- Frontend Modal: [`frontend/src/components/PriorityRecommenderModal.jsx`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/frontend/src/components/PriorityRecommenderModal.jsx)

### 5. Alternative approach
- Machine Learning / NLP Classifier (e.g. BERT or Naive Bayes) trained on historical ticket descriptions.

### 6. Why this approach was selected
Machine Learning models act as "black boxes" that cannot transparently explain *why* a ticket was classified as High or Low. They require large labeled historical training datasets, are prone to data drift, and introduce heavy ML runtime dependencies (PyTorch/Transformers). A deterministic rule-based scoring engine is 100% explainable, deterministic, zero-dependency, and instantly auditable by human agents.

### 7. Likely interviewer question
*"Why didn't you use a Machine Learning model like BERT or an LLM to predict ticket priority?"*

### 8. Simple fresher-level answer
*"I intentionally chose an explainable rule-based scoring algorithm over ML because in enterprise IT operations, decisions must be transparent and predictable. If an employee's issue is classified as Low instead of Critical, the system must explain why—such as '1 affected user, no system outage flagged'. A deterministic scoring algorithm executes in under 1 millisecond, requires zero expensive GPU infrastructure, and eliminates hallucination risks."*
