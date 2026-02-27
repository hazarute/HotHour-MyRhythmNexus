"""
Socket Service - Emit real-time events to connected clients.

All emit helpers follow the same convention:
  - Auction-scoped events  → room "auction:{auction_id}"
  - User-scoped events     → room "user:{user_id}"

Import and call these helpers from AuctionService / BookingService / API endpoints.
"""

from datetime import datetime
from app.core.socket import sio
from app.core.timezone import now_tr


def _now_iso() -> str:
    return now_tr().isoformat()


async def emit_price_update(auction_id: int, current_price: str, details: dict = None) -> None:
    """
    Broadcast latest price for an auction to all subscribers.

    Triggered after: scheduled price drops, forced price recalculations.

    Payload:
        {
            "auction_id": int,
            "current_price": str,       # decimal as string to preserve precision
            "details": dict | null,     # price engine details (stage, drops, etc.)
            "timestamp": str            # ISO-8601 UTC
        }
    """
    room = f"auction:{auction_id}"
    payload = {
        "auction_id": auction_id,
        "current_price": current_price,
        "details": details or {},
        "timestamp": _now_iso(),
    }
    await sio.emit("price_update", payload, room=room)


async def emit_turbo_triggered(
    auction_id: int,
    turbo_started_at,
    remaining_minutes: float = None,
) -> None:
    """
    Notify all auction subscribers that Turbo Mode has been activated.

    Payload:
        {
            "auction_id": int,
            "turbo_started_at": str,    # ISO-8601 UTC
            "remaining_minutes": float | null,
            "timestamp": str
        }
    """
    room = f"auction:{auction_id}"
    if isinstance(turbo_started_at, datetime):
        turbo_started_at = turbo_started_at.isoformat()
    payload = {
        "auction_id": auction_id,
        "turbo_started_at": turbo_started_at,
        "remaining_minutes": remaining_minutes,
        "timestamp": _now_iso(),
    }
    await sio.emit("turbo_triggered", payload, room=room)


async def emit_booking_confirmed(
    user_id: int,
    auction_id: int,
    booking_code: str,
    locked_price: str,
    status: str,
) -> None:
    """
    Send a personal booking-confirmation event to the user who just booked.

    Payload (sent to room "user:{user_id}"):
        {
            "booking_code": str,
            "auction_id": int,
            "locked_price": str,
            "status": str,
            "timestamp": str
        }
    """
    user_room = f"user:{user_id}"
    payload = {
        "booking_code": booking_code,
        "auction_id": auction_id,
        "locked_price": str(locked_price),
        "status": status,
        "timestamp": _now_iso(),
    }
    await sio.emit("booking_confirmed", payload, room=user_room)


async def emit_auction_booked(auction_id: int, booking_code: str) -> None:
    """
    Notify ALL auction subscribers (public broadcast) that the auction has been taken.
    Other users watching the same auction will know it's no longer available.

    Payload:
        {
            "auction_id": int,
            "booking_code": str,   # abbreviated/public reference
            "timestamp": str
        }
    """
    room = f"auction:{auction_id}"
    payload = {
        "auction_id": auction_id,
        "booking_code": booking_code,
        "timestamp": _now_iso(),
    }
    await sio.emit("auction_booked", payload, room=room)
