from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from app.core.config import settings
from app.core.db import connect_db, disconnect_db
from app.core.socket import sio
from app.api import auth
from app.core.scheduler import start_scheduler, stop_scheduler
import socketio

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    start_scheduler()
    yield
    await disconnect_db()
    stop_scheduler()

def create_application() -> FastAPI:
    # Ensure uploads directory exists
    os.makedirs(os.path.join(os.getcwd(), 'uploads', 'studios'), exist_ok=True)
    
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        lifespan=lifespan
    )

    # Mount static files directory
    application.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include Routers
    application.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    from app.api import users
    application.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    from app.api import sectors, service_categories
    application.include_router(sectors.router, prefix="/api/v1/sectors", tags=["sectors"])
    application.include_router(service_categories.router, prefix="/api/v1/service-categories", tags=["service-categories"])
    # Studios router (admin studio management)
    from app.api import studios
    application.include_router(studios.router, prefix="/api/v1/studios", tags=["studios"])
    # Auctions router (admin-only create)
    from app.api import auctions, reservations
    application.include_router(auctions.router, prefix="/api/v1/auctions", tags=["auctions"])
    # Reservations router (booking/status)
    application.include_router(reservations.router)
    # Note: test-only helpers removed; tests use DB fixtures instead

    @application.get("/health")
    async def health_check():
        # Include Redis health information when available
        from app.core.redis_client import ping_redis

        redis_ok = ping_redis()
        return {
            "status": "active",
            "version": settings.PROJECT_VERSION,
            "project": settings.PROJECT_NAME,
            "redis": "available" if redis_ok else "unavailable",
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
