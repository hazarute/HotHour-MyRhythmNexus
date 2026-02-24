"""
Socket.io AsyncServer Setup

Architecture:
- One AsyncServer instance (singleton) shared across the app
- Room-based subscriptions: "auction:{id}" and "user:{id}"
- Clients join rooms to receive targeted events

Events (Client → Server):
  subscribe_auction   {"auction_id": int}  → join room "auction:{id}"
  unsubscribe_auction {"auction_id": int}  → leave room "auction:{id}"
  subscribe_user      {"user_id": int}     → join room "user:{id}"

Events (Server → Client):
  price_update        room="auction:{id}"  → {"auction_id", "current_price", "details", "timestamp"}
  turbo_triggered     room="auction:{id}"  → {"auction_id", "turbo_started_at", "remaining_minutes"}
  booking_confirmed   room="user:{id}"     → {"booking_code", "auction_id", "locked_price", "status"}
  auction_booked      room="auction:{id}"  → {"auction_id", "booking_code"}  (public: auction is taken)
"""

import socketio

# CORS origins accepted by the Socket.io server
_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000", "*"]

# Singleton AsyncServer (async_mode="asgi" required for FastAPI/Starlette)
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=_CORS_ORIGINS,
    logger=False,
    engineio_logger=False,
)


# ─────────────────────────────────────────────
# Connection lifecycle
# ─────────────────────────────────────────────

@sio.event
async def connect(sid: str, environ: dict, auth: dict = None):
    """Called when a client connects."""
    print(f"[Socket.io] Client connected: {sid}")


@sio.event
async def disconnect(sid: str):
    """Called when a client disconnects."""
    print(f"[Socket.io] Client disconnected: {sid}")


# ─────────────────────────────────────────────
# Room management events
# ─────────────────────────────────────────────

@sio.event
async def subscribe_auction(sid: str, data: dict):
    """
    Client asks to receive updates for a specific auction.
    Expected payload: {"auction_id": <int>}
    """
    auction_id = data.get("auction_id")
    if auction_id is None:
        await sio.emit("error", {"message": "auction_id required"}, to=sid)
        return
    room = f"auction:{auction_id}"
    await sio.enter_room(sid, room)
    await sio.emit("subscribed", {"room": room}, to=sid)
    print(f"[Socket.io] {sid} subscribed to {room}")


@sio.event
async def unsubscribe_auction(sid: str, data: dict):
    """Leave an auction room."""
    auction_id = data.get("auction_id")
    if auction_id is None:
        return
    room = f"auction:{auction_id}"
    await sio.leave_room(sid, room)
    await sio.emit("unsubscribed", {"room": room}, to=sid)


@sio.event
async def subscribe_user(sid: str, data: dict):
    """
    Client asks to receive personal notifications (booking confirmations, etc.).
    Expected payload: {"user_id": <int>}
    NOTE: In production, validate this with JWT – do not trust user-supplied user_id blindly.
    """
    user_id = data.get("user_id")
    if user_id is None:
        await sio.emit("error", {"message": "user_id required"}, to=sid)
        return
    room = f"user:{user_id}"
    await sio.enter_room(sid, room)
    await sio.emit("subscribed", {"room": room}, to=sid)
    print(f"[Socket.io] {sid} subscribed to {room}")
