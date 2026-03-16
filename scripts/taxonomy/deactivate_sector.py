#!/usr/bin/env python3
"""
Sektor pasiflestirme scripti
Kullanim:
    python scripts/taxonomy/deactivate_sector.py 3
    python scripts/taxonomy/deactivate_sector.py wellness
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client, parse_identifier, resolve_sector


async def deactivate_sector(identifier_value: str) -> None:
    prisma = await create_client()

    try:
        identifier = parse_identifier(identifier_value)
        sector = await resolve_sector(prisma, identifier)
        if not sector:
            print(f"Hata: sektor bulunamadi ({identifier_value}).")
            return

        if not sector.isActive:
            print(f"Sektor zaten pasif: {sector.name} ({sector.slug})")
            return

        updated = await prisma.sector.update(
            where={"id": sector.id},
            data={"isActive": False},
        )

        print("Sektor pasiflestirildi.")
        print(f"  ID: {updated.id}")
        print(f"  Ad: {updated.name}")
        print(f"  Slug: {updated.slug}")
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sektoru pasiflestirir.")
    parser.add_argument("identifier", help="Sektor ID veya slug")
    args = parser.parse_args()
    asyncio.run(deactivate_sector(args.identifier))


if __name__ == "__main__":
    main()