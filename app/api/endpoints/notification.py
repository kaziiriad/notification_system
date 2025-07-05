<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.notification import NotificationCreate, NotificationResponse, NotificationListResponse
from app.db.sql.connection import get_db  # Assuming you have this dependency
from app.services.notification_service import NotificationService

notification_router = APIRouter(tags=["Notifications"])

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)

@notification_router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    request: NotificationCreate, 
    notification_service: NotificationService = Depends(get_notification_service)
):

    """
    Create a new notification.
    
    - **user_ids**: List of user IDs to notify
    - **emails**: List of email addresses (optional)
    - **sms_numbers**: List of SMS numbers (optional)
    - **priority**: Notification priority (low, medium, high, critical)
    - **channel**: Delivery channel (push, email, sms, all)
    - **content**: Notification content
    - **scheduled_at**: Optional scheduled time (ISO format)
    """

    try:
        response = await notification_service.create_notification(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )

@notification_router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str, 
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get a notification by ID.
    
    - **notification_id**: The ID of the notification to retrieve
    """
    try:
        notification = notification_service.get_notification_status(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        return NotificationResponse(
            id=notification.id,
            status=notification.status.value,
            created_at=notification.created_at,
            scheduled_at=notification.scheduled_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification: {str(e)}"
        )

@notification_router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    page: int = 1,
    page_size: int = 10,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    List all notifications with pagination.
    
    Returns a list of all notifications in the system by page.
    """
    try:
        notifications, total_count = notification_service.list_notifications(page, page_size)
        
        notification_responses = [
            NotificationResponse(
                id=n.id,
                status=n.status.value,
                created_at=n.created_at,
                scheduled_at=n.scheduled_at
            ) for n in notifications
        ]
        
        return NotificationListResponse(
            notifications=notification_responses,
            total=total_count,
            page=page,
            per_page=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list notifications: {str(e)}"
        )
=======
from fastapi import APIRouter, HTTPException, Depends

from ..schemas.notification import NotificationCreate

notification_router = APIRouter(tags=["Notifications"])

@notification_router.post("/create")
async def create_notification(notification: NotificationCreate):

    return {
        "message": "Notification created successfully",
        "notification" : notification.model_dump_json()
    }
>>>>>>> a1ecdf7b4d1c4a83234c658db78c8214db5dc0f2
