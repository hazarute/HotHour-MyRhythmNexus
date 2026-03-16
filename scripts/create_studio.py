#!/usr/bin/env python3
"""
Studio Oluşturma Scripti
Kullanım:
  python scripts/create_studio.py "Studio Adı" ["Adres"] ["Logo URL"] ["Google Maps URL"]
  python scripts/create_studio.py "Studio Adı" --sector wellness --sector fitness
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from scripts.taxonomy._common import create_client, parse_identifier, resolve_sector

load_dotenv()


async def _resolve_sectors(prisma, sector_values: list[str]):
    resolved = []
    seen_ids = set()

    for raw_value in sector_values:
        identifier = parse_identifier(raw_value)
        sector = await resolve_sector(prisma, identifier)
        if not sector:
            raise ValueError(f"Sektör bulunamadı: {raw_value}")

        if not getattr(sector, "isActive", True):
            raise ValueError(f"Pasif sektör kullanılamaz: {getattr(sector, 'name', raw_value)}")

        if sector.id in seen_ids:
            continue

        seen_ids.add(sector.id)
        resolved.append(sector)

    return resolved


async def create_studio(
    name: str,
    address: Optional[str] = None,
    logoUrl: Optional[str] = None,
    googleMapsUrl: Optional[str] = None,
    sector_values: list[str] | None = None,
):
    prisma = await create_client()

    try:
        sectors = await _resolve_sectors(prisma, sector_values or [])

        new_studio = await prisma.studio.create(
            data={
                "name": name,
                "address": address,
                "logoUrl": logoUrl,
                "googleMapsUrl": googleMapsUrl
            }
        )

        for sector in sectors:
            await prisma.studiosector.create(
                data={
                    "studioId": new_studio.id,
                    "sectorId": sector.id,
                }
            )

        print("✅ Studio başarıyla oluşturuldu!")
        print(f"   ID: {new_studio.id}")
        print(f"   İsim: {new_studio.name}")
        print(f"   Adres: {new_studio.address}")
        if sectors:
            print(f"   Sektörler: {', '.join(sector.name for sector in sectors)}")
        else:
            print("   Sektörler: -")
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        raise
    finally:
        await prisma.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Yeni işletme (studio) oluşturur.")
    parser.add_argument("name", help="İşletme adı")
    parser.add_argument("address", nargs="?", default=None, help="Opsiyonel adres")
    parser.add_argument("logo_url", nargs="?", default=None, help="Opsiyonel logo URL")
    parser.add_argument("google_maps_url", nargs="?", default=None, help="Opsiyonel Google Maps URL")
    parser.add_argument(
        "--sector",
        dest="sectors",
        action="append",
        default=[],
        help="Bağlanacak aktif sektör ID veya slug değeri. Birden fazla kez kullanılabilir.",
    )

    args = parser.parse_args()

    asyncio.run(
        create_studio(
            name=args.name,
            address=args.address,
            logoUrl=args.logo_url,
            googleMapsUrl=args.google_maps_url,
            sector_values=args.sectors,
        )
    )

if __name__ == "__main__":
    main()