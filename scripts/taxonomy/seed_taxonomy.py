#!/usr/bin/env python3
"""
Varsayilan sektor ve hizmet kategorilerini idempotent sekilde olusturur.

Kullanim:
    python scripts/taxonomy/seed_taxonomy.py
    python scripts/taxonomy/seed_taxonomy.py --update-existing
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client
from scripts.taxonomy.seed_data import DEFAULT_SECTORS, DEFAULT_SERVICE_CATEGORIES


async def seed_taxonomy(update_existing: bool) -> None:
    prisma = await create_client()

    try:
        print("Varsayilan sektorler kontrol ediliyor...")
        sector_ids_by_slug = {}

        for sector_data in DEFAULT_SECTORS:
            existing = await prisma.sector.find_unique(where={"slug": sector_data["slug"]})
            if existing:
                sector_ids_by_slug[existing.slug] = existing.id
                if update_existing:
                    updated = await prisma.sector.update(
                        where={"id": existing.id},
                        data={
                            "name": sector_data["name"],
                            "description": sector_data["description"],
                            "isActive": True,
                        },
                    )
                    sector_ids_by_slug[updated.slug] = updated.id
                    print(f"Guncellendi: {updated.name} ({updated.slug})")
                else:
                    print(f"Mevcut: {existing.name} ({existing.slug})")
                continue

            created = await prisma.sector.create(
                data={
                    "name": sector_data["name"],
                    "slug": sector_data["slug"],
                    "description": sector_data["description"],
                    "isActive": True,
                }
            )
            sector_ids_by_slug[created.slug] = created.id
            print(f"Olusturuldu: {created.name} ({created.slug})")

        print("\nVarsayilan hizmet kategorileri kontrol ediliyor...")
        for category_data in DEFAULT_SERVICE_CATEGORIES:
            existing = await prisma.servicecategory.find_unique(where={"slug": category_data["slug"]})
            payload = {
                "name": category_data["name"],
                "description": category_data["description"],
                "isActive": True,
                "sectorId": sector_ids_by_slug.get(category_data["sector_slug"]),
            }

            if existing:
                if update_existing:
                    updated = await prisma.servicecategory.update(
                        where={"id": existing.id},
                        data=payload,
                    )
                    print(f"Guncellendi: {updated.name} ({updated.slug})")
                else:
                    print(f"Mevcut: {existing.name} ({existing.slug})")
                continue

            created = await prisma.servicecategory.create(
                data={
                    **payload,
                    "slug": category_data["slug"],
                }
            )
            print(f"Olusturuldu: {created.name} ({created.slug})")

        print("\nTaxonomy seed tamamlandi.")
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Varsayilan taxonomy verisini yukler.")
    parser.add_argument("--update-existing", action="store_true", help="Mevcut kayitlari da varsayilan metadata ile guncelle")
    args = parser.parse_args()
    asyncio.run(seed_taxonomy(update_existing=args.update_existing))


if __name__ == "__main__":
    main()