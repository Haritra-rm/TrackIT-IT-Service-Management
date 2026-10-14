# 17. Cloud Architecture & AWS Deployment Readiness

### 1. What it is
Cloud computing provides on-demand availability of computing resources (compute, database storage, networking) over the internet with pay-as-you-go pricing, enabling high availability, auto-scaling, and disaster recovery.

### 2. Why TrackIT uses it
Enterprise ITSM platforms must remain available 24/7/365. If the corporate data center loses power, IT staff must still be able to access TrackIT to coordinate network recovery. Deploying on AWS provides multi-Availability Zone (AZ) resilience.

### 3. How it works
- **Target AWS Production Topology**:
  - **Networking**: VPC with public subnets (Internet Gateway) and private subnets (NAT Gateway).
  - **Edge / CDN**: AWS Route 53 (DNS) $\rightarrow$ CloudFront (CDN caching static React assets) $\rightarrow$ AWS Certificate Manager (HTTPS/SSL).
  - **Compute Layer**: AWS ECS (Elastic Container Service) with AWS Fargate (serverless container execution) running the FastAPI backend tasks behind an Application Load Balancer (ALB).
  - **Relational Storage**: AWS RDS PostgreSQL Multi-AZ with automatic failover, daily automated snapshots, and read replicas for dashboard analytics queries.
  - **Secrets Management**: AWS Secrets Manager storing database credentials and JWT secret keys, dynamically injected into ECS containers at launch time.
  - **Monitoring**: AWS CloudWatch logs collecting structured JSON application logs and firing alarms on 5xx error spikes.

### 4. Where it exists in the code
- Environment Configurations: [`.env.example`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/.env.example)
- Production Deployment Architecture: [`DEPLOYMENT.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/DEPLOYMENT.md)
- Cloud Explanation Guide: [`docs/interview/09_cloud_explanation.md`](file:///c:/Users/harit/OneDrive/Desktop/TrackIT%20%E2%80%94%20Smart%20IT%20Service%20&%20Issue%20Management%20Platform/docs/interview/09_cloud_explanation.md)

### 5. Alternative approach
- Running on a single EC2 virtual machine with Postgres, FastAPI, and Nginx installed on one server.
- Serverless functions (AWS Lambda + API Gateway) for all API endpoints.

### 6. Why this approach was selected
A single EC2 instance is a Single Point of Failure (SPOF) that crashes if the host hardware fails. While AWS Lambda works well for sporadic events, relational database connection pooling with Lambda can exhaust Postgres connection limits without costly RDS Proxy. ECS Fargate provides steady containerized execution, instant horizontal auto-scaling, and persistent connection pool reuse via SQLAlchemy.

### 7. Likely interviewer question
*"How would you architect TrackIT on AWS to achieve high availability with zero single points of failure?"*

### 8. Simple fresher-level answer
*"I would deploy across at least two Availability Zones. For the compute tier, I would run our FastAPI container on AWS ECS Fargate behind an Application Load Balancer that automatically health-checks and routes traffic. For the database tier, I would use AWS RDS PostgreSQL configured with Multi-AZ replication, so if the primary database fails, AWS automatically fails over to the standby replica in another data center within 60 seconds without data loss. Static frontend assets would be hosted on S3 and distributed globally through CloudFront CDN."*
