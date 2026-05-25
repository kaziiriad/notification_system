# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Notification System is a microservice for sending notifications via multiple channels (email, SMS, push notifications). Built with FastAPI, SQLAlchemy, PostgreSQL, Celery, and RabbitMQ.

## Architecture

- **FastAPI** - REST API endpoints
- **SQLAlchemy + PostgreSQL** - ORM and primary database (notifications, recipients)
- **MongoDB (motor)** - NoSQL data store (user data via `app/db/nosql/models.py`)
- **Celery + RabbitMQ** - Background task processing and message broker
- **Docker** - Containerized services

## Key Components

- `app/services/notification_service.py` - Core notification logic (create, process, list)
- `app/api/endpoints/notification.py` - REST API routes
- `app/worker/tasks.py` - Celery task definition (`send_notification_task`)
- `app/db/sql/models.py` - SQLAlchemy models (Notification, NotificationRecipient)
- `app/db/sql/repositories.py` - Repository pattern implementation
- `app/services/channel_services.py` - Channel factory (SendGrid, Twilio, Firebase)
- `app/services/recipient_resolver.py` - Resolves notification recipients

## API Endpoints

- `POST /api/v1/notifications/` - Create notification (returns NotificationResponse with id, status, created_at, scheduled_at)
- `GET /api/v1/notifications/{id}` - Get notification status
- `GET /api/v1/notifications/` - List notifications (pagination: page, page_size)

## Notification Flow

```
API Request → NotificationService.create_notification()
           → Create DB record (PENDING)
           → Resolve recipients
           → Create recipient records
           → Queue Celery task (send_notification_task.delay)
           → Update status (QUEUED or SCHEDULED)
           → Return NotificationResponse

Celery Worker → send_notification_task
             → NotificationService.process_notification()
             → Fetch recipients from DB
             → ChannelServiceFactory.create_service(channel)
             → Send via provider (SendGrid/Twilio/FCM)
             → Update status (SENT or FAILED)
```

## Development Commands

```bash
# Start all services (Docker)
docker compose up --build

# Stop services
docker compose down

# View logs
docker compose logs -f app worker

# Run migrations
docker compose exec app alembic upgrade head

# Run tests (inside container)
docker compose exec app pytest

# Single test file
docker compose exec app pytest app/tests/services/test_notification_service.py

# Single test
docker compose exec app pytest -xvs app/tests/services/test_notification_service.py::test_name
```

## Manual Commands (without Docker)

```bash
# Install dependencies
uv sync

# Run API
uv run fastapi dev app/main.py

# Run Celery worker
uv run celery -A app.worker.tasks.celery_app worker --loglevel=info

# Run migrations
uv run alembic upgrade head

# Create migration
uv run alembic revision --autogenerate -m "description"

# Run tests
uv run pytest
```

## Environment Setup

1. Copy `.env.example` to `.env` and configure
2. Key variables: `DATABASE_URL`, `CELERY_BROKER_URL` (RabbitMQ: `amqp://guest:guest@rabbitmq:5672//`)
3. Optional providers: `SENDGRID_API_KEY`, `TWILIO_*`, `FCM_SERVER_KEY`

## Testing

Integration tests marked with `@pytest.mark.integration`:

```bash
pytest -m integration
```

## Database Schema

**notifications** - id, sender_user_id, subject, priority, channel, content, status, scheduled_at, sent_at, created_at, updated_at

**notification_recipients** - id, notification_id, user_id, email, phone_number, push_token, status, delivered_at, failed_reason, retry_count

## Common Issues

- **Tables missing**: `alembic upgrade head`
- **Celery not processing**: Check RabbitMQ (`docker compose logs rabbitmq`) and worker status
- **Migrations failing**: Ensure models imported in `migration/alembic/env.py`