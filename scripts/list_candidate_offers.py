#!/usr/bin/env python3
"""List candidate offers for weekly automation.

Usage examples:
  python scripts/list_candidate_offers.py --days-back 90 --status EXPIRED,SOLD --studio-id 5

Run this on Railway where `DATABASE_URL` is configured.
"""
from __future__ import annotations

import os
import sys
import argparse
import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

# Ensure project root is on sys.path so `from app...` imports work when running
# the script from a container where the CWD may be /app or similar.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core.db import connect_db, disconnect_db
from app.services.auction.auction_service import auction_service


def _default(o: Any):
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)


async def main(argv=None):
    parser = argparse.ArgumentParser(description="List candidate offers for automation")
    parser.add_argument("--days-back", type=int, default=90, help="lookback window in days")
    parser.add_argument("--status", type=str, default="EXPIRED,SOLD",
                        help="comma-separated statuses to include (default: EXPIRED,SOLD)")
    parser.add_argument("--studio-id", type=int, default=None, help="optional studio id filter")
    parser.add_argument("--limit", type=int, default=0, help="limit results (0 = no limit)")
    args = parser.parse_args(argv)

    statuses = {s.strip() for s in args.status.split(",") if s.strip()}
    cutoff = datetime.utcnow() - timedelta(days=args.days_back)

    await connect_db()
    try:
        items = await auction_service.list_auctions(include_computed=True)

        out = []
        for item in items:
            created = item.get("created_at")
            if created is None:
                out.append(item)
                continue

            # created may be string or datetime
            if isinstance(created, str):
                try:
                    created_dt = datetime.fromisoformat(created)
                except Exception:
                    created_dt = None
            else:
                created_dt = created

            if created_dt and created_dt < cutoff:
                continue

            if statuses and item.get("status") not in statuses:
                continue

            if args.studio_id is not None and item.get("studioId") != args.studio_id:
                continue

            out.append(item)
            if args.limit and len(out) >= args.limit:
                break

        print(json.dumps(out, default=_default, ensure_ascii=False, indent=2))
    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
