#!/usr/bin/env python3
"""
Hizmet kategorisi listeleme scripti
Kullanim:
    python scripts/taxonomy/list_service_categories.py
    python scripts/taxonomy/list_service_categories.py --all
    python scripts/taxonomy/list_service_categories.py --sector wellness
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client, parse_identifier, resolve_sector


async def list_service_categories(show_all: bool, sector_identifier: str | None) -> None:
    prisma = await create_client()

    try:
        where = None if show_all else {"isActive": True}
        if sector_identifier:
            sector = await resolve_sector(prisma, parse_identifier(sector_identifier))
            if not sector:
                print(f"Hata: sektor bulunamadi ({sector_identifier}).")
                return
            where = {**(where or {}), "sectorId": sector.id}

        categories = await prisma.servicecategory.find_many(
            where=where,
            include={
                "sector": True,
                "auctions": True,
            },
        )

        if not categories:
            print("Kayitli hizmet kategorisi bulunamadi.")
            return

        print("\n=== HIZMET KATEGORILERI ===")
        for category in sorted(categories, key=lambda item: (item.name.lower(), item.id)):
            print(f"ID: {category.id} | Ad: {category.name} | Slug: {category.slug}")
            print(f"  Aktif: {'Evet' if category.isActive else 'Hayir'}")
            print(f"  Sektor: {category.sector.name if category.sector else '-'}")
            print(f"  Bagli firsat: {len(category.auctions)}")
            if category.description:
                print(f"  Aciklama: {category.description}")
            print("-" * 40)
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Hizmet kategorilerini listeler.")
    parser.add_argument("--all", action="store_true", help="Pasif kayitlari da goster")
    parser.add_argument("--sector", help="Filtrelenecek sektor ID veya slug")
    args = parser.parse_args()
    asyncio.run(list_service_categories(show_all=args.all, sector_identifier=args.sector))


if __name__ == "__main__":
    main()