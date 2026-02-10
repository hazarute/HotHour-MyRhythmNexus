from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


def _to_dt(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    # assume ISO string
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


class PriceService:
    @staticmethod
    def _to_decimal(v) -> Decimal:
        return Decimal(str(v))

    @classmethod
    def compute_current_price(cls, auction: dict, now: Optional[datetime] = None) -> Tuple[Decimal, dict]:
        """Compute current auction price and return (price, details).

        auction: dict-like with keys `startPrice`, `floorPrice`, `dropIntervalMins`,
        `dropAmount`, `startTime`, `endTime`, and optional turbo keys:
        `turboEnabled`, `turboTriggerMins`, `turboDropAmount`, `turboIntervalMins`.
        """
        now = now or datetime.now(timezone.utc)

        start_price = cls._to_decimal(auction.get("startPrice") or auction.get("start_price"))
        floor_price = cls._to_decimal(auction.get("floorPrice") or auction.get("floor_price") or "0.00")
        drop_interval = int(auction.get("dropIntervalMins") or auction.get("drop_interval_mins") or 60)
        drop_amount = cls._to_decimal(auction.get("dropAmount") or auction.get("drop_amount") or "0.00")

        start_dt = _to_dt(auction.get("startTime") or auction.get("start_time"))
        end_dt = _to_dt(auction.get("endTime") or auction.get("end_time"))

        if start_dt is None:
            # no schedule -> return start price
            return (start_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), {})

        if now < start_dt:
            return (start_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), {"reason": "not_started"})

        price = start_price

        # normal drops
        if drop_interval > 0:
            elapsed_min = int((now - start_dt).total_seconds() // 60)
            normal_drops = elapsed_min // drop_interval
            price -= drop_amount * normal_drops
        else:
            normal_drops = 0

        turbo_applied = 0
        # turbo mode
        if auction.get("turboEnabled") or auction.get("turbo_enabled"):
            turbo_trigger = int(auction.get("turboTriggerMins") or auction.get("turbo_trigger_mins") or 0)
            turbo_drop = cls._to_decimal(auction.get("turboDropAmount") or auction.get("turbo_drop_amount") or "0.00")
            turbo_interval = int(auction.get("turboIntervalMins") or auction.get("turbo_interval_mins") or 1)
            if end_dt is not None:
                remaining_min = int((end_dt - now).total_seconds() // 60)
                if remaining_min <= turbo_trigger:
                    # turbo start time
                    turbo_start = end_dt - timedelta(minutes=turbo_trigger)
                    if now > turbo_start:
                        elapsed_turbo_min = int((now - turbo_start).total_seconds() // 60)
                        turbo_applied = elapsed_turbo_min // max(1, turbo_interval)
                        price -= turbo_drop * turbo_applied

        # enforce floor
        if price < floor_price:
            price = floor_price

        price = price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        details = {
            "start_price": str(start_price),
            "floor_price": str(floor_price),
            "normal_drops": int(normal_drops),
            "turbo_drops": int(turbo_applied),
        }
        return price, details


price_service = PriceService()
