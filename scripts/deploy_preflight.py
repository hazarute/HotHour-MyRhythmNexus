#!/usr/bin/env python3
"""
Pre-deploy ve pre-migration kontrolleri.

Amaç:
- Production DB'ye migration ve backfill uygulanmadan önce hızlı güvenlik kontrolleri yapmak.
- Tablo/indeks varlıklarını, kritik kayıt sayılarını ve backfill dry-run özetini göstermek.
- Opsiyonel: `--apply-backfill` ve `--yes` ile backfill'i doğrudan çalıştırabilir (commit sonrası dikkat).

Kullanım:
    python scripts/deploy_preflight.py
    python scripts/deploy_preflight.py --dry-run-backfill
    python scripts/deploy_preflight.py --apply-backfill --yes

NOT: Bu script migration'ları çalıştırmaz; yalnızca mevcut şema ve veritabanı durumunu denetler.
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client
from scripts.taxonomy.backfill_taxonomy import backfill_taxonomy


async def run_checks():
    prisma = await create_client()
    try:
        print("\n== Bağlantı testi ve tablo kontrolleri ==")

        # Tabloların varlığını model bazlı denetle
        models = [
            ("sectors", "sector"),
            ("service_categories", "servicecategory"),
            ("studio_sectors", "studiosector"),
            ("studios", "studio"),
            ("auctions", "auction"),
        ]

        model_availability = {}
        for table_name, model_name in models:
            try:
                # Her model için find_first benzeri sorgu deneyelim
                fn = getattr(prisma, model_name)
                # Kullanılabilir: find_many ile 1 eleman dene
                _ = await fn.find_many(take=1)
                model_availability[table_name] = True
            except Exception:
                model_availability[table_name] = False

        for table, ok in model_availability.items():
            print(f"Tablo: {table:20} -> {'OK' if ok else 'YOK'}")

        # Eğer temel taxonomy tabloları yoksa uyar
        if not model_availability.get("sectors") or not model_availability.get("service_categories"):
            print("\nUYARI: Taxonomy tabloları bulunmuyor. Migration uygulanmamış olabilir.")

        print("\n== Veri özetleri ==")
        # Studio sayısı
        studio_count = 0
        try:
            studio_count = await prisma.studio.count()
        except Exception:
            # fallback
            studios = await prisma.studio.find_many(take=1)
            studio_count = None if studios is None else 'unknown'

        print(f"Studyo sayisi: {studio_count}")

        # Sektör sayısı
        sector_count = None
        if model_availability.get("sectors"):
            try:
                sector_count = await prisma.sector.count()
            except Exception:
                sector_count = 'unknown'
        print(f"Sector sayisi: {sector_count}")

        # Service category sayısı
        cat_count = None
        if model_availability.get("service_categories"):
            try:
                cat_count = await prisma.servicecategory.count()
            except Exception:
                cat_count = 'unknown'
        print(f"ServiceCategory sayisi: {cat_count}")

        # Studio'larin sektoru yoksa count
        if model_availability.get("studios") and model_availability.get("studio_sectors"):
            studios = await prisma.studio.find_many(include={"sectors": True})
            studios_without = [s for s in studios if not s.sectors]
            print(f"Studio'larin sektorsuz sayisi: {len(studios_without)}")
            if len(studios_without) > 0:
                print("Kisa ornek (10):")
                for s in studios_without[:10]:
                    print(f" - {s.id}: {s.name}")

        # Auctions without category
        if model_availability.get("auctions") and model_availability.get("service_categories"):
            auctions_without = await prisma.auction.find_many(where={"serviceCategoryId": None}, take=20)
            # total count query
            try:
                total_null = await prisma.auction.count(where={"serviceCategoryId": None})
            except Exception:
                total_null = len(auctions_without)
            print(f"ServiceCategory bagli olmayan auctions sayisi: {total_null}")
            if auctions_without:
                print("Kisa ornek (20):")
                for a in auctions_without:
                    print(f" - {a.id}: {a.title} (studio_id={a.studioId})")

        print("\n== Backfill dry-run önerisi ==")
        print("Backfill script'i (dry-run) çalıştırarak hangi değişikliklerin planlandığını görebilirsiniz:")
        print("  python scripts/taxonomy/backfill_taxonomy.py --dry-run")

    finally:
        await prisma.disconnect()


async def main(apply_backfill: bool, yes: bool):
    await run_checks()

    if apply_backfill:
        if not yes:
            confirm = input("Backfill'i uygulamak istiyor musunuz? (evet/hayir): ")
            if confirm.strip().lower() not in ("evet", "e", "yes", "y"):
                print("Backfill iptal edildi.")
                return

        print("Backfill (apply) başlatılıyor...")
        # call backfill_taxonomy with apply=True
        await backfill_taxonomy(apply_changes=True, force_categories=False)
        print("Backfill tamamlandi.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-deploy DB kontrolleri ve opsiyonel backfill.")
    parser.add_argument("--dry-run-backfill", action="store_true", help="Backfill'i dry-run modunda calistir (ayni asama backfill script ile ayni) -- alias")
    parser.add_argument("--apply-backfill", action="store_true", help="Backfill'i DB'ye uygula (apply)")
    parser.add_argument("--yes", action="store_true", help="Onay sorusunu atla (dangerous)")
    args = parser.parse_args()

    # Eğer --dry-run-backfill verilmişse sadece bilgilendirme, zaten run_checks'te öneriliyor
    if args.dry_run_backfill:
        print("Dry-run backfill'i çalıştırılıyor (backfill script ile aynı sonuç):")
        asyncio.run(backfill_taxonomy(apply_changes=False, force_categories=False))
    else:
        asyncio.run(main(apply_backfill=args.apply_backfill, yes=args.yes))
