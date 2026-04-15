#!/usr/bin/env python3
"""Create weekly offers based on selected templates.

This script creates auctions for the next occurrence of the weekly window:
- start: Wednesday 03:00 (UTC)
- end:   Sunday 22:00 (UTC)

Service time (`scheduled_at`) is set to the Tuesday after the auction end at 18:00 (UTC).

Usage:
  python scripts/create_weekly_offers.py [--dry-run] [--push]

Note: run in Railway one-off or container where project root is /app; script ensures
`app` package is importable by adding project root to `sys.path`.
"""
from __future__ import annotations

import os
import sys
import argparse
import asyncio
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from typing import List, Dict, Any

# Make sure project root is importable when running from containers
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core.db import connect_db, disconnect_db
from app.services.auction.auction_service import auction_service


TEMPLATES: List[Dict[str, Any]] = [
    # From provided terminal output: Gündüz Kuşağı: 8 Seans Fonksiyonel Antrenman (serviceCategoryId:3)
    {
        "title": "💪 Gündüz Kuşağı: 8 Seans Fonksiyonel Antrenman",
        "description": "Günün en verimli saatlerini spora ayır! Hafta içi 10:00-16:00 arası seanslarda geçerli bu fırsatı kaçırma. (Seanslar stüdyo müsaitliğine göre ortaklaşa belirlenir.)",
        "allowed_gender": "FEMALE",
        "start_price": "8040",
        "floor_price": "3216",
        "drop_interval_mins": 60,
        "drop_amount": "37.75",
        "turbo_enabled": True,
        "turbo_trigger_mins": 120,
        "turbo_drop_amount": "24.54",
        "turbo_interval_mins": 10,
        "serviceCategoryId": 3,
        "studioId": 1,
    },
    # Salsa Ateşi: 4 Seans Özel Ders (serviceCategoryId:4) — will create 2 copies
    {
        "title": "💃 Salsa Ateşi: 4 Seans Özel Ders",
        "description": "Birebir çalışmayla salsa öğrenmeye hazır mısın? Haftada 1 saat, toplam 4 seans. (Seanslar stüdyo müsaitliğine göre ortaklaşa belirlenir.)",
        "allowed_gender": "ANY",
        "start_price": "12000",
        "floor_price": "6000",
        "drop_interval_mins": 60,
        "drop_amount": "46.95",
        "turbo_enabled": True,
        "turbo_trigger_mins": 120,
        "turbo_drop_amount": "30.52",
        "turbo_interval_mins": 10,
        "serviceCategoryId": 4,
        "studioId": 1,
    },
    # Gündüz Kuşağı: 8 Seans Reformer (serviceCategoryId:2)
    {
        "title": "🔥 Gündüz Kuşağı: 8 Seans Reformer",
        "description": "Hafta içi 10:00-16:00 arası dilediğin saati seç, en uygun fiyata spora başla! (Seanslar stüdyo müsaitliğine göre ortaklaşa belirlenir.)",
        "allowed_gender": "FEMALE",
        "start_price": "8040",
        "floor_price": "3216",
        "drop_interval_mins": 60,
        "drop_amount": "37.75",
        "turbo_enabled": True,
        "turbo_trigger_mins": 120,
        "turbo_drop_amount": "24.54",
        "turbo_interval_mins": 10,
        "serviceCategoryId": 2,
        "studioId": 1,
    },
    # Hafta Sonu Kaçamağı: 8 Seans Reformer (serviceCategoryId:2)
    {
        "title": "✨ Hafta Sonu Kaçamağı: 8 Seans Reformer",
        "description": "Hafta sonu moduna reformer ile gir, yeni haftaya zinde başla! Cumartesi-Pazar 12:00-17:00 arası seanslar için. (Seanslar stüdyo müsaitliğine göre ortaklaşa belirlenir.)",
        "allowed_gender": "FEMALE",
        "start_price": "8040",
        "floor_price": "3216",
        "drop_interval_mins": 60,
        "drop_amount": "37.75",
        "turbo_enabled": True,
        "turbo_trigger_mins": 120,
        "turbo_drop_amount": "24.54",
        "turbo_interval_mins": 10,
        "serviceCategoryId": 2,
        "studioId": 1,
    },
]


