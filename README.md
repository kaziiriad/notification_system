# Notification System

A microservice for sending notifications via email, SMS, and push notifications. Built with FastAPI, SQLAlchemy, PostgreSQL, RabbitMQ (direct consumer pattern), and structured JSON logging.

## Features

- **Multi-Channel Notifications** — Send via email (SendGrid), SMS (Twilio), push (Firebase)
- **Scheduled Notifications** — Schedule delivery at a future time
- **Priority Queuing** — Critical alerts delivered first
- **Direct MQ Consumer** — No Celery, worker consumes RabbitMQ directly with pika
- **Retry with Backoff** — 3 retry attempts (1s, 2s, 4s delays) on send failure
- **Idempotency** — Worker skips already-processed notifications
- **Structured Logging** — JSON-formatted logs for production observability
- **JWT Service Auth** — Service-to-service authentication with scoped tokens

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  PostgreSQL  │     │  RabbitMQ  │
│   (REST)   │     │  (metadata) │     │  (broker)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                        │
       └────────────────┬──────────────────────┘
                        │
                   ┌────▼────┐
                   │ Worker  │ (NotificationConsumer)
                   │ (pika)  │
                   └────┬────┘
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
           Email      SMS       Push
         (SendGrid) (Twilio)  (FCM)
```

## API Endpoints

### Authentication
```bash
# Get service token
POST /api/v1/auth/token
{
  "service_id": "my-service",
  "service_secret": "service-secret",
  "scope": ["notifications:read", "notifications:write"]
}
```

### Create Notification (requires `notifications:write` scope)
```bash
POST /api/v1/notifications/
Authorization: Bearer <token>
{
  "user_ids": [1, 2],
  "channel": "email",
  "priority": "high",
  "subject": "Hello",
  "content": "Notification body"
}
```

### Get Notification (requires `notifications:read` scope)
```bash
GET /api/v1/notifications/{id}
Authorization: Bearer <token>
```

### List Notifications (requires `notifications:read` scope)
```bash
GET /api/v1/notifications/?page=1&page_size=10
Authorization: Bearer <token>
```

## Quick Start

```bash
# Start all services (Docker)
make up

# API available at http://localhost:8000/docs
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `CELERY_BROKER_URL` | RabbitMQ connection | `amqp://guest:guest@rabbitmq:5672/` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Must change in prod |
| `SERVICE_API_SECRET` | Service credential for token mint | `service-secret-change-in-production` |
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
│   ├── recipient_resolver.py
│   └── rabbitmq_publisher.py  # Direct MQ publisher
├── worker/
│   └── consumer.py         # Direct RabbitMQ consumer (pika)
└── tests/                  # Test suite
```

## Database Schema

**notifications** — id, sender_user_id, subject, priority, channel, content, status, scheduled_at, sent_at, created_at, updated_at

**notification_recipients** — id, notification_id, user_id, email, phone_number, push_token, status, delivered_at, failed_reason, retry_count

## Notification Flow

```
API Request → NotificationService.create_notification()
           → Create DB record (PENDING)
           → Resolve recipients
           → Publish to RabbitMQ (RabbitMQPublisher)
           → Update status (QUEUED)
           → Return NotificationResponse

Worker → NotificationConsumer._process_message()
      → Check if already SENT (idempotency)
      → NotificationService.process_notification()
      → ChannelServiceFactory.create_service(channel)
      → Send via provider (SendGrid/Twilio/FCM)
      → Update status (SENT or FAILED on exhaustion)

## Authentication Flow

```
1. Service calls POST /api/v1/auth/token with service_id + service_secret
2. API returns JWT token with scopes (expires in 60 min)
3. Service includes JWT in Authorization: Bearer <token> header
4. Protected endpoints validate JWT and check required scopes
```
```