from typing import Dict, Optional, List
from app.core.db import db
from app.models.enums import ReservationStatus

class BookingRepository:
    """Veritabanından (Prisma) sadece Rezervasyon bilgilerini alan salt okunur Repository katmanıdır."""

    async def get_reservation(self, reservation_id: int) -> Optional[Dict]:
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

    async def get_user_reservations(self, user_id: int) -> List[Dict]:
        reservations = await db.reservation.find_many(
            where={"userId": user_id},
            include={"auction": {"include": {"studio": True}}},
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
                "status": getattr(res, 'status', ReservationStatus.CONFIRMED.value),
                "reserved_at": res.reservedAt.isoformat() if res.reservedAt else None,
                "studio": getattr(res.auction, "studio", None) if res.auction else None,
            }
            for res in reservations
        ]

    async def get_all_reservations(self, studio_id: int | None = None) -> List[Dict]:
        reservations = await db.reservation.find_many(
            include={
                "user": True,
                "auction": True
            },
            order={"reservedAt": "desc"}
        )

        if studio_id is not None:
            reservations = [
                res for res in reservations
                if getattr(getattr(res, "auction", None), "studioId", None) == studio_id
            ]

        studio_ids = set()
        for res in reservations:
            auction = getattr(res, "auction", None)
            if auction:
                studio_id_val = getattr(auction, "studioId", None)
                if studio_id_val is not None:
                    studio_ids.add(studio_id_val)

        studio_name_map = {}
        if studio_ids:
            studios = await db.studio.find_many(where={"id": {"in": list(studio_ids)}})
            studio_name_map = {studio.id: studio.name for studio in studios}

        result = []
        for res in reservations:
            auction = getattr(res, "auction", None)
            studio_id_val = getattr(auction, "studioId", None) if auction else None

            studio_name = None
            if auction is not None:
                studio_obj = getattr(auction, "studio", None)
                if studio_obj is not None:
                    studio_name = getattr(studio_obj, "name", None)

            if studio_name is None and studio_id_val is not None:
                studio_name = studio_name_map.get(studio_id_val)

            if studio_name is None:
                studio_name = "Bilinmeyen İşletme"

            result.append({
                "id": res.id,
                "auction_id": res.auctionId,
                "user_id": res.userId,
                "user_name": res.user.fullName if res.user else "Unknown User",
                "auction_title": auction.title if auction else "Unknown Auction",
                "scheduled_at": getattr(auction, "scheduledAt", None) if auction else None,
                "studio_id": studio_id_val,
                "studio_name": studio_name,
                "locked_price": str(res.lockedPrice),
                "booking_code": res.bookingCode,
                "status": getattr(res.status, 'name', str(res.status)) if res.status else ReservationStatus.CONFIRMED.value,
                "created_at": res.reservedAt.isoformat() if res.reservedAt else None,
            })

        return result

    async def get_reservation_with_details(self, reservation_id: int, studio_id: int | None = None) -> Optional[Dict]:
        reservations = await db.reservation.find_many(
            where={"id": reservation_id},
            include={
                "user": True,
                "auction": True
            },
            take=1,
        )

        reservation = reservations[0] if reservations else None
        if not reservation:
            return None

        if studio_id is not None and getattr(getattr(reservation, "auction", None), "studioId", None) != studio_id:
            return None
            
        return {
            "id": reservation.id,
            "booking_code": reservation.bookingCode,
            "status": getattr(reservation.status, 'name', str(reservation.status)),
            "locked_price": str(reservation.lockedPrice),
            "reserved_at": reservation.reservedAt.isoformat() if reservation.reservedAt else None,
            "user": {
                "id": reservation.userId,
                "full_name": reservation.user.fullName if reservation.user else "Unknown User",
                "email": reservation.user.email if reservation.user else "",
                "phone": reservation.user.phone if reservation.user else "",
                "is_verified": reservation.user.isVerified if reservation.user else False,
            },
            "auction": {
                "id": reservation.auctionId,
                "title": reservation.auction.title if reservation.auction else "Unknown Auction",
                "start_time": reservation.auction.startTime.isoformat() if reservation.auction else None,
                "end_time": reservation.auction.endTime.isoformat() if reservation.auction else None,
                "status": getattr(reservation.auction.status, 'name', str(reservation.auction.status)) if reservation.auction else "UNKNOWN",
            }
        }

booking_repository = BookingRepository()
