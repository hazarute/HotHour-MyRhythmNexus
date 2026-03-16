from datetime import datetime
from decimal import Decimal
from typing import Optional, Any

from app.core.db import db
from app.core.timezone import now_tr, to_tr_aware
from app.models.enums import AuctionStatus, ReservationStatus
from app.services import socket_service
from app.services.price_service import price_service
from app.utils.auction_mapper import auction_mapper

# Lifecycle metodlarında db.auction.update vb. yaparken kullanılacak standart include ilişkileri:
DEFAULT_INCLUDES = {
    "studio": {
        "include": {
            "sectors": {
                "include": {"sector": True}
            }
        }
    },
    "serviceCategory": {
        "include": {"sector": True}
    }
}

class AuctionLifecycleManager:
    """
    Müzayedenin yaşam döngüsünü (zaman, kural, fiyat ve tetikleyiciler) yönetir.
    Orkestratörün veri işlemlerinden ziyade 'iş kurallarını' işlettiği yerdir.
    """

    @staticmethod
    def determine_initial_status(start_time: Optional[datetime], end_time: Optional[datetime]) -> str:
        now_value = now_tr()
        if start_time and end_time and start_time <= now_value <= end_time:
            return AuctionStatus.ACTIVE.value
        elif start_time and now_value < start_time:
            return AuctionStatus.DRAFT.value
        return AuctionStatus.EXPIRED.value

    @staticmethod
    async def sync_current_price(auction: Any, now: Optional[datetime] = None, emit_event: bool = False) -> Any:
        if not auction:
            return None

        if getattr(auction, "status", None) != AuctionStatus.ACTIVE.value:
            return auction

        mapping = auction_mapper.to_mapping(auction)
        now_value = to_tr_aware(now) if now else now_tr()

        computed_price, details = price_service.compute_current_price(mapping, now=now_value)
        current_price = mapping.get("currentPrice")
        auction_id = getattr(auction, "id", None)

        if auction_id is not None and (current_price is None or Decimal(str(current_price)) != Decimal(str(computed_price))):
            auction = await db.auction.update(
                where={"id": auction_id},
                data={"currentPrice": computed_price},
                include=DEFAULT_INCLUDES
            )

            if emit_event and auction is not None:
                await socket_service.emit_price_update(
                    auction_id=getattr(auction, "id", auction_id),
                    current_price=str(computed_price),
                    details=details or {},
                )

        return auction

    @staticmethod
    async def check_and_update_status(auction: Any) -> Any:
        if not auction:
            return None

        now = now_tr()
        start_time = to_tr_aware(getattr(auction, "startTime", None))
        end_time = to_tr_aware(getattr(auction, "endTime", None))

        if not start_time or not end_time:
            return auction

        updated = False
        new_status = auction.status

        if auction.status == AuctionStatus.DRAFT.value and start_time <= now < end_time:
            new_status = AuctionStatus.ACTIVE.value
            updated = True
        elif auction.status == AuctionStatus.ACTIVE.value and now >= end_time:
            new_status = AuctionStatus.EXPIRED.value
            updated = True
        elif auction.status == AuctionStatus.DRAFT.value and now >= end_time:
            new_status = AuctionStatus.EXPIRED.value
            updated = True

        if updated:
            auction = await db.auction.update(
                where={"id": auction.id},
                data={"status": new_status},
                include=DEFAULT_INCLUDES
            )
            mapping = auction_mapper.to_mapping(auction)
            mapping["status"] = getattr(auction, "status", new_status)
            await socket_service.emit_auction_updated(mapping)

        return auction

    @staticmethod
    async def sync_status_with_reservation(auction: Any) -> Any:
        if not auction:
            return None

        auction_id = getattr(auction, "id", None)
        if auction_id is None:
            return auction

        reservations = await db.reservation.find_many(where={"auctionId": auction_id})
        if not reservations:
            return auction

        reservation = reservations[0]

        reservation_status = str(getattr(reservation, "status", "")).upper()
        auction_status = str(getattr(auction, "status", "")).upper()

        target_status = None
        if reservation_status and reservation_status != ReservationStatus.CANCELLED.value and auction_status != AuctionStatus.SOLD.value:
            target_status = AuctionStatus.SOLD.value
        elif reservation_status == ReservationStatus.CANCELLED.value and auction_status != AuctionStatus.CANCELLED.value:
            target_status = AuctionStatus.CANCELLED.value

        if target_status and target_status != auction_status:
            auction = await db.auction.update(
                where={"id": auction.id},
                data={"status": target_status},
                include=DEFAULT_INCLUDES
            )

        return auction

    @staticmethod
    async def check_and_trigger_turbo(auction_id: int, now: Optional[datetime] = None) -> dict:
        now_value = to_tr_aware(now) if now else now_tr()

        auction = await db.auction.find_unique(where={"id": auction_id})
        if not auction:
            return {"triggered": False, "reason": "auction_not_found", "turbo_started_at": None}

        turbo_enabled = getattr(auction, "turboEnabled", False) or getattr(auction, "turbo_enabled", False)
        if not turbo_enabled:
            return {"triggered": False, "reason": "turbo_not_enabled", "turbo_started_at": None}

        turbo_started_at = getattr(auction, "turboStartedAt", None)
        if turbo_started_at is not None:
            return {
                "triggered": False,
                "reason": "turbo_already_triggered",
                "turbo_started_at": turbo_started_at,
            }

        end_time = getattr(auction, "endTime", None) or getattr(auction, "end_time", None)
        end_time = to_tr_aware(end_time)
        if end_time is None:
            return {"triggered": False, "reason": "invalid_end_time", "turbo_started_at": None}

        remaining_min = (end_time - now_value).total_seconds() / 60
        turbo_trigger_mins = getattr(auction, "turboTriggerMins", None) or getattr(auction, "turbo_trigger_mins", 120)

        if remaining_min <= turbo_trigger_mins:
            await db.auction.update(
                where={"id": auction_id},
                data={"turboStartedAt": now_value}
            )
            await socket_service.emit_turbo_triggered(
                auction_id=auction_id,
                turbo_started_at=now_value,
                remaining_minutes=round(remaining_min, 2),
            )
            return {
                "triggered": True,
                "reason": "turbo_condition_met",
                "turbo_started_at": now_value,
                "remaining_minutes": round(remaining_min, 2),
            }

        return {
            "triggered": False,
            "reason": "turbo_condition_not_met",
            "turbo_started_at": None,
            "remaining_minutes": round(remaining_min, 2),
        }

    @staticmethod
    async def ensure_turbo_triggered(auction: Any, now: Optional[datetime] = None) -> Any:
        if not auction:
            return None

        auction_id = getattr(auction, "id", None)
        if auction_id is None:
            return auction

        auction_status = str(getattr(auction, "status", "")).upper()
        if auction_status != AuctionStatus.ACTIVE.value:
            return auction

        result = await AuctionLifecycleManager.check_and_trigger_turbo(auction_id, now=now)
        if result.get("triggered"):
            refreshed = await db.auction.find_unique(where={"id": auction_id}, include=DEFAULT_INCLUDES)
            return refreshed or auction

        return auction

auction_lifecycle_manager = AuctionLifecycleManager()