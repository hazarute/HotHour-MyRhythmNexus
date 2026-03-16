#!/usr/bin/env python3
"""
seed_taxonomy.py tarafindan olusturulan varsayilan sektor ve hizmet
kategorilerini veritabanindan siler.

Kullanim:
    python scripts/taxonomy/delete_taxonomy.py
    python scripts/taxonomy/delete_taxonomy.py --dry-run
    python scripts/taxonomy/delete_taxonomy.py --force
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

SECTOR_SLUGS = [s["slug"] for s in DEFAULT_SECTORS]
CATEGORY_SLUGS = [c["slug"] for c in DEFAULT_SERVICE_CATEGORIES]


async def delete_taxonomy(dry_run: bool, force: bool) -> None:
    prisma = await create_client()

    try:
        # --- Hizmet kategorileri ---
        print("Silinecek hizmet kategorileri kontrol ediliyor...")
        categories_to_delete = []
        for slug in CATEGORY_SLUGS:
            record = await prisma.servicecategory.find_unique(where={"slug": slug})
            if record:
                categories_to_delete.append(record)
                print(f"  Bulundu: {record.name} ({record.slug})")
            else:
                print(f"  Bulunamadi (zaten yok): {slug}")

        # --- Sektorler ---
        print("\nSilinecek sektorler kontrol ediliyor...")
        sectors_to_delete = []
        for slug in SECTOR_SLUGS:
            record = await prisma.sector.find_unique(where={"slug": slug})
            if record:
                sectors_to_delete.append(record)
                print(f"  Bulundu: {record.name} ({record.slug})")
            else:
                print(f"  Bulunamadi (zaten yok): {slug}")

        if not categories_to_delete and not sectors_to_delete:
            print("\nSilinecek kayit bulunamadi. Islem tamamlandi.")
            return

        print(
            f"\nToplamda {len(categories_to_delete)} hizmet kategorisi ve "
            f"{len(sectors_to_delete)} sektor silinecek."
        )

        if dry_run:
            print("\n[DRY-RUN] Gercek silme islemi yapilmadi.")
            return

        if not force:
            answer = input("\nDevam etmek istiyor musunuz? [e/H]: ").strip().lower()
            if answer not in ("e", "evet", "y", "yes"):
                print("Islem iptal edildi.")
                return

        # Once hizmet kategorilerini sil (FK kisiti nedeniyle once bunlar)
        deleted_categories = 0
        for record in categories_to_delete:
            await prisma.servicecategory.delete(where={"id": record.id})
            print(f"Silindi (kategori): {record.name} ({record.slug})")
            deleted_categories += 1

        # Sonra sektorleri sil
        deleted_sectors = 0
        for record in sectors_to_delete:
            try:
                await prisma.sector.delete(where={"id": record.id})
                print(f"Silindi (sektor): {record.name} ({record.slug})")
                deleted_sectors += 1
            except Exception as exc:
                print(
                    f"HATA: {record.name} ({record.slug}) silinemedi - "
                    "Bu sektore bagli baska kayitlar olabilir. Detay: {exc}"
                )

        print(
            f"\nTamamlandi: {deleted_categories} hizmet kategorisi, "
            f"{deleted_sectors} sektor silindi."
        )

    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="seed_taxonomy.py tarafindan olusturulan varsayilan taxonomy verisini siler."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Silme islemi yapmadan hangi kayitlarin silineceğini listeler.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Onay sormadan dogrudan siler.",
    )
    args = parser.parse_args()
    asyncio.run(delete_taxonomy(dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()
