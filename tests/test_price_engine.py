from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.services.price_service import price_service


def test_price_not_started():
    start = datetime(2026, 2, 12, 12, 0, tzinfo=timezone.utc)
    auction = {
        "startPrice": "100.00",
        "floorPrice": "10.00",
        "dropIntervalMins": 30,
        "dropAmount": "5.00",
        "startTime": start.isoformat(),
    }
    now = start - timedelta(minutes=1)
    price, details = price_service.compute_current_price(auction, now=now)
    assert price == Decimal("100.00")
    assert details.get("reason") == "not_started"


def test_single_drop():
    start = datetime(2026, 2, 12, 12, 0, tzinfo=timezone.utc)
    auction = {
        "startPrice": "200.00",
        "floorPrice": "50.00",
        "dropIntervalMins": 30,
        "dropAmount": "20.00",
        "startTime": start.isoformat(),
    }
    now = start + timedelta(minutes=30)
    price, details = price_service.compute_current_price(auction, now=now)
    assert price == Decimal("180.00")
    assert details["normal_drops"] == 1


def test_floor_enforced():
    start = datetime(2026, 2, 12, 12, 0, tzinfo=timezone.utc)
    auction = {
        "startPrice": "100.00",
        "floorPrice": "30.00",
        "dropIntervalMins": 10,
        "dropAmount": "25.00",
        "startTime": start.isoformat(),
    }
    # after 3 drops would be 25, but floor is 30
    now = start + timedelta(minutes=30)
    price, details = price_service.compute_current_price(auction, now=now)
    assert price == Decimal("30.00")


def test_turbo_mode_applies_extra_drops():
    start = datetime(2026, 2, 12, 10, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=120)
    auction = {
        "startPrice": "500.00",
        "floorPrice": "100.00",
        "dropIntervalMins": 60,
        "dropAmount": "50.00",
        "startTime": start.isoformat(),
        "endTime": end.isoformat(),
        "turboEnabled": True,
        "turboTriggerMins": 30,
        "turboDropAmount": "20.00",
        "turboIntervalMins": 5,
    }
    # now is 15 minutes into turbo window -> should apply floor((15)/5)=3 turbo drops
    now = end - timedelta(minutes=15)
    price, details = price_service.compute_current_price(auction, now=now)
    # normal drops: elapsed = 105 min -> 1 normal drop (60 min)
    # price after normal: 450.00
    # turbo drops: 3 * 20 = 60 -> 390.00
    assert price == Decimal("390.00")
    assert details["turbo_drops"] == 3
