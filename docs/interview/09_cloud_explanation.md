# Interview Guide: 09. Cloud Architecture & Deployment Readiness (AWS)

## What is the Cloud Strategy?
TrackIT is architected for **zero-downtime, horizontally scalable production deployment on Amazon Web Services (AWS)** using standard cloud-native building blocks:
* **Frontend:** Amazon S3 + Amazon CloudFront CDN.
* **Backend:** AWS ECS Fargate (Serverless Containers) behind an Application Load Balancer (ALB).
* **Database:** Amazon RDS PostgreSQL (Multi-AZ).
* **Secrets:** AWS Secrets Manager.
* **Monitoring:** Amazon CloudWatch Logs & Alarms.

## Why was this architecture chosen?
* **Separation of Compute & Storage:** Static React assets are served from edge caching (CloudFront), removing static file serving load from backend servers and achieving sub-50ms latency globally.
* **Serverless Containerization (ECS Fargate):** Eliminates EC2 server patching, OS maintenance, and capacity planning. Fargate tasks scale up automatically under load and scale down during off-peak hours.
* **Multi-AZ RDS Reliability:** Automated master-standby replication ensures zero data loss and automated failover in the event of an availability zone outage.

## How it works in TrackIT
1. User enters `https://trackit.company.org` into their browser.
2. AWS Route 53 routes request to CloudFront.
3. Static files are served from S3 cache; API requests matching `/api/*` are routed to the Application Load Balancer.
4. ALB distributes traffic across ECS Fargate tasks running the TrackIT backend container in private subnets.
5. Backend containers query the private RDS PostgreSQL cluster and authenticate secrets using IAM roles.

## Interview Questions & Answers

### Q: "How would you handle database migrations in a production zero-downtime deployment?"
**Answer:** "In a CI/CD pipeline, database migrations (using Alembic) should run as an isolated pre-deployment job (e.g., an ephemeral ECS task) before new backend application tasks are spun up. Furthermore, schema migrations must follow the expand-contract pattern: adding backward-compatible columns first so older running tasks continue working, deploying the new application version, and only dropping obsolete columns after verification."

### Q: "How do you secure secrets in the cloud without exposing them in source code?"
**Answer:** "Secrets such as `DATABASE_URL` and `JWT_SECRET_KEY` are stored in AWS Secrets Manager or Parameter Store. The ECS Task Execution IAM Role is granted least-privilege permission to read those specific secrets. When the container starts, AWS ECS injects the secrets directly into the container's environment variables without writing them to disk or hardcoding them in Git."
