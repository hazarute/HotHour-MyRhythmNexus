from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.auction.auction_service import auction_service
from app.core.socket import sio
from app.core.db import db

scheduler = AsyncIOScheduler()

async def update_auctions_job():
    """
    Periodic job to update auction statuses and broadcast changes via WebSocket.
    Delegates to auction_service.check_pending_auctions() which handles all
    lifecycle transitions (DRAFT->ACTIVE, ACTIVE->EXPIRED/SOLD, price sync).
    """
    try:
        await auction_service.check_pending_auctions()
    except Exception as e:
        print(f"Scheduler Error: {e}")

def start_scheduler():
    scheduler.add_job(update_auctions_job, "interval", seconds=60)  # Run every minute
    scheduler.start()