def next_weekday(base: datetime, weekday: int) -> datetime:
    """Return the next datetime (>= base) that has the given weekday (0=Mon..6=Sun)."""
    days_ahead = (weekday - base.weekday() + 7) % 7
    if days_ahead == 0 and base.time() > time(23, 59, 59):
        days_ahead = 7
    return (base + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)


def build_times_for_week(start_wed: datetime) -> Dict[str, datetime]:
    # start_wed is a date at midnight UTC for a Wednesday; set start at 03:00
    start_time = start_wed.replace(hour=3, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    # Sunday is weekday 6
    days_to_sun = (6 - start_wed.weekday()) % 7
    end_day = (start_wed + timedelta(days=days_to_sun)).replace(hour=22, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    # Service scheduled_at: following Tuesday at 18:00
    # Find next Tuesday (weekday=1) after end_day
    search_base = end_day + timedelta(days=1)
    days_to_tue = (1 - search_base.weekday() + 7) % 7
    service_at = (search_base + timedelta(days=days_to_tue)).replace(hour=18, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    return {"start_time": start_time, "end_time": end_day, "scheduled_at": service_at}


async def create_offers(dry_run: bool = True):
    now = datetime.now(timezone.utc)
    # get next Wednesday (weekday=2)
    wed = next_weekday(now, 2)
    times = build_times_for_week(wed)

    planned: List[Dict[str, Any]] = []

    # counts: Reformer (gunduz), Hafta Sonu Reformer, Fonksiyonel -> 1 each; Salsa -> 2
    for tpl in TEMPLATES:
        count = 2 if tpl.get("serviceCategoryId") == 4 else 1
        for i in range(count):
            data = {
                "title": tpl["title"] + (" (Kopya)" if count > 1 and i > 0 else ""),
                "description": tpl.get("description"),
                "allowed_gender": tpl.get("allowed_gender"),
                "start_price": Decimal(tpl.get("start_price")),
                "floor_price": Decimal(tpl.get("floor_price")),
                "start_time": times["start_time"],
                "end_time": times["end_time"],
                "scheduled_at": times["scheduled_at"],
                "drop_interval_mins": tpl.get("drop_interval_mins"),
                "drop_amount": Decimal(tpl.get("drop_amount")),
                "turbo_enabled": tpl.get("turbo_enabled"),
                "turbo_trigger_mins": tpl.get("turbo_trigger_mins"),
                "turbo_drop_amount": Decimal(tpl.get("turbo_drop_amount")),
                "turbo_interval_mins": tpl.get("turbo_interval_mins"),
                "serviceCategoryId": tpl.get("serviceCategoryId"),
            }
            planned.append({"data": data, "studio_id": tpl.get("studioId")})

    print(f"Planned to create {len(planned)} offers for week starting {wed.date()}")

    if dry_run:
        for idx, item in enumerate(planned, 1):
            print(f"[{idx}] {item['data']['title']} -> start={item['data']['start_time'].isoformat()} end={item['data']['end_time'].isoformat()} scheduled_at={item['data']['scheduled_at'].isoformat()}")
        return

    await connect_db()
    try:
        created_ids = []
        for item in planned:
            try:
                created = await auction_service.create_auction(item["data"], studio_id=item["studio_id"])
                created_id = getattr(created, "id", None)
                created_ids.append(created_id)
                print(f"Created auction id={created_id} title={item['data']['title']}")
            except Exception as e:
                print(f"Error creating auction {item['data']['title']}: {e}")
        print(f"Done. Created {len(created_ids)} auctions: {created_ids}")
    finally:
        await disconnect_db()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show planned creations without touching DB")
    parser.add_argument("--push", action="store_true", help="(ignored) kept for compatibility")
    args = parser.parse_args(argv)
    asyncio.run(create_offers(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
