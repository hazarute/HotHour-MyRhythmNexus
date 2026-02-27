from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.auction_service import auction_service
from app.core.socket import sio
from app.core.db import db

scheduler = AsyncIOScheduler()

async def update_auctions_job():
    """
    Periodic job to update auction statuses and broadcast changes via WebSocket.
    """
    try:
        # 1. Update statuses in DB
        # We'll use a slightly different method to bulk update/check instead of one-by-one to be efficient
        # But for now, let's reuse the logic we just added to list_auctions
        # Ideally, we should have a dedicated service method for bulk updates
        
        # Fetch all non-final auctions (DRAFT, ACTIVE)
        # Note: Prisma current version might not support advanced filtering easily in one go
        # so we fetch potential candidates
        
        # Candidates for DRAFT -> ACTIVE
        # Candidates for ACTIVE -> EXPIRED
        
        # For simplicity and reliability in MVP phase, let's iterate over ALL non-final auctions
        # In production this should be optimized query
        
        auctions = await db.auction.find_many(
            where={
                "status": {
                    "in": ["DRAFT", "ACTIVE"]
                }
            }
        )
        
        for auction in auctions:
            # Check and update status (logic is in service)
            updated_auction = await auction_service._check_and_update_status(auction)
            
            # If status changed, broadcast via socket
            if updated_auction and updated_auction.status != auction.status:
                await sio.emit("auction_updated", {
                    "id": updated_auction.id,
                    "status": updated_auction.status,
                    "current_price": str(updated_auction.currentPrice)
                })
                
    except Exception as e:
        print(f"Scheduler Error: {e}")

def start_scheduler():
    scheduler.add_job(update_auctions_job, "interval", seconds=60) # Run every minute
    scheduler.start()
