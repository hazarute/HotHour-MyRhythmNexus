#!/usr/bin/env python3
"""
Mevcut isletme ve firsat kayitlarini interaktif olarak taksonomiye esler.

Mod 1 (varsayilan): Sektoru olmayan isletmeleri listeler, her biri icin
  veritabanindaki sektorlerden sec ve ata.

Mod 2 (--studio <ad veya id>): Belirli bir isletmenin sektorunu ekler veya degistirir.
  --replace eklenirse mevcut sektorler temizlenerek yeniden atanir.

Mod 3 (--auto): Heuristic anahtar kelime esleme ile otomatik calisir.
  --apply eklenmezse dry-run modundadir.

Kullanim:
    python scripts/taxonomy/backfill_taxonomy.py
    python scripts/taxonomy/backfill_taxonomy.py --studio "Zen Studio"
    python scripts/taxonomy/backfill_taxonomy.py --studio 42
    python scripts/taxonomy/backfill_taxonomy.py --studio "Zen Studio" --replace
    python scripts/taxonomy/backfill_taxonomy.py --auto
    python scripts/taxonomy/backfill_taxonomy.py --auto --apply
    python scripts/taxonomy/backfill_taxonomy.py --auto --apply --force-categories
"""

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.taxonomy._common import create_client
from scripts.taxonomy.seed_data import AUCTION_CATEGORY_KEYWORDS, STUDIO_SECTOR_KEYWORDS


def match_sector_slugs(studio_name: str) -> list[str]:
    haystack = (studio_name or "").lower()
    matches = []
    for sector_slug, keywords in STUDIO_SECTOR_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            matches.append(sector_slug)
    return matches


def match_category_slug(title: str, description: str | None) -> str | None:
    haystack = f"{title or ''} {description or ''}".lower()
    for category_slug, keywords in AUCTION_CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category_slug
    return None


def prompt_sector_selection(studio_name: str, sectors: list) -> list:
    """Kullaniciya sektör listesi gosterir, secimini alir. Birden fazla secim virgülle girilebilir."""
    print(f"\n  Isletme : {studio_name}")
    print("  Mevcut sektorler:")
    for i, s in enumerate(sectors, 1):
        print(f"    [{i}] {s.name}  ({s.slug})")
    print("    [0] Atla (bu isletmeyi gec)")

    while True:
        raw = input("  Seciminiz (ornek: 1  veya  1,3): ").strip()
        if raw == "0" or raw == "":
            return []
        parts = [p.strip() for p in raw.split(",")]
        selected = []
        valid = True
        for p in parts:
            if not p.isdigit() or not (1 <= int(p) <= len(sectors)):
                print(f"  Gecersiz giris: '{p}'. Lutfen 0-{len(sectors)} arasinda sayi girin.")
                valid = False
                break
            selected.append(sectors[int(p) - 1])
        if valid:
            return selected


async def assign_studio(studio_identifier: str, replace: bool, prisma) -> None:
    """Belirli bir isletmenin sektorlerini interaktif olarak ekler veya degistirir."""
    # ID mi isim mi?
    studio = None
    if studio_identifier.isdigit():
        studio = await prisma.studio.find_unique(
            where={"id": int(studio_identifier)},
            include={"sectors": True},
        )
    else:
        # Ada gore ara (buyuk/kucuk harf duyarsiz tam esleme yok, find_first ile)
        all_studios = await prisma.studio.find_many(include={"sectors": True})
        for s in all_studios:
            if s.name.lower() == studio_identifier.lower():
                studio = s
                break
        if not studio:
            # Kısmi eşleme dene
            matches = [s for s in all_studios if studio_identifier.lower() in s.name.lower()]
            if len(matches) == 1:
                studio = matches[0]
            elif len(matches) > 1:
                print(f"\n'{studio_identifier}' icin birden fazla isletme bulundu:")
                for i, s in enumerate(matches, 1):
                    print(f"  [{i}] {s.name}  (id={s.id})")
                while True:
                    raw = input("Hangisini kastettigini sec (numara): ").strip()
                    if raw.isdigit() and 1 <= int(raw) <= len(matches):
                        studio = matches[int(raw) - 1]
                        break
                    print("  Gecersiz giris.")

    if not studio:
        print(f"Hata: '{studio_identifier}' ile eslesen isletme bulunamadi.")
        return

    sectors = await prisma.sector.find_many(where={"isActive": True}, order={"name": "asc"})
    if not sectors:
        print("Hata: Veritabaninda aktif sektor bulunamadi. Once seed_taxonomy.py calistirin.")
        return

    # Mevcut durum
    current_sector_ids = {ss.id for ss in (studio.sectors or [])}
    current_names = ", ".join(ss.name for ss in (studio.sectors or [])) or "(yok)"
    print(f"\n  Isletme  : {studio.name}  (id={studio.id})")
    print(f"  Mevcut   : {current_names}")
    if replace:
        print("  Mod      : DEGISTIR (mevcut sektorler silinecek, secilen atanacak)")
    else:
        print("  Mod      : EKLE (mevcut sektorlere ek olarak secilenler atanacak)")

    chosen = prompt_sector_selection(studio.name, sectors)
    if not chosen:
        print("  -> Iptal edildi.")
        return

    if replace:
        # Mevcut tum sektör baglarini sil
        await prisma.studiosector.delete_many(where={"studioId": studio.id})
        print(f"  -> Onceki sektorler temizlendi.")
        for sector in chosen:
            await prisma.studiosector.create(
                data={"studioId": studio.id, "sectorId": sector.id}
            )
    else:
        # Sadece yeni olanları ekle (zaten varsa atla)
        added = []
        for sector in chosen:
            if sector.id in current_sector_ids:
                print(f"  -> Zaten mevcut, atildi: {sector.name}")
                continue
            await prisma.studiosector.create(
                data={"studioId": studio.id, "sectorId": sector.id}
            )
            added.append(sector.name)
        if not added:
            print("  -> Yeni atama yapilmadi (hepsi zaten mevcuttu).")
            return

    names = ", ".join(s.name for s in chosen)
    action = "Guncellendi" if replace else "Eklendi"
    print(f"  -> {action}: {names}")


