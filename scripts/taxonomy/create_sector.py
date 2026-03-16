#!/usr/bin/env python3
"""
Sektor olusturma scripti
Kullanim:
    python scripts/taxonomy/create_sector.py "Wellness" --description "Saglik ve iyi yasam"
    python scripts/taxonomy/create_sector.py "Pilates ve Yoga" --slug pilates-yoga --inactive
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client, slugify


async def create_sector(name: str, slug: str | None, description: str | None, is_active: bool) -> None:
    prisma = await create_client()

    try:
        final_slug = slugify(slug or name)
        if not final_slug:
            raise ValueError("Slug bos olamaz")

        existing_by_slug = await prisma.sector.find_unique(where={"slug": final_slug})
        if existing_by_slug:
            print(f"Hata: '{final_slug}' slug'i zaten kullaniliyor.")
            return

        sector = await prisma.sector.create(
            data={
                "name": name.strip(),
                "slug": final_slug,
                "description": description.strip() if description else None,
                "isActive": is_active,
            }
        )

        print("Sektor olusturuldu.")
        print(f"  ID: {sector.id}")
        print(f"  Ad: {sector.name}")
        print(f"  Slug: {sector.slug}")
        print(f"  Aktif: {sector.isActive}")
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Yeni sektor olusturur.")
    parser.add_argument("name", help="Sektor adi")
    parser.add_argument("--slug", help="Opsiyonel manuel slug")
    parser.add_argument("--description", help="Opsiyonel aciklama")
    parser.add_argument("--inactive", action="store_true", help="Sektoru pasif olustur")
    args = parser.parse_args()

    asyncio.run(
        create_sector(
            name=args.name,
            slug=args.slug,
            description=args.description,
            is_active=not args.inactive,
        )
    )


if __name__ == "__main__":
    main()