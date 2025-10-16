# AWS Deployment Guide for Social Media API

This guide walks through preparing, deploying, and operating the `social_media_api` Django project on Amazon Web Services using Elastic Beanstalk, RDS, and S3. Follow each section carefully to ensure a secure and reliable production environment.

> **Live URL**: `https://<your-env-name>.elasticbeanstalk.com` (replace after launching the environment).

---

## 1. Prerequisites

- AWS account with AdministratorAccess (for initial setup). Drop privileges to least-permission roles afterwards.
- AWS CLI v2 installed and configured with credentials: `aws configure`.
- Elastic Beanstalk CLI (`pip install awsebcli`).
- Docker (optional but useful for local parity tests).
- GitHub repository access for CI/CD (optional but recommended).

---

## 2. Environment Variables

Set the following environment variables in the Elastic Beanstalk console (Configuration → Software) or via the EB CLI (`eb setenv`). Use secure storage (AWS Secrets Manager or SSM Parameter Store) for sensitive values and reference them in EB.

| Variable | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Production secret key. Generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG` | Set to `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames (e.g., `your-env.elasticbeanstalk.com,your.custom.domain`) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins (e.g., `https://your.custom.domain`) |
| `DATABASE_URL` | RDS connection string (`postgres://user:password@hostname:5432/dbname`) |
| `DATABASE_CONN_MAX_AGE` | (Optional) Keep-alive seconds, e.g., `120` |
| `DATABASE_SSL_REQUIRE` | `True` to enforce TLS to RDS |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket for static/media content |
| `AWS_S3_REGION_NAME` | Bucket region, e.g., `us-east-1` |
| `AWS_S3_CUSTOM_DOMAIN` | (Optional) CloudFront domain serving the bucket |
| `AWS_S3_STATIC_LOCATION` | Prefix for collected static files, default `static` |
| `AWS_S3_MEDIA_LOCATION` | Prefix for uploaded media, default `media` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | IAM user or role credentials with S3 access (if not using instance profile) |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` to enforce HTTPS (default) |
| `DJANGO_LOG_LEVEL` | Logging level, e.g., `INFO` |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, etc. | Configure if outbound email is required |

> Configure IAM instance profiles or Secrets Manager wherever possible so you do not inject long-term credentials directly.

---

## 3. AWS Infrastructure Overview

1. **Elastic Beanstalk (EB)** – Python 3.11 platform running Gunicorn behind nginx.
2. **Amazon RDS (PostgreSQL)** – Production database in the same VPC as EB.
3. **Amazon S3** – Stores static assets (`collectstatic`) and uploaded media. Optionally front with **Amazon CloudFront** CDN.
4. **Amazon Certificate Manager (ACM)** – Issues TLS certificates for HTTPS.
5. **AWS CloudWatch** – Aggregates logs and metrics. Configure alarms on `5xx` responses, latency, CPU, and RDS health.

Create the VPC, security groups, and subnets (public for ALB, private for EB/RDS) if they do not already exist. Ensure the EB environment, RDS instance, and S3 bucket share the same region and VPC for low latency and security.

---

## 4. Project Preparation

1. **Install dependencies locally**
   ```bash
   pip install -r requirements.txt
   ```
2. **Collect static assets** (optional dry run)
   ```bash
   DJANGO_DEBUG=False DJANGO_SECRET_KEY=dummy python manage.py collectstatic --noinput
   ```
3. **Commit deployment files**: `Procfile`, `runtime.txt`, `.ebextensions/01_django.config`, and this guide.
4. **Push to GitHub** if not already present.

---

## 5. Provision AWS Resources

### 5.1 Create the S3 Bucket

- Name: `social-media-api-prod-<unique>` (must be globally unique).
- Enable versioning and (optionally) default encryption.
- Update bucket policy to allow ELB/CloudFront access. Example policy granting public read of `static` objects:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::social-media-api-prod-<unique>/static/*"
    }
  ]
}
```

Keep media objects private by default. Serve them via signed URLs if needed.

### 5.2 Launch RDS PostgreSQL

- Engine: PostgreSQL 15 or newer.
- Instance class: `db.t3.micro` (adjust for load).
- Storage: Start at 20 GB, GP3.
- Enable automatic backups, Multi-AZ (production), and Performance Insights.
- Set VPC security group to allow inbound traffic from the EB security group on port 5432.

Gather the connection endpoint, database name, username, and password to compose `DATABASE_URL`.

### 5.3 Create Elastic Beanstalk Environment

```bash
eb init --platform "Python 3.11" --region us-east-1 social-media-api
```

- Choose **Load Balanced, Scalable** environment.
- Configure capacity (minimum 1 instance; auto scaling as needed).
- Attach the RDS security group to allow outbound DB connections.
- Associate the S3 bucket as an environment property (`AWS_STORAGE_BUCKET_NAME`).
- Add the IAM instance profile with S3/RDS access.

