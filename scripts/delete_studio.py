#!/usr/bin/env python3
"""
Studio Silme Scripti
Kullanım: python scripts/delete_studio.py <ID>
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()

async def delete_studio(studio_id: int):
    prisma = Prisma()
    await prisma.connect()
    
    try:
        # Önce stüdyo var mı diye kontrol et
        studio = await prisma.studio.find_unique(
            where={"id": studio_id},
            include={
                "users": True,
                "auctions": True
            }
        )
        
        if not studio:
            print(f"❌ Hata: {studio_id} ID'li studio bulunamadı.")
            return

        if len(studio.auctions) > 0 or len(studio.users) > 0:
            print(f"⚠️ Uyarı: Bu stüdyoya bağlı {len(studio.users)} kullanıcı ve {len(studio.auctions)} oturum (auction) var.")
            print("Lütfen önce bağlı kayıtları silin veya başka bir stüdyoya taşıyın.")
            confirm = input("Yine de silmek istiyor musunuz? Bağlı veriler de silinebilir/bozulabilir. (E/h): ")
            if confirm.lower() != 'e':
                print("İşlem iptal edildi.")
                return

        await prisma.studio.delete(where={"id": studio_id})
        print(f"✅ Studio (ID: {studio_id}, İsim: {studio.name}) başarıyla silindi!")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
    finally:
        await prisma.disconnect()

def main():
    if len(sys.argv) != 2:
        print("📋 Kullanım:")
        print("   python scripts/delete_studio.py <ID>")
        sys.exit(1)

    try:
        studio_id = int(sys.argv[1])
    except ValueError:
        print("❌ Hata: ID sayısal bir değer olmalıdır.")
        sys.exit(1)

    import asyncio
    asyncio.run(delete_studio(studio_id))

if __name__ == "__main__":
    main()