# Interview Guide: 04. REST API Design & Contracts

## What is the API Design?
TrackIT adheres to **RESTful architectural constraints** under versioned URIs (`/api/v1/*`). It uses standard HTTP verbs (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), semantic status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`, `500`), and a consistent JSON response envelope.

## Why was this design chosen?
* **Versioning (`/api/v1`):** Protects frontend clients and mobile/third-party consumers from breaking contract changes when endpoints evolve in the future.
* **Standard Error Contract:** Frontend developers and API consumers can reliably parse error codes without guessing structure:
  ```json
  { "success": false, "error": { "code": "...", "message": "..." } }
  ```
* **Semantic Verbs:**
  * `PUT /api/v1/tickets/{id}`: Replaces/updates ticket content fields.
  * `PATCH /api/v1/users/{id}/status`: Modifies a specific resource attribute (account active flag).
  * `POST /api/v1/tickets/{id}/assign`: Sub-resource lifecycle action.

## How it works in TrackIT
1. Request hits FastAPI routing table.
2. Dependencies resolve authentication, RBAC authorization, and database session injection.
3. Query parameters (`page`, `page_size`, `status`, `search`) pass into repository pagination algorithms.
4. Outgoing objects are automatically converted into typed Pydantic models with OpenAPI schemas generated on the fly.

## Interview Questions & Answers

### Q: "What is the difference between PUT and PATCH in your API?"
**Answer:** "In TrackIT, `PUT` is used when updating a collection of resource fields (e.g., updating a ticket's title, description, and category), whereas `PATCH` is used for partial modifications to a specific attribute (e.g. `PATCH /api/v1/users/{id}/status` to toggle an account between active and deactivated)."

### Q: "How does pagination prevent Out-of-Memory (OOM) errors?"
**Answer:** "If an API fetches all records via `.all()`, as the ticket count grows to hundreds of thousands of rows, loading them into server memory will exhaust RAM and crash the Python process. TrackIT implements parameterized SQL `OFFSET` and `LIMIT` in `TicketRepository.search_and_filter`. Only the requested page slice (e.g. 20 rows) is loaded into memory, ensuring constant $O(1)$ memory consumption regardless of total database volume."
