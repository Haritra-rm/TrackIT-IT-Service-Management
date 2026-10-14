# 08. REST API Design & Error Contracts

### 1. What it is
REST (Representational State Transfer) is an architectural style for networked applications that uses standard HTTP verbs (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), URI resources, and standardized HTTP status codes to manipulate resources statelessly.

### 2. Why TrackIT uses it
Adhering to standard REST principles ensures predictable interfaces between the React frontend, external monitoring integrations, and testing harnesses, preventing ambiguous status codes and inconsistent JSON payloads.

### 3. How it works
- **API Versioning**: All routes are namespaced under `/api/v1/`, allowing non-breaking API evolution in the future.
- **Resource-Oriented URIs**:
  - `GET /api/v1/tickets` (List with search, filter, sort, pagination)
  - `POST /api/v1/tickets` (Create new ticket - 201 Created)
  - `GET /api/v1/tickets/{id}` (Retrieve ticket detail - 200 OK)
  - `PUT /api/v1/tickets/{id}` (Update ticket content - 200 OK)
  - `DELETE /api/v1/tickets/{id}` (Admin hard delete - 204 No Content)
  - `POST /api/v1/tickets/{id}/assign` (State mutation)
  - `POST /api/v1/tickets/{id}/resolve` (State mutation)
  - `POST /api/v1/tickets/{id}/reopen` (State mutation)
- **Standardized Response Envelope**:
  ```json
  {
    "success": true,
    "data": { ... },
    "message": "Operation completed successfully"
  }
  ```
- **Consistent Error Contract**:
  ```json
  {
    "success": false,
    "error": {
      "code": "TICKET_NOT_FOUND",
      "message": "Ticket with ID 101 was not found",
      "details": null
    }
  }
  ```

### 4. Where it exists in the code
- Central Envelope Schemas: [`backend/app/schemas/common.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/schemas/common.py)
- Route Implementations: [`backend/app/routes/`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/routes/)
- Global Exception Handler: [`backend/app/middleware/error_handler.py`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/backend/app/middleware/error_handler.py)
- Full API Specification: [`API.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/API.md)

### 5. Alternative approach
- GraphQL API with a single `/graphql` endpoint.
- gRPC with protocol buffers.
- Ad-hoc RPC-style endpoints (`/api/doTicketUpdate`, `/api/fetchTicketDetails`).

### 6. Why this approach was selected
RPC-style endpoints lead to inconsistent methods and poor caching. GraphQL introduces significant complexity around query cost analysis, schema stitching, and HTTP caching for a straightforward CRUD and workflow application. REST over HTTP/JSON is universally understood, naturally cached by web proxies and CDNs, and seamlessly mapped to frontend React services.

### 7. Likely interviewer question
*"Why do you wrap all API responses in a standardized `ApiResponse` envelope instead of returning raw JSON objects?"*

### 8. Simple fresher-level answer
*"A standardized response envelope guarantees that the frontend client always receives a predictable JSON structure containing `success`, `data`, and `error`. In React, our Axios/fetch interceptor can inspect `response.data.success` universally. If false, it extracts the standardized `error.code` and `error.message` for user alerts. This avoids having different components write custom error-parsing logic for different endpoints."*
