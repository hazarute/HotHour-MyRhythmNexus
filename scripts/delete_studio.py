#!/usr/bin/env python3
"""
Studio Silme Scripti
Kullanim:
    python scripts/delete_studio.py <ID>
    python scripts/delete_studio.py <ID> --force-detach
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, cast

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()


def _affected_count(result) -> int:
    if isinstance(result, int):
        return result
    return int(getattr(result, "count", 0) or 0)


async def delete_studio(studio_id: int, force_detach: bool = False):
    prisma = Prisma()
    await prisma.connect()

    try:
        studio = await prisma.studio.find_unique(
            where={"id": studio_id},
            include={
                "users": True,
                "auctions": True,
                "sectors": {
                    "include": {
                        "sector": True,
                    }
                },
            },
        )

        if not studio:
            print(f"❌ Hata: {studio_id} ID'li studio bulunamadı.")
            return

        users = studio.users or []
        auctions = studio.auctions or []
        sector_links = studio.sectors or []

        user_count = len(users)
        auction_count = len(auctions)
        sector_link_count = len(sector_links)

        print(f"📦 Studio bulundu: {studio.name} (ID: {studio.id})")
        print(f"   - Bağlı kullanıcı: {user_count}")
        print(f"   - Bağlı açık artırma: {auction_count}")
        print(f"   - Bağlı sektör eşleşmesi: {sector_link_count}")

        has_blocking_relations = user_count > 0 or auction_count > 0
        if has_blocking_relations and not force_detach:
            print("\n⚠️ Bu studioya hala kullanıcı ve/veya açık artırma bağlı.")
            print("Varsayılan güvenli mod silmeyi durdurur.")
            print("Önce kayıtları başka bir işletmeye taşıyın veya --force-detach ile studio bağlarını null yaparak silin.")
            return

        if force_detach and has_blocking_relations:
            confirm = input(
                "\nBu işlem bağlı kullanıcı ve açık artırmaların studioId alanını boşaltacak, ardından studio silinecek. Devam? (evet/hayir): "
            ).strip().lower()
            if confirm != "evet":
                print("İşlem iptal edildi.")
                return

            if auction_count > 0:
                updated_auctions = await prisma.auction.update_many(
                    where={"studioId": studio_id},
                    data=cast(Any, {"studioId": None}),
                )
                print(f"✅ {_affected_count(updated_auctions)} açık artırmanın studio bağı kaldırıldı.")

            if user_count > 0:
                updated_users = await prisma.user.update_many(
                    where={"studioId": studio_id},
                    data=cast(Any, {"studioId": None}),
                )
                print(f"✅ {_affected_count(updated_users)} kullanıcının studio bağı kaldırıldı.")

        if sector_link_count > 0:
            deleted_sector_links = await prisma.studiosector.delete_many(where={"studioId": studio_id})
            print(f"✅ {_affected_count(deleted_sector_links)} sektör eşleşmesi silindi.")

        await prisma.studio.delete(where={"id": studio_id})
        print(f"✅ Studio (ID: {studio_id}, İsim: {studio.name}) başarıyla silindi.")

    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
        raise
    finally:
        await prisma.disconnect()


def build_parser():
    parser = argparse.ArgumentParser(description="Studio silme aracı")
    parser.add_argument("studio_id", type=int, help="Silinecek studio ID")
    parser.add_argument(
        "--force-detach",
        action="store_true",
        help="Bağlı kullanıcı ve açık artırmaların studioId alanını null yapıp studioyu sil",
    )
    return parser


def main():
    args = build_parser().parse_args()
    asyncio.run(delete_studio(args.studio_id, force_detach=args.force_detach))


if __name__ == "__main__":
    main()