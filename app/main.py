from fastapi import FastAPI
from api.endpoints.notficiation import notification_router

app = FastAPI(
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
