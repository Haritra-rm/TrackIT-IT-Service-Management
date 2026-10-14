# 02. Architecture & Clean Modular Design

### 1. What it is
TrackIT is structured as a **Clean Architecture Modular Monolith**. It separates concerns into clear layers: Presentation (React SPA), API Gateway / Routing (FastAPI), Application Business Services, Data Access Repositories, and Relational Database Persistence (PostgreSQL/SQLAlchemy).

### 2. Why TrackIT uses it
Mixing database queries directly into route controllers leads to tight coupling, untestable code, repeated business logic, and security vulnerabilities. Clean Architecture decouples the HTTP transport layer from domain business rules and database schemas.

### 3. How it works
- **Routes (`backend/app/routes/`)**: Handle HTTP serialization, OpenAPI docs, and role dependency injection. No raw SQL or business decisions live here.
- **Schemas (`backend/app/schemas/`)**: Pydantic v2 models validate and sanitize request payloads and serialize API responses.
- **Services (`backend/app/services/`)**: Enforce business rules (State Machine transitions, SLA calculations, Priority scoring, User authorization).
- **Repositories (`backend/app/repositories/`)**: Encapsulate SQLAlchemy ORM queries, joins (`joinedload`), and pagination.
- **Models (`backend/app/models/`)**: Define the database relational schema and foreign key constraints.

### 4. Where it exists in the code
- Controller Route: [`backend/app/routes/tickets.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/routes/tickets.py)
- Domain Service: [`backend/app/services/ticket_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/ticket_service.py)
- Generic & Domain Repository: [`backend/app/repositories/base_repository.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/repositories/base_repository.py), [`backend/app/repositories/ticket_repository.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/repositories/ticket_repository.py)
- Database Engine & Session: [`backend/app/database/connection.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/database/connection.py), [`backend/app/database/session.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/database/session.py)

### 5. Alternative approach
- **Alternative 1:** Django's Model-View-Template (MVT) pattern or FastAPI "fat controllers" putting all SQL inside routes.
- **Alternative 2:** Distributed Microservices (Auth service, Ticket service, Notification service, Analytics service).

### 6. Why this approach was selected
Fat controllers create spaghetti code that cannot be unit-tested without a live web server and database. Distributed microservices introduce high network latency, distributed transaction complexity (Saga pattern), and unnecessary DevOps overhead for an organization with under 100,000 employees. A modular monolith provides the maintainability and separation of microservices with the deployment simplicity of a single service.

### 7. Likely interviewer question
*"Why did you choose a Modular Monolith instead of Microservices for TrackIT?"*

### 8. Simple fresher-level answer
*"I chose a Modular Monolith because our domain boundaries—Users, Tickets, Comments, and SLA Analytics—share strong transactional consistency requirements. For example, creating a ticket must immediately initialize its status history and SLA deadline within an atomic database transaction. Microservices would introduce network serialization latency, two-phase commits, and operational complexity without added value at this scale. Our modular repository-service pattern allows us to cleanly split into microservices in the future if team size demands it."*
