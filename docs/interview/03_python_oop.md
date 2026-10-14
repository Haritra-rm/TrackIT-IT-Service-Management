# 03. Python & Object-Oriented Programming (OOP)

### 1. What it is
Object-Oriented Programming (OOP) in Python is an engineering paradigm that structures code into reusable, encapsulated classes with clear responsibilities, using principles like Encapsulation, Abstraction, Inheritance, and Polymorphism.

### 2. Why TrackIT uses it
Rather than writing loose procedural scripts, TrackIT uses OOP to encapsulate domain logic (SLA calculations, priority assessments, and database operations) into reusable classes, isolating data manipulation and enabling thorough dependency injection and unit testing.

### 3. How it works
- **Encapsulation**: Classes like `TicketService` and `AuthService` hide internal repository details and database session management, exposing only high-level operations like `create_ticket()` and `authenticate_user()`.
- **Abstraction**: `BaseRepository[ModelType]` provides a clean abstract interface (`get_by_id`, `create`, `update`, `delete`), shielding business services from underlying SQLAlchemy query construction.
- **Inheritance**: `TicketRepository` and `UserRepository` inherit from `BaseRepository`, reusing core CRUD mechanics while extending domain-specific queries (`get_by_email`, `search_tickets`). Custom exceptions (`NotFoundException`, `ForbiddenException`, `ValidationException`) inherit from a unified `AppException`.
- **Polymorphism**: Base exception handling middleware catches any subclass of `AppException` and formats it uniformly into standard JSON error responses without needing custom error handlers per route.

### 4. Where it exists in the code
- Generic Base Repository: [`backend/app/repositories/base_repository.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/repositories/base_repository.py)
- Domain Service Encapsulation: [`backend/app/services/ticket_service.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/services/ticket_service.py)
- Exception Hierarchy: [`backend/app/core/exceptions.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/core/exceptions.py)
- Domain Models: [`backend/app/models/ticket.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/models/ticket.py)

### 5. Alternative approach
- Pure procedural scripting with global variables and ad-hoc helper functions across multiple `.py` files.
- Functional programming using higher-order functions and dictionaries instead of typed model and repository classes.

### 6. Why this approach was selected
Procedural code quickly produces high technical debt, makes mock testing difficult, and causes circular import traps. OOP enables dependency injection: by passing the database session `db: Session` into the service class constructor (`TicketService(db)`), we can easily substitute a test database or mock session during unit testing.

### 7. Likely interviewer question
*"Where did you use Inheritance in TrackIT, and why was it genuinely useful rather than forced?"*

### 8. Simple fresher-level answer
*"I used inheritance in two places where it provided genuine value: first, in our `BaseRepository[ModelType]`, where generic CRUD methods (`get_by_id`, `delete`, `count`) are inherited by `UserRepository`, `TicketRepository`, and `CategoryRepository`, eliminating hundreds of lines of duplicate database code. Second, in `AppException`, where domain exceptions like `NotFoundException` (404) and `ForbiddenException` (403) inherit common status codes and error code fields, allowing our global FastAPI middleware to handle all domain errors polymorphically."*
