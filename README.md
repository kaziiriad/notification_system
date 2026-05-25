# Notification System

A microservice for sending notifications via email, SMS, and push notifications. Built with FastAPI, SQLAlchemy, PostgreSQL, Celery, and RabbitMQ.

## Features

- **Multi-Channel Notifications** — Send via email (SendGrid), SMS (Twilio), push (Firebase)
- **Scheduled Notifications** — Schedule delivery at a future time
- **Priority Queuing** — Critical alerts delivered first
- **Asynchronous Processing** — Celery + RabbitMQ handles delivery without blocking the API
- **Structured Logging** — JSON-formatted logs for production observability

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  PostgreSQL  │     │  RabbitMQ  │
│   (REST)   │     │  (metadata) │     │  (broker)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                         │
       │         ┌──────────────┐                 │
       └────────▶│   Celery     │◀────────────────┘
                 │   Worker    │
                 └──────────────┘
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
           Email      SMS       Push
         (SendGrid) (Twilio)  (FCM)
```

## Quick Start

```bash
# Start all services
make up

# API available at http://localhost:8000/docs
```

## API Endpoints

### Create Notification
```bash
POST /api/v1/notifications/
{
  "user_ids": [1, 2],
  "channel": "email",
  "priority": "high",
  "subject": "Hello",
  "content": "Notification body"
}
```

### Get Notification
```bash
GET /api/v1/notifications/{id}
```

### List Notifications
```bash
GET /api/v1/notifications/?page=1&page_size=10
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `CELERY_BROKER_URL` | RabbitMQ connection | `amqp://guest:guest@rabbitmq:5672//` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `rpc://guest:guest@rabbitmq:5672//` |
| `SENDGRID_API_KEY` | SendGrid API key | Optional |
| `SENDGRID_FROM_EMAIL` | Sender email | Optional |
| `TWILIO_ACCOUNT_SID` | Twilio account | Optional |
| `TWILIO_AUTH_TOKEN` | Twilio auth | Optional |
| `FCM_SERVER_KEY` | Firebase Cloud Messaging | Optional |

## Commands

```bash
make up          # Start services
make down        # Stop services
make logs        # View logs
make test        # Run tests
make migrate     # Run migrations
make shell       # Shell in app container
make shell-db    # PostgreSQL shell
```

## Testing

```bash
make test
# Or without Docker:
uv run pytest
```

## Project Structure

```
app/
├── api/                    # FastAPI routes and schemas
│   ├── endpoints/          # Route handlers
│   └── schemas/            # Pydantic models
├── core/                   # Config, logging
├── db/
│   ├── nosql/              # MongoDB models (user data)
│   └── sql/                # PostgreSQL models + repositories
├── services/               # Business logic
│   ├── notification_service.py
│   ├── channel_services.py # Email/SMS/Push factories
│   └── recipient_resolver.py
├── utils/                  # Validators, interfaces, utilities
├── worker/                 # Celery tasks
└── tests/                  # Test suite
```

## Database Schema

**notifications** — id, sender_user_id, subject, priority, channel, content, status, scheduled_at, sent_at, created_at, updated_at

**notification_recipients** — id, notification_id, user_id, email, phone_number, push_token, status, delivered_at, failed_reason, retry_count