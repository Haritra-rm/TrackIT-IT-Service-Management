# Interview Guide: 08. Docker & Containerization

## What is the Containerization Strategy?
TrackIT provides multi-container orchestration via **Docker** and **Docker Compose**:
1. `postgres:16-alpine`: Lightweight PostgreSQL database container with volume persistence.
2. `backend`: Custom container using `python:3.10-slim`, non-root security principles, and health check probe.
3. `frontend`: Multi-stage build (`node:20-alpine` build stage $\rightarrow$ `nginx:alpine` runtime stage) with reverse proxy routing.

## Why was Docker chosen?
* **"Works on My Machine" Elimination:** Containerization encapsulates system libraries (`libpq-dev`), runtime versions (Node 20, Python 3.10), and environment configurations, guaranteeing identical execution on macOS, Linux, and Windows.
* **Multi-Stage Builds:** Building the React SPA in Node produces static files; copying only `dist/` into an Nginx Alpine container reduces image size from $> 800\text{ MB}$ down to $\approx 25\text{ MB}$ and eliminates Node.js from the production attack surface.

## How it works in TrackIT
When executing `docker compose up --build`:
1. `postgres` starts and initializes healthcheck `pg_isready`.
2. `backend` waits for PostgreSQL's `service_healthy` signal via `depends_on`.
3. `backend` runs `python seed.py` to auto-seed initial categories and demo accounts, then boots Uvicorn on port 8000.
4. `frontend` boots Nginx on host port 3000, proxies `/api/*` to the internal backend container, and serves the React SPA.

## Interview Questions & Answers

### Q: "What is a multi-stage Docker build, and why did you use it for the frontend?"
**Answer:** "A multi-stage build uses multiple `FROM` instructions in a single Dockerfile. In TrackIT's frontend, stage 1 uses a full `node:20-alpine` image with all devDependencies and Vite tools to compile the React code into static HTML/CSS/JS. Stage 2 uses a tiny `nginx:alpine` image and only copies the compiled `dist/` folder. This dramatically decreases the final Docker image footprint from hundreds of megabytes to ~25MB, speeds up container deployment, and improves security by removing Node and npm from the runtime container."

### Q: "How does Docker Compose handle startup dependencies and health checks?"
**Answer:** "Simply using `depends_on: [postgres]` only waits for the postgres container to start, not for the database engine to finish initializing. In TrackIT, I configured a health check using `pg_isready` on PostgreSQL, and set `condition: service_healthy` in the backend service definition. This ensures the backend only attempts database connections after PostgreSQL is fully ready to accept sockets."
