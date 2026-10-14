# Interview Guide: 02. Architecture & Design Decisions

## What is the Architecture?
TrackIT is structured as a **Clean Architecture Modular Monolith**. The backend strictly isolates presentation (FastAPI routes), domain business logic (Services), data access (Repositories), schemas (Pydantic DTOs), and database models (SQLAlchemy ORM). The frontend is a decoupled React single-page application communicating over REST APIs.

## Why was this architecture chosen?
* **Modular Monolith vs. Microservices:** Early-stage and internal enterprise platforms rarely need the operational complexity of distributed microservices (distributed tracing, network partitions, multi-repo overhead). A modular monolith maintains high development velocity, in-memory ACID transaction safety, and clean domain boundaries.
* **Repository Pattern:** Isolating query logic from business logic allows unit testing services without an active database connection and makes switching database drivers seamless.
* **Separation of Concerns:** Route handlers only validate input and return output; service classes implement domain logic; repositories manage SQL queries.

## How it works in TrackIT
When a user updates a ticket status:
1. `RequestLoggingMiddleware` logs the incoming request with an assigned `X-Request-ID`.
2. `routes/tickets.py` validates the input payload using `TicketStatusUpdate` schema and verifies bearer token via `require_role`.
3. `services/ticket_service.py` evaluates the `VALID_TRANSITIONS` state machine to ensure the change is legal.
4. `repositories/ticket_repository.py` writes the update and appends a record to `ticket_status_history`.
5. `repositories/audit_repository.py` creates an immutable audit record.
6. The enriched response is serialized through `TicketResponse` and returned.

## Alternative Approaches
* **Putting all logic in route functions (`main.py`):** Leads to "spaghetti code", duplicate queries, untested business logic, and inability to maintain the codebase as features scale.
* **Microservices with Event Bus (Kafka/RabbitMQ):** Introduces eventual consistency issues for ticket state transitions where immediate consistency is mandatory.

## Interview Questions & Answers

### Q: "Why did you use FastAPI over Django or Flask?"
**Answer:** "I chose FastAPI because of its asynchronous capabilities, automatic generation of OpenAPI/Swagger documentation, and native integration with Pydantic for strict type validation. Compared to Flask, it reduces boilerplate input validation; compared to Django, it provides lightweight flexibility without imposing an opinionated ORM or monolith template rendering engine."

### Q: "How does TrackIT demonstrate Object-Oriented Programming (OOP)?"
**Answer:** "TrackIT demonstrates OOP through:
1. **Encapsulation:** Services hide business algorithms and state transition maps inside private attributes.
2. **Abstraction:** Route controllers depend on abstract repository interfaces rather than raw database sessions.
3. **Inheritance & Generics:** `BaseRepository[T]` encapsulates common CRUD logic, which `TicketRepository` and `UserRepository` inherit.
4. **Polymorphism:** The dashboard summary method adjusts query behavior dynamically based on the caller's role."
