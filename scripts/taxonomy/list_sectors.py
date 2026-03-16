#!/usr/bin/env python3
"""
Sektor listeleme scripti
Kullanim:
    python scripts/taxonomy/list_sectors.py
    python scripts/taxonomy/list_sectors.py --all
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client


async def list_sectors(show_all: bool) -> None:
    prisma = await create_client()

    try:
        sectors = await prisma.sector.find_many(
            where=None if show_all else {"isActive": True},
            include={
                "studios": True,
                "serviceCategories": True,
            },
        )

        if not sectors:
            print("Kayitli sektor bulunamadi.")
            return

        print("\n=== SEKTORLER ===")
        for sector in sorted(sectors, key=lambda item: (item.name.lower(), item.id)):
            print(f"ID: {sector.id} | Ad: {sector.name} | Slug: {sector.slug}")
            print(f"  Aktif: {'Evet' if sector.isActive else 'Hayir'}")
            print(f"  Isletme baglantisi: {len(sector.studios)}")
            print(f"  Hizmet kategorisi: {len(sector.serviceCategories)}")
            if sector.description:
                print(f"  Aciklama: {sector.description}")
            print("-" * 40)
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sektorleri listeler.")
    parser.add_argument("--all", action="store_true", help="Pasif kayitlari da goster")
    args = parser.parse_args()
    asyncio.run(list_sectors(show_all=args.all))


if __name__ == "__main__":
    main()