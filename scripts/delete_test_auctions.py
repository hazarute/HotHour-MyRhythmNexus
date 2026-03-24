#!/usr/bin/env python3
"""Test amaçlı "test" başlıklı fırsat kayıtlarını ve ilişkili bağımlı verileri siler.

Not: Bu script yalnızca Railway canlı veritabanı üzerinde manuel çalıştırılmalıdır.
"""

import os
import sys
import asyncio

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db

TEST_TITLES = ["test", "test2", "test3", "test4"]


def _deleted_count(result) -> int:
    # Prisma delete_many returns count-like object (or fake int in tests)
    if result is None:
        return 0
    if isinstance(result, int):
        return result
    return int(getattr(result, "count", 0) or 0)


async def delete_test_auctions():
    print("Veritabanına bağlanılıyor...")
    await db.connect()

    try:
        print("\nSilinecek test başlıkları:", TEST_TITLES)

        auctions = await db.auction.find_many(where={"title": {"in": TEST_TITLES}})

        if not auctions:
            print("Hiç test fırsatı bulunamadı. İşlem sonlandırıldı.")
            return

        auction_ids = [a.id for a in auctions]
        print(f"Bulunan auction ID'leri: {auction_ids}")

        confirm = input("\nBu kayıtları ve ilişkili verileri silmek istediğinizden emin misiniz? (evet/hayir): ").strip().lower()
        if confirm != "evet":
            print("İşlem iptal edildi.")
            return

        print("\nBildirimler siliniyor...")
        notifications_result = await db.notification.delete_many(where={"auctionId": {"in": auction_ids}})
        deleted_notifications = _deleted_count(notifications_result)

        print("Rezervasyonlar siliniyor...")
        reservations_result = await db.reservation.delete_many(where={"auctionId": {"in": auction_ids}})
        deleted_reservations = _deleted_count(reservations_result)

        print("Fırsatlar siliniyor...")
        auctions_result = await db.auction.delete_many(where={"id": {"in": auction_ids}})
        deleted_auctions = _deleted_count(auctions_result)

        print("\n✅ İşlem tamamlandı")
        print(f"  - {deleted_notifications} bildirim silindi")
        print(f"  - {deleted_reservations} rezervasyon silindi")
        print(f"  - {deleted_auctions} fırsat silindi")

    finally:
        await db.disconnect()
        print("Veritabanı bağlantısı kapatıldı.")


if __name__ == "__main__":
    asyncio.run(delete_test_auctions())
