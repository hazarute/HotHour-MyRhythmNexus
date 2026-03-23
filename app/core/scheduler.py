from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.auction.auction_service import auction_service
from app.services.booking.booking_service import booking_service

scheduler = AsyncIOScheduler()

async def update_auctions_job():
    """
    Her 60 saniyede çalışan periyodik iş:
    1. DRAFT/ACTIVE ilan durumlarını kontrol eder ve fiyatları senkronize eder.
    2. Hizmet saatinden 30 dk. sonra hâlâ PENDING olan rezervasyonları iptal eder.
    """
    try:
        await auction_service.check_pending_auctions()
        await booking_service.auto_cancel_overdue_pending_reservations()
    except Exception as e:
        print(f"[Scheduler] Error: {e}")

def start_scheduler():
    scheduler.add_job(update_auctions_job, "interval", seconds=60)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
