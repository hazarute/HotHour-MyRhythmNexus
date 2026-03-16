#!/usr/bin/env python3
"""
Hizmet kategorisi olusturma scripti
Kullanim:
    python scripts/taxonomy/create_service_category.py "Aletli Pilates" --sector wellness
    python scripts/taxonomy/create_service_category.py "Acik Grup Dersi" --sector 2 --slug acik-grup
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client, parse_identifier, resolve_sector, slugify


async def create_service_category(
    name: str,
    slug: str | None,
    description: str | None,
    sector_identifier: str | None,
    is_active: bool,
) -> None:
    prisma = await create_client()

    try:
        base_slug = slugify(slug or name)
        if not base_slug:
            raise ValueError("Slug bos olamaz")

        sector_id = None
        sector = None
        if sector_identifier:
            sector = await resolve_sector(prisma, parse_identifier(sector_identifier))
            if not sector:
                print(f"Hata: sektor bulunamadi ({sector_identifier}).")
                return
            sector_id = sector.id

        final_slug = base_slug

        existing = await prisma.servicecategory.find_unique(where={"slug": final_slug})
        if existing:
            # Eğer kullanıcı manuel --slug vermediyse, fallback: name + sector
            if slug:
                print(f"Hata: '{final_slug}' slug'i zaten kullaniliyor.")
                return

            # Deneme 1: name + sector.slug (eğer sector mevcutsa)
            if sector and getattr(sector, "slug", None):
                fallback = slugify(f"{name.strip()}-{sector.slug}")
            else:
                # Eğer sector belirtilmiş ama bulunamadıysa zaten return edilmişti;
                # burada sector yoksa sektore bağlı identifier ile dene
                fallback = slugify(f"{name.strip()}-{sector_identifier}")

            if fallback and not await prisma.servicecategory.find_unique(where={"slug": fallback}):
                final_slug = fallback
            else:
                print(f"Hata: '{final_slug}' slug'i zaten kullaniliyor ve fallback slug da uygun degil.")
                return

        category = await prisma.servicecategory.create(
            data={
                "name": name.strip(),
                "slug": final_slug,
                "description": description.strip() if description else None,
                "isActive": is_active,
                "sectorId": sector_id,
            }
        )

        print("Hizmet kategorisi olusturuldu.")
        print(f"  ID: {category.id}")
        print(f"  Ad: {category.name}")
        print(f"  Slug: {category.slug}")
        print(f"  Aktif: {category.isActive}")
        print(f"  Sektor: {sector.name if sector else '-'}")
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Yeni hizmet kategorisi olusturur.")
    parser.add_argument("name", help="Kategori adi")
    parser.add_argument("--slug", help="Opsiyonel manuel slug")
    parser.add_argument("--description", help="Opsiyonel aciklama")
    parser.add_argument("--sector", help="Baglanacak sektorun ID veya slug degeri")
    parser.add_argument("--inactive", action="store_true", help="Kategoriyi pasif olustur")
    args = parser.parse_args()

    asyncio.run(
        create_service_category(
            name=args.name,
            slug=args.slug,
            description=args.description,
            sector_identifier=args.sector,
            is_active=not args.inactive,
        )
    )


if __name__ == "__main__":
    main()