async def backfill_interactive(prisma) -> None:
    """Sektoru olmayan isletmeleri interaktif olarak esler."""
    sectors = await prisma.sector.find_many(where={"isActive": True}, order={"name": "asc"})
    if not sectors:
        print("Hata: Veritabaninda aktif sektor bulunamadi. Once seed_taxonomy.py calistirin.")
        return

    studios = await prisma.studio.find_many(include={"sectors": True}, order={"name": "asc"})
    unassigned = [s for s in studios if not s.sectors]

    if not unassigned:
        print("Tum isletmelerin zaten en az bir sektoru mevcut. Yapilacak bir sey yok.")
        return

    print(f"\n{len(unassigned)} isletmenin sektoru yok.\n")
    assigned_count = 0

    for studio in unassigned:
        chosen = prompt_sector_selection(studio.name, sectors)
        if not chosen:
            print("  -> Atildi.")
            continue

        for sector in chosen:
            await prisma.studiosector.create(
                data={"studioId": studio.id, "sectorId": sector.id}
            )
        names = ", ".join(s.name for s in chosen)
        print(f"  -> Atandi: {names}")
        assigned_count += 1

    print(f"\nTamamlandi: {assigned_count} isletmeye sektor atamasi yapildi.")


async def backfill_auto(apply_changes: bool, force_categories: bool, prisma) -> None:
    """Heuristic anahtar kelime esleme ile otomatik backfill."""
    sectors = await prisma.sector.find_many(where={"isActive": True})
    categories = await prisma.servicecategory.find_many(where={"isActive": True})

    sector_ids_by_slug = {item.slug: item.id for item in sectors}
    category_ids_by_slug = {item.slug: item.id for item in categories}

    if not sector_ids_by_slug or not category_ids_by_slug:
        print("Hata: backfill oncesi python scripts/taxonomy/seed_taxonomy.py calistirin.")
        return

    studios = await prisma.studio.find_many(include={"sectors": True})
    auctions = await prisma.auction.find_many(include={"serviceCategory": True, "studio": True})

    print("\n=== STUDIO -> SECTOR BACKFILL ===")
    studio_updates = 0
    for studio in studios:
        if studio.sectors:
            print(f"Atlandi: {studio.name} zaten {len(studio.sectors)} sektor ile bagli")
            continue

        matched_sector_slugs = match_sector_slugs(studio.name)
        if not matched_sector_slugs:
            print(f"Eslesme yok: {studio.name}")
            continue

        print(f"Plan: {studio.name} -> {', '.join(matched_sector_slugs)}")
        studio_updates += 1

        if not apply_changes:
            continue

        for sector_slug in matched_sector_slugs:
            sector_id = sector_ids_by_slug.get(sector_slug)
            if not sector_id:
                continue
            await prisma.studiosector.create(
                data={"studioId": studio.id, "sectorId": sector_id}
            )

    print("\n=== AUCTION -> SERVICE CATEGORY BACKFILL ===")
    auction_updates = 0
    for auction in auctions:
        if auction.serviceCategory and not force_categories:
            print(f"Atlandi: {auction.title} zaten kategoriye sahip")
            continue

        matched_category_slug = match_category_slug(auction.title, auction.description)
        if not matched_category_slug:
            print(f"Eslesme yok: {auction.title}")
            continue

        category_id = category_ids_by_slug.get(matched_category_slug)
        if not category_id:
            print(f"Kategori bulunamadi: {matched_category_slug} ({auction.title})")
            continue

        print(f"Plan: {auction.title} -> {matched_category_slug}")
        auction_updates += 1

        if not apply_changes:
            continue

        await prisma.auction.update(
            where={"id": auction.id},
            data={"serviceCategoryId": category_id},
        )

    print("\n=== OZET ===")
    print(f"Studio esleme adayi: {studio_updates}")
    print(f"Firsat kategori adayi: {auction_updates}")
    print("Mod: Uygulandi" if apply_changes else "Mod: Dry run (--apply ekleyin)")


async def run(args) -> None:
    prisma = await create_client()
    try:
        if args.studio:
            await assign_studio(
                studio_identifier=args.studio,
                replace=args.replace,
                prisma=prisma,
            )
        elif args.auto:
            await backfill_auto(
                apply_changes=args.apply,
                force_categories=args.force_categories,
                prisma=prisma,
            )
        else:
            await backfill_interactive(prisma)
    finally:
        await prisma.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Isletme sektor atamasi. Varsayilan: sektoru olmayan isletmeleri interaktif esler. "
            "--studio ile tek isletme hedeflenebilir, --auto ile heuristic otomatik mod aktif olur."
        )
    )
    parser.add_argument(
        "--studio",
        metavar="AD_VEYA_ID",
        help="Hedef isletmenin adi (veya id'si). Tek isletme icin sektor ekle/degistir.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="(--studio ile) Mevcut sektorleri temizle ve secileni ata (degistir modu).",
    )
    parser.add_argument("--auto", action="store_true", help="Heuristic anahtar kelime esleme ile otomatik calistir")
    parser.add_argument("--apply", action="store_true", help="(--auto ile) Dry run yerine degisiklikleri uygula")
    parser.add_argument("--force-categories", action="store_true", help="(--auto ile) Mevcut kategorisi olan firsatlari da yeniden esle")
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()