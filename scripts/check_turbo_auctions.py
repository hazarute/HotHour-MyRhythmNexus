import sys
import os
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db
from app.core.timezone import now_tr, to_tr_aware


def _fmt_dt(value):
    if not value:
        return "-"
    dt = to_tr_aware(value)
    if not dt:
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


async def check_turbo_auctions():
    await db.connect()
    try:
        auctions = await db.auction.find_many(order={"id": "asc"})
        now = now_tr()

        print("\n=== TURBO AUCTION CHECK ===")
        print(f"Now (TR): {_fmt_dt(now)}")
        print()

        turbo_count = 0
        for auction in auctions:
            status = getattr(auction, "status", "-")
            turbo_enabled = bool(getattr(auction, "turboEnabled", False))
            turbo_started_at = getattr(auction, "turboStartedAt", None)
            end_time = to_tr_aware(getattr(auction, "endTime", None))

            remaining_min = None
            if end_time is not None:
                remaining_min = round((end_time - now).total_seconds() / 60, 2)

            is_turbo = turbo_started_at is not None
            if is_turbo:
                turbo_count += 1

            print(
                f"#{getattr(auction, 'id', '-'):>2} | {getattr(auction, 'title', '-')[:28]:<28} | "
                f"status={status:<9} | enabled={str(turbo_enabled):<5} | "
                f"startedAt={_fmt_dt(turbo_started_at):<19} | remainingMin={remaining_min if remaining_min is not None else '-'}"
            )

        print()
        print(f"Turbo active count (turboStartedAt not null): {turbo_count}")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(check_turbo_auctions())
