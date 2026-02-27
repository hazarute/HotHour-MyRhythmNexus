import sys
import os
import asyncio

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db


def _deleted_count(result) -> int:
    if isinstance(result, int):
        return result
    return int(getattr(result, "count", 0) or 0)


async def _delete_all(model_name: str) -> int:
    model = getattr(db, model_name, None)
    if model is None or not hasattr(model, "delete_many"):
        return 0
    result = await model.delete_many(where={})
    return _deleted_count(result)

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

    try:
        print("\nTemizlik başlıyor...")

        # 1. Önce bağımlı tabloları sil (Foreign Key kısıtlamaları yüzünden)
        deleted_reservations = await _delete_all("reservation")
        print(f"✅ {deleted_reservations} rezervasyon silindi.")

        deleted_notifications = await _delete_all("notification")
        print(f"✅ {deleted_notifications} bildirim silindi.")

        # 2. Ana tabloları sil
        deleted_auctions = await _delete_all("auction")
        print(f"✅ {deleted_auctions} açık artırma silindi.")

        deleted_users = await _delete_all("user")
        print(f"✅ {deleted_users} kullanıcı silindi.")

        print("\n✨ Veritabanı başarıyla temizlendi.")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(clear_database())
