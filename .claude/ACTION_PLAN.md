# Project Improvement Action Plan

This document provides a checklist for implementing the architectural improvements outlined in the `ROADMAP.md`.

---

## Short-Term Goals (Foundation)

### ✅ Build a Robust CI/CD Pipeline
- [ ] Create a GitHub Actions workflow file (`.github/workflows/ci-cd.yml`).
- [ ] Configure the workflow to trigger on push and pull requests.
- [ ] Add a linting step using `ruff` and `black`.
- [ ] Add a testing step that runs the `pytest` suite.
- [ ] Add a step to build Docker images for the `app` and `worker` services.
- [ ] (Optional CD) Add a step to push Docker images to a container registry (e.g., Docker Hub, GitHub Container Registry).

### ✅ Secure the API with Authentication
- [ ] Add a dependency for JWT token management (e.g., `python-jose`).
- [ ] Create a new service for handling user authentication and token generation.
- [ ] Implement a `/token` endpoint to issue JWT tokens based on user credentials.
- [ ] Create a FastAPI dependency to verify JWT tokens in incoming requests.
- [ ] Protect the notification creation endpoint with the new authentication dependency.

### ✅ Implement Structured Logging
- [ ] Add `structlog` to the project dependencies.
- [ ] Create a central logging configuration module (`app/core/logging_config.py`).
- [ ] Configure `structlog` with processors for timestamps, log levels, and JSON rendering.
- [ ] Integrate the logging configuration with FastAPI/Uvicorn in `app/main.py`.
- [ ] Integrate the logging configuration with Celery in `app/worker/tasks.py`.
- [ ] Replace all `print()` statements with `structlog` log calls.

---

## Mid-Term Goals (Scalability & Security)

### ✅ Migrate to Kubernetes
- [ ] Create Kubernetes deployment and service YAML files for the FastAPI application.
- [ ] Create Kubernetes deployment and service YAML files for the Celery worker.
- [ ] Create a Kubernetes StatefulSet and service for PostgreSQL.
- [ ] Create Kubernetes deployments and services for RabbitMQ and Redis.
- [ ] Create a Helm chart to package and manage all Kubernetes configurations.
- [ ] Configure Horizontal Pod Autoscalers (HPAs) for the API and worker deployments.

### ✅ Introduce an API Gateway
- [ ] Choose and deploy an API Gateway (e.g., Kong, Traefik).
- [ ] Configure the gateway to route traffic to the FastAPI service.
- [ ] Implement SSL termination at the gateway.
- [ ] Configure rate limiting and other security policies.

### ✅ Implement a Secret Management Solution
- [ ] Choose and deploy a secret management tool (e.g., HashiCorp Vault).
- [ ] Store database credentials and other secrets in the vault.
- [ ] Modify the application to fetch secrets from the vault at startup.

---

## Long-Term Goals (Enterprise-Grade Observability)

### ✅ Implement Monitoring and Alerting
- [ ] Add Prometheus client libraries to the FastAPI application.
- [ ] Expose a `/metrics` endpoint with relevant application metrics.
- [ ] Deploy Prometheus to scrape metrics from the application.
- [ ] Deploy Grafana and create dashboards to visualize the metrics.
- [ ] Deploy Alertmanager and configure alerts for critical conditions.

### ✅ Implement Distributed Tracing
- [ ] Integrate the OpenTelemetry SDK into the FastAPI application and Celery workers.
- [ ] Configure an exporter to send traces to a backend (e.g., Jaeger, Zipkin).
- [ ] Add instrumentation to trace requests across services.
