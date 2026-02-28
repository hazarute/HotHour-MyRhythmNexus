"""
Booking Service - Implements Dutch Auction booking logic with Race Condition handling.

Key Design:
1. Atomic Operation: Use Prisma transaction to ensure atomicity
2. Unique Constraint: auctionId is UNIQUE in Reservation table (one auction = one reservation)
3. Price Locking: Current price at booking time is locked in reservation
4. Idempotent: If booking code already exists, return existing reservation
"""

from app.core.db import db
from app.core.timezone import now_tr, to_tr_aware
from app.services.price_service import price_service
from app.utils.booking_utils import generate_booking_code
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional, Tuple
from app.services import socket_service


class BookingError(Exception):
    """Base exception for booking errors"""
    pass


class AuctionNotFoundError(BookingError):
    """Raised when auction is not found"""
    pass


class AuctionNotActiveError(BookingError):
    """Raised when auction is not in ACTIVE status"""
    pass


class AuctionAlreadyBookedError(BookingError):
    """Raised when auction is already reserved (race condition or already booked)"""
    pass


class UserNotFoundError(BookingError):
    """Raised when user is not found"""
    pass


class AdminCannotBookError(BookingError):
    """Raised when admin user attempts to book an auction"""
    pass


class GenderNotEligibleError(BookingError):
    """Raised when user's gender is not eligible for this auction"""
    pass


