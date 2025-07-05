import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.endpoints.notification import notification_router


async def run_migrations():
    """Run database migrations on startup."""
    # Correctly locate the migration directory relative to this file
    project_root = Path(__file__).parent.parent
    migrations_dir = project_root / "migration"
    alembic_ini_path = migrations_dir / "alembic.ini"

    # Ensure alembic is run from the correct virtual environment
    alembic_executable = str(Path(sys.executable).parent / "alembic")

    print(f"Running migrations from: {alembic_ini_path}")

    process = await asyncio.create_subprocess_exec(
        alembic_executable,
        "-c",
        str(alembic_ini_path),
        "upgrade",
        "head",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print("Migration failed!")
        print(f"Exit Code: {process.returncode}")
        print(f"STDOUT: {stdout.decode().strip()}")
        print(f"STDERR: {stderr.decode().strip()}")
        raise RuntimeError("Could not apply database migrations.")
    
    print("Database migrations completed successfully.")
    if stdout:
        print(f"STDOUT: {stdout.decode().strip()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application startup...")
    await run_migrations()
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