#!/usr/bin/env python3
"""
Stüdyosu olmayan Admin hesaplarına stüdyo atamak için script.
Kullanım: python scripts/assign_studio_to_admins.py <studio_id>
"""

import sys
import os
import asyncio
from pathlib import Path

# Proje root dizinini sys.path'e ekle
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from prisma import Prisma

async def main():
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print("ℹ️  Kullanım:")
        print("   python scripts/assign_studio_to_admins.py <studio_id>")
        print()
        print("Örnek:")
        print("   python scripts/assign_studio_to_admins.py 3")
        print("Bu komut stüdyosu (studioId) null olan tüm ADMIN rollerindeki kullanıcılara 3 ID'li stüdyoyu atar.")
        sys.exit(1 if len(sys.argv) < 2 else 0)

    try:
        studio_id = int(sys.argv[1])
    except ValueError:
        print("❌ Hata: studio_id bir tam sayı olmalıdır.")
        sys.exit(1)

    db = Prisma()
    await db.connect()

    try:
        # Önce Stüdyonun var olup olmadığını kontrol et
        studio = await db.studio.find_unique(where={"id": studio_id})
        if not studio:
            print(f"❌ Hata: {studio_id} ID'li stüdyo bulunamadı.")
            
            # Varolan stüdyoları listele
            studios = await db.studio.find_many()
            if studios:
                print("\nMevcut Stüdyolar:")
                for s in studios:
                    print(f"  - ID: {s.id} | İsim: {s.name}")
            else:
                print("\nSistemde hiç stüdyo bulunmuyor.")
            sys.exit(1)
            
        print(f"✅ {studio.name} (ID: {studio.id}) bulundu.")

        # Stüdyosu olmayan adminleri bul
        orphaned_admins = await db.user.find_many(
            where={
                "role": "ADMIN",
                "studioId": None
            }
        )
        
        if not orphaned_admins:
            print("ℹ️  Güncellenecek stüdyosuz Admin hesabı bulunamadı.")
        else:
            print(f"🔄 {len(orphaned_admins)} adet Admin hesabı güncelleniyor...")
            
            # Toplu güncelleme yap
            updated = await db.user.update_many(
                where={
                    "role": "ADMIN",
                    "studioId": None
                },
                data={"studioId": studio_id}
            )
            
            print(f"✅ Başarıyla {updated} adet Admin hesabına {studio.name} stüdyosu atandı!")

    except Exception as e:
        print(f"❌ Bir hata oluştu: {str(e)}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