class BookingService:
    """Service for managing booking/reservation operations"""

    async def _create_admin_notifications(
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

            await notification_model.create(
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

    async def auto_cancel_overdue_pending_reservations(self) -> int:
        now = now_tr()
        reservations = await db.reservation.find_many(where={"status": "PENDING_ON_SITE"})

        cancelled_count = 0
        for reservation in reservations:
            auction_id = getattr(reservation, "auctionId", None)
            user_id = getattr(reservation, "userId", None)

            auction = await db.auction.find_unique(where={"id": auction_id}) if auction_id else None
            user = await db.user.find_unique(where={"id": user_id}) if user_id else None

            if not auction:
                continue

            scheduled_at = to_tr_aware(getattr(auction, "scheduledAt", None))
            end_time = to_tr_aware(getattr(auction, "endTime", None))
            service_time = scheduled_at or end_time

            if not service_time or now < service_time:
                continue

            await self.cancel_reservation(reservation.id, cancel_source="AUTO_NO_SHOW")
            cancelled_count += 1

        return cancelled_count
    
    async def book_auction(
        self, 
        auction_id: int, 
        user_id: int
    ) -> Dict:
        """
        Book (reserve) an auction with a user at the current price.
        
        Race Condition Handling:
        - Use Prisma transaction for atomicity
        - auctionId is UNIQUE in Reservation table
        - If two users try simultaneously, only one succeeds (unique constraint violation)
        
        Args:
            auction_id: ID of auction to book
            user_id: ID of user booking
        
        Returns:
            Dict with reservation details {
                "id": int,
                "auction_id": int,
                "user_id": int,
                "locked_price": Decimal,
                "booking_code": str,
                "status": str,
                "reserved_at": datetime
            }
        
        Raises:
            AuctionNotFoundError: If auction doesn't exist
            AuctionNotActiveError: If auction is not in ACTIVE status
            AuctionAlreadyBookedError: If auction is already reserved (race condition)
            UserNotFoundError: If user doesn't exist
            BookingError: For other booking errors
        """
        
        # Step 1: Verify auction exists and is ACTIVE
        auction = await db.auction.find_unique(where={"id": auction_id})
        if not auction:
            raise AuctionNotFoundError(f"Auction {auction_id} not found")
        
        if auction.status != "ACTIVE":
            existing_reservations = await db.reservation.find_many(where={"auctionId": auction_id})
            if existing_reservations:
                raise AuctionAlreadyBookedError(
                    f"Auction {auction_id} is already reserved or race condition detected"
                )
            raise AuctionNotActiveError(
                f"Auction {auction_id} is not active. Status: {auction.status}"
            )
        
        # Step 2: Verify user exists
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user_role = str(getattr(user, "role", "") or "").upper()
        if user_role == "ADMIN":
            raise AdminCannotBookError("Admin kullanıcılar rezervasyon yapamaz.")

        # Step 2.1: Verify gender eligibility rule
        allowed_gender = str(getattr(auction, "allowedGender", "ANY") or "ANY").upper()
        user_gender = str(getattr(user, "gender", "") or "").upper()
        if allowed_gender in {"FEMALE", "MALE"} and user_gender != allowed_gender:
            if allowed_gender == "FEMALE":
                raise GenderNotEligibleError("Bu oturum yalnızca kadın kullanıcılar içindir.")
            raise GenderNotEligibleError("Bu oturum yalnızca erkek kullanıcılar içindir.")
        
        # Step 3: Get current (locked) price
        # Note: We use the auction's currentPrice field directly
        # In a real scenario, this is already computed by price_service
        locked_price = auction.currentPrice
        
        # Step 4: Generate unique booking code
        booking_code = generate_booking_code()
        
        # Step 5: Create reservation (atomic operation with unique constraint)
        # If a concurrent request tries to create for same auction, Prisma will throw:
        # UniqueConstraintViolationException (because auctionId is @unique)
        try:
            reservation = await db.reservation.create(
                data={
                    "auctionId": auction_id,
                    "userId": user_id,
                    "lockedPrice": locked_price,
                    "bookingCode": booking_code,
                    "status": "PENDING_ON_SITE",
                }
            )

            await db.auction.update(
                where={"id": auction_id},
                data={"status": "SOLD"}
            )
            
            result = {
                "id": reservation.id,
                "auction_id": reservation.auctionId,
                "user_id": reservation.userId,
                "locked_price": reservation.lockedPrice,
                "booking_code": reservation.bookingCode,
                "status": reservation.status,
                "reserved_at": reservation.reservedAt,
            }

            # Broadcast real-time events after successful booking
            await socket_service.emit_booking_confirmed(
                user_id=user_id,
                auction_id=auction_id,
                booking_code=reservation.bookingCode,
                locked_price=reservation.lockedPrice,
                status=reservation.status,
            )
            await socket_service.emit_auction_booked(
                auction_id=auction_id,
                booking_code=reservation.bookingCode,
            )

            return result
        
        except Exception as e:
            # Prisma's unique constraint violation
            # Check if it's because auctionId is already reserved
            error_msg = str(e).lower()
            if "unique constraint" in error_msg or "duplicate key" in error_msg:
                raise AuctionAlreadyBookedError(
                    f"Auction {auction_id} is already reserved or race condition detected"
                )
            raise BookingError(f"Booking failed: {str(e)}")
    
    async def get_reservation(self, reservation_id: int) -> Optional[Dict]:
        """Get reservation details by ID"""
        reservation = await db.reservation.find_unique(where={"id": reservation_id})
        if not reservation:
            return None
        
        return {
            "id": reservation.id,
            "auction_id": reservation.auctionId,
            "user_id": reservation.userId,
            "locked_price": reservation.lockedPrice,
            "booking_code": reservation.bookingCode,
            "status": reservation.status,
            "reserved_at": reservation.reservedAt,
        }
    
    async def get_reservation_by_code(self, booking_code: str) -> Optional[Dict]:
        """Get reservation details by booking code"""
        reservation = await db.reservation.find_unique(where={"bookingCode": booking_code})
        if not reservation:
            return None
        
        return {
            "id": reservation.id,
            "auction_id": reservation.auctionId,
            "user_id": reservation.userId,
            "locked_price": reservation.lockedPrice,
            "booking_code": reservation.bookingCode,
            "status": reservation.status,
            "reserved_at": reservation.reservedAt,
        }
    
    async def get_user_reservations(self, user_id: int) -> list[Dict]:
        """Get all reservations for a user with auction details"""
        reservations = await db.reservation.find_many(
            where={"userId": user_id},
            include={"auction": True},
            order={"reservedAt": "desc"}
        )
        
        return [
            {
                "id": res.id,
                "auction_id": res.auctionId,
                "auction_title": res.auction.title if res.auction else "Unknown Auction",
                "auction_description": res.auction.description if res.auction else "",
                "auction_start_time": res.auction.startTime if res.auction else None,
                "auction_end_time": res.auction.endTime if res.auction else None,
                "scheduled_at": getattr(res.auction, "scheduledAt", None) if res.auction else None,
                "user_id": res.userId,
                "locked_price": str(res.lockedPrice),
                "booking_code": res.bookingCode,
                "status": getattr(res, 'status', 'CONFIRMED'),
                "reserved_at": res.reservedAt.isoformat() if res.reservedAt else None,
            }
            for res in reservations
        ]
    
    async def get_all_reservations(self) -> list[Dict]:
        """
        Get all reservations with user and auction details.
        """
        reservations = await db.reservation.find_many(
            include={
                "user": True,
                "auction": True
            },
            order={"reservedAt": "desc"}
        )
        
        return [
            {
                "id": res.id,
                "auction_id": res.auctionId,
                "user_id": res.userId,
                "user_name": res.user.fullName if res.user else "Unknown User",
                "auction_title": res.auction.title if res.auction else "Unknown Auction",
                "scheduled_at": getattr(res.auction, "scheduledAt", None) if res.auction else None,
                "locked_price": str(res.lockedPrice),
                "booking_code": res.bookingCode,
                "status": getattr(res.status, 'name', str(res.status)) if res.status else 'CONFIRMED',
                "created_at": res.reservedAt.isoformat() if res.reservedAt else None,
            }
            for res in reservations
        ]

    async def get_reservation_with_details(self, reservation_id: int) -> Optional[Dict]:
        """
        Get detailed reservation info including User and Auction.
        """
        reservation = await db.reservation.find_unique(
            where={"id": reservation_id},
            include={
                "user": True,
                "auction": True
            }
        )
        if not reservation:
            return None
            
        return {
            "id": reservation.id,
            "booking_code": reservation.bookingCode,
            "status": getattr(reservation.status, 'name', str(reservation.status)),
            "locked_price": str(reservation.lockedPrice),
            # Use 'created_at' in response to match frontend expectations if needed, but 'reserved_at' is more accurate to model
            "reserved_at": reservation.reservedAt.isoformat() if reservation.reservedAt else None,
            
            # User Details
            "user": {
                "id": reservation.userId,
                "full_name": reservation.user.fullName if reservation.user else "Unknown User",
                "email": reservation.user.email if reservation.user else "",
                "phone": reservation.user.phone if reservation.user else "",
                "is_verified": reservation.user.isVerified if reservation.user else False,
            },
            
            # Auction Details
            "auction": {
                "id": reservation.auctionId,
                "title": reservation.auction.title if reservation.auction else "Unknown Auction",
                "start_time": reservation.auction.startTime.isoformat() if reservation.auction else None,
                "end_time": reservation.auction.endTime.isoformat() if reservation.auction else None,
                "status": getattr(reservation.auction.status, 'name', str(reservation.auction.status)) if reservation.auction else "UNKNOWN",
            }
        }

    async def cancel_reservation(self, reservation_id: int, cancel_source: str = "SYSTEM") -> bool:
        """
        Cancel a reservation (mark as CANCELLED).
        
        Args:
            reservation_id: ID of reservation to cancel
        
        Returns:
            True if successful, False if not found
        """
        reservation = await db.reservation.find_unique(where={"id": reservation_id})
        if not reservation:
            return False

        if str(getattr(reservation, "status", "")).upper() == "CANCELLED":
            return True

        auction_id = getattr(reservation, "auctionId", None)
        user_id = getattr(reservation, "userId", None)
        auction = await db.auction.find_unique(where={"id": auction_id}) if auction_id else None
        user = await db.user.find_unique(where={"id": user_id}) if user_id else None
        
        await db.reservation.update(
            where={"id": reservation_id},
            data={"status": "CANCELLED"}
        )

        if auction and str(getattr(auction, "status", "")).upper() != "CANCELLED":
            next_status = "CANCELLED"
            await db.auction.update(
                where={"id": auction.id},
                data={"status": next_status}
            )

        user_name = getattr(user, "fullName", "Bilinmeyen Kullanıcı")
        auction_title = getattr(auction, "title", "Bilinmeyen Oturum")
        booking_code = getattr(reservation, "bookingCode", "-")

        source_key = str(cancel_source or "").upper()
        if source_key == "AUTO_NO_SHOW":
            await self._create_admin_notifications(
                title="Otomatik Rezervasyon İptali",
                message=(
                    f'"{auction_title}" oturumu için {user_name} (kod: {booking_code}) '
                    "hizmet saatine kadar giriş yapmadığı için rezervasyon otomatik iptal edildi."
                ),
                notification_type="AUTO_CANCEL_NO_SHOW",
                reservation_id=reservation_id,
                auction_id=auction_id,
            )
        elif source_key == "USER":
            await self._create_admin_notifications(
                title="Müşteri Rezervasyonu İptal Etti",
                message=(
                    f'{user_name}, "{auction_title}" oturumu için rezervasyonunu '
                    f'(kod: {booking_code}) kullanıcı panelinden iptal etti.'
                ),
                notification_type="USER_CANCELLED_BY_CUSTOMER",
                reservation_id=reservation_id,
                auction_id=auction_id,
            )

        return True

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
                deleted_count += 1

        return deleted_count

    async def check_in_reservation(self, reservation_id: int) -> bool:
        """
        Mark a reservation as CHECKED_IN / COMPLETED.
        
        Args:
            reservation_id: ID of reservation to check in
        
        Returns:
            True if successful, False if not found
        """
        reservation = await db.reservation.find_unique(where={"id": reservation_id})
        if not reservation:
            return False
            
        await db.reservation.update(
            where={"id": reservation_id},
            data={"status": "COMPLETED"}
        )
        return True


# Singleton instance
booking_service = BookingService()
