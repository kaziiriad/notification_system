# Notification System

A robust and scalable notification system designed to send notifications across multiple channels, including email, SMS, and push notifications. Built with a modern technology stack, this system is designed for high performance and reliability.

## Features

-   **Multi-Channel Notifications:** Supports sending notifications via email, SMS, and push notifications.
-   **Scheduled Notifications:** Schedule notifications to be sent at a future date and time.
-   **Notification Priorities:** Assign priorities to notifications to ensure that critical alerts are delivered first.
-   **Recipient Management:** Easily manage recipients and their contact information.
-   **Scalable Architecture:** Built with a microservices-based architecture to handle high volumes of notifications.
-   **Asynchronous Processing:** Uses Celery and RabbitMQ for asynchronous task processing to ensure that notifications are sent without blocking the API.
-   **Database Migrations:** Uses Alembic to manage database schema changes.

## Technology Stack

-   **Backend:** FastAPI
-   **Database:** PostgreSQL
-   **Asynchronous Tasks:** Celery
-   **Message Broker:** RabbitMQ
-   **Result Backend:** Redis
-   **Database Migrations:** Alembic
-   **Dependency Management:** uv
-   **Testing:** pytest

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose
-   Python 3.12+

### Local Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/notification-system.git
    cd notification-system
    ```

2.  **Create a `.env` file:**

    Copy the `.env.example` file to a new file named `.env` and update the values as needed.

    ```bash
    cp .env.example .env
    ```

3.  **Run the application:**

    ```bash
    docker-compose up -d
    ```

## Configuration

The application is configured using environment variables. See the `.env.example` file for a list of available variables.

## Running Tests

To run the tests, use the following command:

```bash
pytest
```

## API Endpoints

The API is documented using Swagger UI. To access the documentation, go to `http://localhost:8000/docs` in your browser.

### Create Notification

-   **URL:** `/api/v1/notifications/`
-   **Method:** `POST`
-   **Body:**

    ```json
    {
      "user_ids": [1, 2],
      "channel": "email",
      "priority": "high",
      "subject": "Test Subject",
      "content": "Test Content"
    }
    ```

## Project Structure

```
.
├── app
│   ├── api
│   │   ├── endpoints
│   │   └── schemas
│   ├── core
│   ├── db
│   │   ├── nosql
│   │   └── sql
│   ├── services
│   ├── tests
│   ├── utils
│   └── worker
├── docker
├── migration
└── README.md
```
