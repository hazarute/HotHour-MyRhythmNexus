from typing import Dict, Optional
from app.core.db import db
from app.services import socket_service

class NotificationService:
    async def create_admin_notifications(
        self,
        *,
        title: str,
        message: str,
        notification_type: str,
        reservation_id: Optional[int] = None,
        auction_id: Optional[int] = None,
    ):
        notification_model = getattr(db, "notification", None)
        if notification_model is None:
            return

        admins = await db.user.find_many(where={"role": "ADMIN"})
        for admin in admins:
            admin_id = getattr(admin, "id", None)
            if admin_id is None:
                continue

            notification = await notification_model.create(
                data={
                    "userId": admin_id,
                    "reservationId": reservation_id,
                    "auctionId": auction_id,
                    "type": notification_type,
                    "title": title,
                    "message": message,
                    "isRead": False,
                }
            )
            await socket_service.emit_notification_created(
                notification_id=notification.id,
                notification_type=notification_type,
            )

    async def get_admin_cancellation_notifications(self, admin_user_id: int, limit: int = 20) -> Dict:
        notification_model = getattr(db, "notification", None)
        if notification_model is None:
            return {"notifications": [], "unread_count": 0}

        all_notifications = await notification_model.find_many(
            where={"userId": admin_user_id},
            order={"createdAt": "desc"},
            take=max(limit * 3, limit),
        )

        allowed_types = {"AUTO_CANCEL_NO_SHOW", "USER_CANCELLED_BY_CUSTOMER"}
        notifications = [
            item for item in all_notifications
            if str(getattr(item, "type", "")).upper() in allowed_types
        ][:limit]

        unread_count = sum(1 for item in notifications if not bool(getattr(item, "isRead", False)))

        return {
            "notifications": [
                {
                    "id": item.id,
                    "title": item.title,
                    "message": item.message,
                    "type": item.type,
                    "is_read": item.isRead,
                    "reservation_id": item.reservationId,
                    "auction_id": item.auctionId,
                    "created_at": item.createdAt.isoformat() if item.createdAt else None,
                }
                for item in notifications
            ],
            "unread_count": unread_count,
        }

    async def mark_notification_as_read(self, notification_id: int, admin_user_id: int) -> bool:
        notification_model = getattr(db, "notification", None)
        if notification_model is None:
            return False

        item = await notification_model.find_unique(where={"id": notification_id})
        if not item:
            return False

        if item.userId != admin_user_id:
            return False

        await notification_model.update(
            where={"id": notification_id},
            data={"isRead": True},
        )
        return True

    async def delete_admin_notification(self, notification_id: int, admin_user_id: int) -> bool:
        notification_model = getattr(db, "notification", None)
        if notification_model is None:
            return False

        item = await notification_model.find_unique(where={"id": notification_id})
        if not item:
            return False

        if item.userId != admin_user_id:
            return False

        await notification_model.delete(where={"id": notification_id})
        await socket_service.emit_notification_deleted(notification_id=notification_id)
        return True

    async def delete_admin_read_notifications(self, admin_user_id: int) -> int:
        notification_model = getattr(db, "notification", None)
        if notification_model is None:
            return 0

        allowed_types = {"AUTO_CANCEL_NO_SHOW", "USER_CANCELLED_BY_CUSTOMER"}
        all_notifications = await notification_model.find_many(
            where={"userId": admin_user_id},
            order={"createdAt": "desc"},
        )

        deleted_count = 0
        for item in all_notifications:
            notification_type = str(getattr(item, "type", "")).upper()
            is_read = bool(getattr(item, "isRead", False))
            if notification_type in allowed_types and is_read:
                await notification_model.delete(where={"id": item.id})
                await socket_service.emit_notification_deleted(notification_id=item.id)
                deleted_count += 1

        return deleted_count

notification_service = NotificationService()