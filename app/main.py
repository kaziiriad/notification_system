from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.endpoints.notification import notification_router


def run_migrations():
    """Run database migrations on startup."""
    import subprocess
    import os
    
    migrations_dir = os.path.join(os.getcwd(), "migration")
    original_dir = os.getcwd()
    
    try:
        os.chdir(migrations_dir)
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Database migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        os.chdir(original_dir)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Run database migrations
    run_migrations()
    yield
    # Shutdown
    print("Application shutting down...")


app = FastAPI(
    lifespan=lifespan,
    title="Notification System API",
    version="1.0.0",
    description="API for managing notifications across multiple channels including push, email, and SMS.",
    contact={
        "name": "Support Team",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.include_router(notification_router, prefix="/api/v1/notifications", tags=["Notifications"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Notification System API. Use /api/v1/notifications for endpoints."}
@app.get("/health")
async def read_health():
    return {"status": "healthy", "version": "1.0.0"}    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
