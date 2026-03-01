"""
Socket Service - Emit real-time events to connected clients.

All emit helpers follow the same convention:
  - Auction-scoped events  → room "auction:{auction_id}"
  - User-scoped events     → room "user:{user_id}"

Import and call these helpers from AuctionService / BookingService / API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from app.core.socket import sio
from app.core.timezone import now_tr


def _now_iso() -> str:
    return now_tr().isoformat()

def _sanitize_dict(d: dict) -> dict:
    """Recursively convert Decimals to strings and datetimes to ISO strings for JSON serialization."""
    if not isinstance(d, dict):
        return d
    result = {}
    for k, v in d.items():
        if isinstance(v, Decimal):
            result[k] = str(v)
        elif isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, dict):
            result[k] = _sanitize_dict(v)
        elif isinstance(v, list):
            result[k] = [
                str(i) if isinstance(i, Decimal) else 
                i.isoformat() if isinstance(i, datetime) else 
                _sanitize_dict(i) if isinstance(i, dict) else i 
                for i in v
            ]
        else:
            result[k] = v
    return result


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


# ─────────────────────────────────────────────
# Admin-scoped reservation & notification events
# (broadcast to ALL connected clients — no room filter)
# ─────────────────────────────────────────────

async def emit_reservation_created(
    reservation_id: int,
    booking_code: str,
    user_id: int,
    auction_id: int,
    status: str,
) -> None:
    """
    Broadcast to ALL clients when a new reservation is created.
    Admin panel uses this to refresh the reservations list in real-time.

    Payload:
        {
            "reservation_id": int,
            "booking_code": str,
            "user_id": int,
            "auction_id": int,
            "status": str,
            "timestamp": str
        }
    """
    payload = {
        "reservation_id": reservation_id,
        "booking_code": booking_code,
        "user_id": user_id,
        "auction_id": auction_id,
        "status": status,
        "timestamp": _now_iso(),
    }
    await sio.emit("reservation_created", payload)


async def emit_reservation_updated(
    reservation_id: int,
    status: str,
    auction_id: int = None,
) -> None:
    """
    Broadcast to ALL clients when a reservation's status changes.
    Covers check-in (COMPLETED) and admin-initiated status changes.

    Payload:
        {
            "reservation_id": int,
            "status": str,
            "auction_id": int | null,
            "timestamp": str
        }
    """
    payload = {
        "reservation_id": reservation_id,
        "status": status,
        "auction_id": auction_id,
        "timestamp": _now_iso(),
    }
    await sio.emit("reservation_updated", payload)


async def emit_reservation_cancelled(
    reservation_id: int,
    auction_id: int = None,
) -> None:
    """
    Broadcast to ALL clients when a reservation is cancelled.
    Admin panel uses this to refresh the list in real-time.

    Payload:
        {
            "reservation_id": int,
            "auction_id": int | null,
            "status": "CANCELLED",
            "timestamp": str
        }
    """
    payload = {
        "reservation_id": reservation_id,
        "auction_id": auction_id,
        "status": "CANCELLED",
        "timestamp": _now_iso(),
    }
    await sio.emit("reservation_cancelled", payload)


async def emit_notification_created(notification_id: int, notification_type: str = None) -> None:
    """
    Broadcast to ALL clients when an admin notification is created.
    Admin panel uses this to refresh the notification dropdown in real-time.

    Payload:
        {
            "notification_id": int,
            "type": str | null,
            "timestamp": str
        }
    """
    payload = {
        "notification_id": notification_id,
        "type": notification_type,
        "timestamp": _now_iso(),
    }
    await sio.emit("notification_created", payload)


async def emit_notification_deleted(notification_id: int) -> None:
    """
    Broadcast to ALL clients when an admin notification is deleted.

    Payload:
        {
            "notification_id": int,
            "timestamp": str
        }
    """
    payload = {
        "notification_id": notification_id,
        "timestamp": _now_iso(),
    }
    await sio.emit("notification_deleted", payload)


# ─────────────────────────────────────────────
# Global auction-scoped events
# (broadcast to ALL connected clients to update lists)
# ─────────────────────────────────────────────

async def emit_auction_created(auction: dict) -> None:
    """
    Broadcast to ALL clients when a new auction is created.
    """
    payload = {
        "auction": _sanitize_dict(auction),
        "timestamp": _now_iso(),
    }
    await sio.emit("auction_created", payload)


async def emit_auction_updated(auction: dict) -> None:
    """
    Broadcast to ALL clients when an auction is updated (e.g., status changed).
    """
    payload = {
        "auction": _sanitize_dict(auction),
        "timestamp": _now_iso(),
    }
    await sio.emit("auction_updated", payload)


async def emit_auction_deleted(auction_id: int) -> None:
    """
    Broadcast to ALL clients when an auction is deleted.
    """
    payload = {
        "auction_id": auction_id,
        "timestamp": _now_iso(),
    }
    await sio.emit("auction_deleted", payload)
