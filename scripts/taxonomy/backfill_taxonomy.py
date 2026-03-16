#!/usr/bin/env python3
"""
Mevcut isletme ve firsat kayitlarini varsayilan taksonomiye gore esler.

Dry run varsayilandir.

Kullanim:
    python scripts/taxonomy/backfill_taxonomy.py
    python scripts/taxonomy/backfill_taxonomy.py --apply
    python scripts/taxonomy/backfill_taxonomy.py --apply --force-categories
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client
from scripts.taxonomy.seed_data import AUCTION_CATEGORY_KEYWORDS, STUDIO_SECTOR_KEYWORDS


def match_sector_slugs(studio_name: str) -> list[str]:
    haystack = (studio_name or "").lower()
    matches = []

    for sector_slug, keywords in STUDIO_SECTOR_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            matches.append(sector_slug)

    return matches


def match_category_slug(title: str, description: str | None) -> str | None:
    haystack = f"{title or ''} {description or ''}".lower()

    for category_slug, keywords in AUCTION_CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category_slug

    return None


async def backfill_taxonomy(apply_changes: bool, force_categories: bool) -> None:
    prisma = await create_client()

    try:
        sectors = await prisma.sector.find_many(where={"isActive": True})
        categories = await prisma.servicecategory.find_many(where={"isActive": True})

        sector_ids_by_slug = {item.slug: item.id for item in sectors}
        category_ids_by_slug = {item.slug: item.id for item in categories}

        if not sector_ids_by_slug or not category_ids_by_slug:
            print("Hata: backfill oncesi python scripts/taxonomy/seed_taxonomy.py calistirin.")
            return

        studios = await prisma.studio.find_many(include={"sectors": True})
        auctions = await prisma.auction.find_many(include={"serviceCategory": True, "studio": True})

        print("\n=== STUDIO -> SECTOR BACKFILL ===")
        studio_updates = 0
        for studio in studios:
            if studio.sectors:
                print(f"Atlandi: {studio.name} zaten {len(studio.sectors)} sektor ile bagli")
                continue

            matched_sector_slugs = match_sector_slugs(studio.name)
            if not matched_sector_slugs:
                print(f"Eslesme yok: {studio.name}")
                continue

            print(f"Plan: {studio.name} -> {', '.join(matched_sector_slugs)}")
            studio_updates += 1

            if not apply_changes:
                continue

            for sector_slug in matched_sector_slugs:
                sector_id = sector_ids_by_slug.get(sector_slug)
                if not sector_id:
                    continue
                await prisma.studiosector.create(
                    data={
                        "studioId": studio.id,
                        "sectorId": sector_id,
                    }
                )

        print("\n=== AUCTION -> SERVICE CATEGORY BACKFILL ===")
        auction_updates = 0
        for auction in auctions:
            if auction.serviceCategory and not force_categories:
                print(f"Atlandi: {auction.title} zaten kategoriye sahip")
                continue

            matched_category_slug = match_category_slug(auction.title, auction.description)
            if not matched_category_slug:
                print(f"Eslesme yok: {auction.title}")
                continue

            category_id = category_ids_by_slug.get(matched_category_slug)
            if not category_id:
                print(f"Kategori bulunamadi: {matched_category_slug} ({auction.title})")
                continue

            print(f"Plan: {auction.title} -> {matched_category_slug}")
            auction_updates += 1

            if not apply_changes:
                continue

            await prisma.auction.update(
                where={"id": auction.id},
                data={"serviceCategoryId": category_id},
            )

        print("\n=== OZET ===")
        print(f"Studio esleme adayi: {studio_updates}")
        print(f"Firsat kategori adayi: {auction_updates}")
        print("Mod: Uygulandi" if apply_changes else "Mod: Dry run")
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Varsayilan heuristic ile taxonomy backfill yapar.")
    parser.add_argument("--apply", action="store_true", help="Dry run yerine degisiklikleri uygula")
    parser.add_argument("--force-categories", action="store_true", help="Mevcut kategorisi olan firsatlari da yeniden esle")
    args = parser.parse_args()
    asyncio.run(backfill_taxonomy(apply_changes=args.apply, force_categories=args.force_categories))


if __name__ == "__main__":
    main()