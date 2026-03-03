import sys
import os
import asyncio
import argparse

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db
from app.core.redis_client import get_redis_client
from app.core.config import settings
from app.core import token_revocation


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


async def clear_sessions_and_reservations():
    print("Veritabanına bağlanılıyor...")
    await db.connect()

    try:
        confirm = input("\n⚠️  UYARI: Sadece oturumlar ve rezervasyonlar temizlenecek. Devam? (evet/hayir): ").strip().lower()
        if confirm != "evet":
            print("İşlem iptal edildi.")
            return

        print("\nTemizlik başlıyor (oturumlar + rezervasyonlar)...")

        deleted_reservations = await _delete_all("reservation")
        print(f"✅ {deleted_reservations} rezervasyon silindi.")

        # Clear revoked refresh tokens from Redis if configured, otherwise clear in-memory set
        redis_client = get_redis_client()
        deleted_redis = 0
        if redis_client:
            try:
                pattern = f"{settings.REDIS_REVOKED_KEY_PREFIX}*"
                for key in redis_client.scan_iter(match=pattern):
                    try:
                        redis_client.delete(key)
                        deleted_redis += 1
                    except Exception:
                        pass
                print(f"✅ {deleted_redis} oturum anahtarı (Redis) silindi.")
            except Exception:
                try:
                    keys = redis_client.keys(f"{settings.REDIS_REVOKED_KEY_PREFIX}*") or []
                    for k in keys:
                        try:
                            redis_client.delete(k)
                            deleted_redis += 1
                        except Exception:
                            pass
                    print(f"✅ {deleted_redis} oturum anahtarı (Redis) silindi.")
                except Exception:
                    print("⚠️ Redis ile bağlantı kurulamadı, oturum anahtarları silinemedi.")
        else:
            try:
                token_revocation._revoked_tokens.clear()
                print("✅ In-memory oturum revocation set temizlendi.")
            except Exception:
                print("⚠️ In-memory oturum seti temizlenemedi.")

        print("\n✨ Seçili veriler temizlendi.")
    finally:
        await db.disconnect()


def _build_parser():
    p = argparse.ArgumentParser(description="Veritabanı temizleme aracı")
    p.add_argument("--sessions-only", action="store_true", help="Sadece oturumlar (revoked tokens) ve rezervasyonları temizle")
    return p


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    if args.sessions_only:
        asyncio.run(clear_sessions_and_reservations())
    else:
        asyncio.run(clear_database())
