# TrackIT — Deployment & Cloud Architecture Guide

## 1. Local Development Setup

### Prerequisites
* Python 3.10+
* Node.js 20+ & npm 10+
* Git

### Step-by-Step Setup
1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd "TrackIT — Smart IT Service & Issue Management Platform"
   ```

2. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```

3. **Backend Setup:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtualenv (Windows PowerShell)
   .\venv\Scripts\Activate.ps1
   # Or Linux/macOS:
   # source venv/bin/activate

   # Install dependencies
   pip install -r backend/requirements.txt

   # Seed database with demo data (8 users, 7 categories, 22 tickets)
   python backend/seed.py

   # Start backend API server
   python -m uvicorn app.main:app --app-dir backend --reload --port 8000
   ```
   Backend will be running at: `http://localhost:8000`  
   Interactive Swagger docs at: `http://localhost:8000/docs`

4. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend will be running at: `http://localhost:5173`

---

## 2. Docker & Docker Compose Deployment

TrackIT is fully containerized. A single command provisions PostgreSQL, runs seed data/migrations, and compiles the React SPA behind Nginx.

### Running with Docker Compose:
```bash
docker compose up --build -d
```

### Services Provisioned:
| Container | Service | Internal Port | Exposed Host Port | Health Check |
| :--- | :--- | :--- | :--- | :--- |
| `trackit-postgres` | PostgreSQL 16 Alpine | 5432 | 5432 | `pg_isready` |
| `trackit-backend` | FastAPI / Python 3.10 | 8000 | 8000 | `curl /health` |
| `trackit-frontend` | React SPA / Nginx | 80 | 3000 | Nginx HTTP 200 |

### Access URLs:
* Web Application: `http://localhost:3000`
* API Documentation: `http://localhost:8000/docs`
* Health Check: `http://localhost:8000/health`

### Stopping Containers:
```bash
docker compose down -v
```

---

## 3. Production Cloud Architecture on AWS

TrackIT is designed for scalable, zero-downtime deployment on **Amazon Web Services (AWS)** using managed services.

```
                            [ USER BROWSER ]
                                   │
                                   ▼
                            [ AWS Route 53 ]
                                   │
               ┌───────────────────┴───────────────────┐
               │ HTTPS (Port 443)                      │ HTTPS / API
               ▼                                       ▼
     [ CloudFront CDN ]                     [ Application Load Balancer ]
               │                                       │
               ▼                                       ▼
    [ S3 Static Website ]                   [ AWS ECS Fargate Cluster ]
    (Compiled React SPA)                    (FastAPI Docker Containers)
                                                       │
                                        ┌──────────────┴──────────────┐
                                        │                             │
                                        ▼                             ▼
                            [ AWS Secrets Manager ]       [ Amazon RDS PostgreSQL ]
                            (JWT Key & DB Passwords)      (Multi-AZ Deployment)
                                                                      │
                                                                      ▼
                                                          [ Amazon S3 Automated Backups ]
```

### AWS Component Mapping:

1. **Frontend Hosting (S3 + CloudFront):**
   * The React SPA is compiled (`npm run build`) and stored in a private **Amazon S3** bucket.
   * **AWS CloudFront** serves the assets globally via Edge Locations with SSL termination (ACM Certificate) and automatic Gzip/Brotli compression.

2. **Backend Application (AWS ECS Fargate):**
   * The backend Docker container is pushed to **Amazon Elastic Container Registry (ECR)**.
   * Runs as a serverless container on **AWS ECS Fargate** inside a private VPC subnet.
   * **Application Load Balancer (ALB)** routes traffic from `/api/*` to ECS task targets and checks the `/health` endpoint for auto-healing.
   * Auto Scaling policies scale tasks horizontally based on CPU utilization and request count.

3. **Database Tier (Amazon RDS PostgreSQL):**
   * Provisioned as an **Amazon RDS for PostgreSQL** instance in Multi-AZ configuration for automated failover.
   * Automated snapshots and point-in-time recovery enabled.
   * Placed in private database subnets accessible only by the ECS security group.

4. **Secrets & Configuration:**
   * `JWT_SECRET_KEY` and database credentials are stored in **AWS Secrets Manager** and injected into ECS task definitions at startup.

5. **Monitoring & Logging:**
   * Structured logs stream to **Amazon CloudWatch Logs**.
   * CloudWatch Alarms trigger notifications if API 5xx errors or SLA breaches spike.
