from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.api.endpoints.notification import notification_router
from app.api.endpoints.auth import router as auth_router
from app.core.logging_config import configure_logging

logger = logging.getLogger(__name__)

# Configure logging at startup
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application startup")
    yield
    # Shutdown
    logger.info("Application shutting down")


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
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Notification System API. Use /api/v1/notifications for endpoints."}
@app.get("/health")
async def read_health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
