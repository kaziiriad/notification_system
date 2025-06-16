from fastapi import APIRouter, HTTPException, Depends

from ..schemas.notification import NotificationCreate

notification_router = APIRouter(tags=["Notifications"])

@notification_router.post("/create")
async def create_notification(notification: NotificationCreate):

    return {
        "message": "Notification created successfully",
        "notification" : notification.model_dump_json()
    }