from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.db import connect_db, disconnect_db
from app.api import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    await connect_db()
    yield
    # Shutdown: Disconnect DB
    await disconnect_db()

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
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include Routers
    application.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    # Auctions router (admin-only create)
    from app.api import auctions
    application.include_router(auctions.router, prefix="/api/v1/auctions", tags=["auctions"])
    # Note: test-only helpers removed; tests use DB fixtures instead

    @application.get("/health")
    async def health_check():
        return {
            "status": "active", 
            "version": settings.PROJECT_VERSION,
            "project": settings.PROJECT_NAME
        }

    return application

app = create_application()
