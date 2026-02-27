import sys
import os
import asyncio

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db

async def clear_database():
    print("Veritabanına bağlanılıyor...")
    await db.connect()

    print("\n⚠️  UYARI: Bu işlem tüm veritabanını temizleyecektir!")
    print("   - Rezervasyonlar")
    print("   - Bildirimler")
    print("   - Açık Artırmalar")
    print("   - Kullanıcılar (Adminler dahil)")
    
    confirm = input("\nDevam etmek istiyor musunuz? (evet/hayir): ").strip().lower()
    
    if confirm != "evet":
        print("İşlem iptal edildi.")
        await db.disconnect()
        return

    print("\nTemizlik başlıyor...")

    # 1. Önce bağımlı tabloları sil (Foreign Key kısıtlamaları yüzünden)
    deleted_reservations = await db.reservation.delete_many(where={})
    print(f"✅ {deleted_reservations.count} rezervasyon silindi.")

    deleted_notifications = await db.notification.delete_many(where={})
    print(f"✅ {deleted_notifications.count} bildirim silindi.")

    # 2. Ana tabloları sil
    deleted_auctions = await db.auction.delete_many(where={})
    print(f"✅ {deleted_auctions.count} açık artırma silindi.")

    deleted_users = await db.user.delete_many(where={})
    print(f"✅ {deleted_users.count} kullanıcı silindi.")

    print("\n✨ Veritabanı başarıyla temizlendi.")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(clear_database())
