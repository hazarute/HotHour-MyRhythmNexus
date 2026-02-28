from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.db import connect_db, disconnect_db
from app.core.socket import sio
from app.api import auth
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.auction_service import auction_service
from app.services.booking_service import booking_service
import socketio

scheduler = AsyncIOScheduler()

async def update_auctions_job():
    """
    Periodic job to update auction statuses.
    Only checks DRAFT and ACTIVE auctions to reduce server load.
    """
    try:
        # Fetch status candidates (DRAFT and ACTIVE only)
        count = await auction_service.check_pending_auctions()
        auto_cancelled = await booking_service.auto_cancel_overdue_pending_reservations()
        # print(f"Checked {count} pending auctions for status updates.")
    except Exception as e:
        print(f"Scheduler Error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    await connect_db()
    
    # Simple Background Scheduler
    scheduler.add_job(update_auctions_job, 'interval', seconds=60)
    scheduler.start()
    
    yield
    # Shutdown: Disconnect DB
    await disconnect_db()
    scheduler.shutdown()

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        lifespan=lifespan
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include Routers
    application.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    # Auctions router (admin-only create)
    from app.api import auctions, reservations
    application.include_router(auctions.router, prefix="/api/v1/auctions", tags=["auctions"])
    # Reservations router (booking/status)
    application.include_router(reservations.router)
    # Note: test-only helpers removed; tests use DB fixtures instead

    @application.get("/health")
    async def health_check():
        return {
            "status": "active", 
            "version": settings.PROJECT_VERSION,
            "project": settings.PROJECT_NAME
        }

    return application

_fastapi_app = create_application()

# Mount Socket.io ASGI app alongside FastAPI
# All Socket.io traffic goes through /socket.io/
# FastAPI handles everything else
app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=_fastapi_app,
    socketio_path="/socket.io",
)
