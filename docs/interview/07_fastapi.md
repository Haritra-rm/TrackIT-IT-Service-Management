# 07. FastAPI & Modern Python Frameworks

### 1. What it is
FastAPI is a modern, high-performance web framework for building RESTful APIs with Python 3.10+, built on Starlette (for async web routing) and Pydantic (for data validation and schema serialization).

### 2. Why TrackIT uses it
FastAPI provides automatic request validation, automatic interactive OpenAPI/Swagger documentation (`/docs`), strong typing, and dependency injection—which is essential for building robust Role-Based Access Control and database session management.

### 3. How it works
- **Dependency Injection (`Depends`)**: FastAPI resolves dependencies hierarchically. For example:
  ```python
  @router.post("/{id}/assign")
  def assign_ticket(
      id: int,
      payload: TicketAssign,
      current_user: User = Depends(require_support_or_admin),
      db: Session = Depends(get_db),
  ):
  ```
  Here, `get_db` opens a database session and safely closes it via a generator (`yield db / db.close()`). `require_support_or_admin` validates the JWT token and verifies that the calling user has `SUPPORT_AGENT` or `ADMIN` role before the function body executes.
- **Pydantic Validation**: Incoming JSON requests are automatically mapped to Pydantic models (e.g. `TicketCreate`), validating string lengths, email formats, and required fields before reaching business logic.
- **Auto-Generated Documentation**: FastAPI automatically produces interactive Swagger UI at `/docs` and ReDoc at `/redoc` directly from Python type hints.

### 4. Where it exists in the code
- Main Application Entry: [`backend/app/main.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/main.py)
- Dependency Injection: [`backend/app/core/dependencies.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/core/dependencies.py)
- Database Session Dependency: [`backend/app/database/session.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/database/session.py)

### 5. Alternative approach
- Django REST Framework (DRF)
- Flask with Marshmallow and Flask-RESTful

### 6. Why this approach was selected
Flask lacks native asynchronous request handling, requires multiple third-party libraries for validation, and does not provide automatic OpenAPI generation. Django is heavyweight, introducing unnecessary ORM coupling and boilerplate administrative overhead. FastAPI is lightweight, operates at speeds comparable to NodeJS and Go, and has first-class Python type hint integration.

### 7. Likely interviewer question
*"How does FastAPI's dependency injection system improve security and testability in TrackIT?"*

### 8. Simple fresher-level answer
*"FastAPI's dependency injection allows us to define reusable security checkpoints like `require_roles(['ADMIN'])`. Because dependencies execute before the route handler, unauthorized requests are intercepted and terminated with a 403 Forbidden before any database query runs. For testability, FastAPI provides `app.dependency_overrides`, allowing us to seamlessly swap out the production database session with an in-memory SQLite test database during automated pytest runs without changing application code."*
