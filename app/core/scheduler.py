from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.auction.auction_service import auction_service
from app.services.booking.booking_service import booking_service
from app.core.timezone import TR_TIMEZONE

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


async def create_weekly_offers_job():
    """
    Haftalık otomatik fırsat oluşturma job'u.
    Pazartesi/Çarşamba programlanmış olarak `scripts.create_weekly_offers.create_offers`
    fonksiyonunu çağırır (dry_run=False).
    """
    try:
        # Import here to avoid import-time side effects; the module lives in /scripts
        from scripts.create_weekly_offers import create_offers

        await create_offers(dry_run=False)
    except Exception as e:
        print(f"[Scheduler:create_weekly_offers_job] Error: {e}")


def start_scheduler():
    # Existing frequent job
    scheduler.add_job(update_auctions_job, "interval", seconds=60)

    # Weekly job: every Wednesday at 03:00 Turkey time
    scheduler.add_job(
        create_weekly_offers_job,
        "cron",
        day_of_week="wed",
        hour=3,
        minute=0,
        timezone=TR_TIMEZONE,
    )

    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