Deploy the application:

```bash
eb create social-media-api-prod --single
```

> The bundled `.ebextensions/01_django.config` runs database migrations and `collectstatic` during each deployment.

### 5.4 Configure HTTPS

1. Request a certificate via AWS Certificate Manager for your domain.
2. Attach the certificate to the Elastic Beanstalk load balancer listener (Configuration → Load Balancer).
3. Ensure port 80 redirects to 443 (nginx handles this automatically; Django also enforces HTTPS via `SECURE_SSL_REDIRECT`).

### 5.5 Optional: CloudFront Distribution

- Create a distribution with the S3 bucket as the origin.
- Set alternate domain names (CNAMEs) and attach an ACM certificate.
- Point `AWS_S3_CUSTOM_DOMAIN` to the CloudFront domain to leverage CDN caching.

---

## 6. Deployment Workflow

1. **Commit and push changes** to the `main` branch.
2. **Deploy with EB CLI**:
   ```bash
   eb deploy social-media-api-prod
   ```
3. **Run database migrations** (automated via `.ebextensions`). Trigger manually if required:
   ```bash
   eb ssh --command "python manage.py migrate --noinput"
   ```
4. **Seed data** (optional):
   ```bash
   eb ssh --command "python manage.py createsuperuser"
   ```

For CI/CD, integrate GitHub Actions with the `elasticbeanstalk-deploy` action. Ensure the workflow runs tests, builds the artifact, and calls `eb deploy` using IAM credentials scoped to Elastic Beanstalk.

---

## 7. Monitoring & Maintenance

| Task | Tooling | Frequency |
| --- | --- | --- |
| Application logs | Elastic Beanstalk console or `eb logs` (pipes to CloudWatch) | Ad hoc / on alert |
| Metrics & Alarms | CloudWatch dashboards, `5xx`, latency, CPU, RDS connections | Continuous |
| Security patches | Dependabot / `pip list --outdated` | Weekly |
| Database backups | Automated snapshots (configure retention) | Daily |
| Static asset invalidation | CloudFront cache invalidation after major releases | As needed |
| Health checks | EB environment health, ALB target status | Continuous |

Set up CloudWatch alarms to notify (SNS/Slack) when:
- `HTTPCode_Target_5XX_Count` > 5 in 5 minutes.
- `Latency` p95 > 1s.
- `CPUUtilization` > 80% for 15 minutes.
- `DatabaseConnections` near the max configured.

Enable AWS X-Ray for distributed tracing if you need deeper diagnostics.

---

## 8. Disaster Recovery & Scaling

- **Scaling**: Configure Auto Scaling in EB to add instances when CPU or network IO exceeds thresholds.
- **Blue/Green Deployments**: Create a cloned environment, deploy there, validate, then swap CNAMEs.
- **Backups**: Store database snapshots and S3 lifecycle transitions to Glacier for long-term retention.
- **IaC**: Consider migrating to AWS CDK or Terraform to codify infrastructure.

---

## 9. Final Verification Checklist

- [ ] `DEBUG=False` and `DJANGO_ALLOWED_HOSTS` configured correctly.
- [ ] Elastic Beanstalk deployment returns HTTP 200 on `/health/` or root endpoint.
- [ ] Static assets load from S3/CloudFront.
- [ ] File uploads succeed and appear in the S3 bucket under the media prefix.
- [ ] Migrations applied and admin login works over HTTPS.
- [ ] CloudWatch alarms and log streaming enabled.
- [ ] New relic/Sentry (optional) connected for error tracking.

---

## 10. Troubleshooting

| Symptom | Resolution |
| --- | --- |
| `ImproperlyConfigured: SECRET_KEY` missing | Ensure `DJANGO_SECRET_KEY` is set in EB environment |
| 502/504 errors from ALB | Check EB health dashboard, view logs (`eb logs`), verify Gunicorn boot |
| Static files return 403 | Update S3 bucket policy, confirm `AWS_STORAGE_BUCKET_NAME` and ACL settings |
| Database connection timeouts | Confirm security groups, use RDS `Database_URL` with SSL, verify `DATABASE_SSL_REQUIRE` |
| `collectstatic` failure on deploy | Ensure IAM role has `s3:PutObject` and `s3:ListBucket`, bucket exists |

---

## 11. Next Steps

- Add automated smoke tests hitting critical endpoints post-deploy.
- Wire up Sentry or AWS Error Reporting for exception monitoring.
- Configure GitHub Actions pipeline to run `python -m compileall`, `python -m pytest`, and `eb deploy`.
- Register a custom domain and update DNS A/AAAA records to the ALB alias.

Happy shipping! 🚀
