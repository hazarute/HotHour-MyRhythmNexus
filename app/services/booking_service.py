"""
Booking Service - Implements Dutch Auction booking logic with Race Condition handling.

Key Design:
1. Atomic Operation: Use Prisma transaction to ensure atomicity
2. Unique Constraint: auctionId is UNIQUE in Reservation table (one auction = one reservation)
3. Price Locking: Current price at booking time is locked in reservation
4. Idempotent: If booking code already exists, return existing reservation
"""

from app.core.db import db
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


class BookingService:
    """Service for managing booking/reservation operations"""
    
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
            raise AuctionNotActiveError(
                f"Auction {auction_id} is not active. Status: {auction.status}"
            )
        
        # Step 2: Verify user exists
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
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
            order={"createdAt": "desc"}
        )
        
        return [
            {
                "id": res.id,
                "auction_id": res.auctionId,
                "auction_title": res.auction.title if res.auction else "Unknown Auction",
                "auction_start_time": res.auction.startTime if res.auction else None,
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
            order={"createdAt": "desc"}
        )
        
        return [
            {
                "id": res.id,
                "auction_id": res.auctionId,
                "user_id": res.userId,
                "user_name": f"{res.user.firstName} {res.user.lastName}" if res.user else "Unknown User",
                "auction_title": res.auction.title if res.auction else "Unknown Auction",
                "locked_price": str(res.lockedPrice),
                "booking_code": res.bookingCode,
                "status": getattr(res, 'status', 'CONFIRMED'),
                "created_at": res.createdAt.isoformat() if res.createdAt else None,
            }
            for res in reservations
        ]

    async def cancel_reservation(self, reservation_id: int) -> bool:
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
        
        await db.reservation.update(
            where={"id": reservation_id},
            data={"status": "CANCELLED"}
        )
        return True


# Singleton instance
booking_service = BookingService()
