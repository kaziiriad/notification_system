# Gemini Project Context: Notification System

This document provides a summary of the project structure, key components, and conventions to guide development and ensure consistency.

## Project Overview

This project is a notification system designed to send notifications through various channels, including email, SMS, and push notifications. It is built with a FastAPI backend, a PostgreSQL database, and Celery for asynchronous task processing.

### Key Technologies

-   **Backend:** FastAPI
-   **Database:** PostgreSQL
-   **Asynchronous Tasks:** Celery with RabbitMQ as the message broker and Redis as the result backend.
-   **Database Migrations:** Alembic
-   **Dependency Management:** `uv` with `pyproject.toml`
-   **Testing:** `pytest` with `pytest-asyncio`, `pytest-mock`, and `pytest-cov`.

### Project Structure

-   `app/`: The main application directory.
    -   `api/`: Contains the API endpoints and schemas.
    -   `core/`: Core application settings and configuration.
    -   `db/`: Database models, repositories, and connection management.
    -   `services/`: Business logic for handling notifications, channels, and recipients.
    -   `tests/`: Unit, integration, and end-to-end tests.
    -   `utils/`: Utility functions and classes.
    -   `worker/`: Celery worker tasks.
-   `docker/`: Docker-related files, including `docker-compose.yml` and `Dockerfile.api`.
-   `migration/`: Alembic database migration scripts.
-   `pyproject.toml`: Project dependencies and settings.

### How to Run the Application

The application is designed to be run with Docker Compose. The `docker-compose.yml` file defines the following services:

-   `app`: The FastAPI application.
-   `db`: The PostgreSQL database.
-   `rabbitmq`: The RabbitMQ message broker.
-   `worker`: The Celery worker.

To run the application, use the following command:

```bash
docker-compose up -d
```

### Testing

The project uses `pytest` for testing. The tests are located in the `app/tests` directory. To run the tests, use the following command:

```bash
pytest
```

### Key Files

-   `app/main.py`: The main entry point for the FastAPI application.
-   `app/core/config.py`: Application configuration settings.
-   `app/db/sql/models.py`: SQLAlchemy database models.
-   `app/db/sql/repositories.py`: Database repository classes for interacting with the database.
-   `app/services/notification_service.py`: The main service for creating and processing notifications.
-   `app/worker/tasks.py`: Celery tasks for asynchronous processing.
-   `docker-compose.yml`: Docker Compose configuration for running the application and its services.
-   `pyproject.toml`: Project dependencies and settings.
-   `alembic.ini`: Alembic configuration for database migrations.
