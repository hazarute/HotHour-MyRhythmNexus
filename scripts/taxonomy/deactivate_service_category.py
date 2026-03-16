#!/usr/bin/env python3
"""
Hizmet kategorisi pasiflestirme scripti
Kullanim:
    python scripts/taxonomy/deactivate_service_category.py 5
    python scripts/taxonomy/deactivate_service_category.py aletli-pilates
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client, parse_identifier


async def deactivate_service_category(identifier_value: str) -> None:
    prisma = await create_client()

    try:
        identifier = parse_identifier(identifier_value)
        if isinstance(identifier, int):
            category = await prisma.servicecategory.find_unique(where={"id": identifier})
        else:
            category = await prisma.servicecategory.find_unique(where={"slug": str(identifier)})

        if not category:
            print(f"Hata: hizmet kategorisi bulunamadi ({identifier_value}).")
            return

        if not category.isActive:
            print(f"Hizmet kategorisi zaten pasif: {category.name} ({category.slug})")
            return

        updated = await prisma.servicecategory.update(
            where={"id": category.id},
            data={"isActive": False},
        )

        print("Hizmet kategorisi pasiflestirildi.")
        print(f"  ID: {updated.id}")
        print(f"  Ad: {updated.name}")
        print(f"  Slug: {updated.slug}")
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Hizmet kategorisini pasiflestirir.")
    parser.add_argument("identifier", help="Kategori ID veya slug")
    args = parser.parse_args()
    asyncio.run(deactivate_service_category(args.identifier))


if __name__ == "__main__":
    main()