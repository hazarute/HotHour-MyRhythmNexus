#!/usr/bin/env python3
"""
Studioları Listeleme Scripti
Kullanım: python scripts/list_studios.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()

async def list_studios():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        studios = await prisma.studio.find_many(
            include={
                "users": True,
                "auctions": True
            }
        )
        
        print("\n=== KAYITLI STUDIOLAR ===")
        if not studios:
            print("Henüz hiç studio kaydedilmemiş.")
        
        for s in studios:
            admin_count = len([u for u in s.users if u.role == "ADMIN"])
            print(f"ID: {s.id} | İsim: {s.name}")
            print(f"  Adres: {s.address or '-'}")
            print(f"  Bağlı Admin Sayısı: {admin_count}")
            print(f"  Açılan Oturum (Auction) Sayısı: {len(s.auctions)}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(list_studios())