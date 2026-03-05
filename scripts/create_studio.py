#!/usr/bin/env python3
"""
Studio Oluşturma Scripti
Kullanım: python scripts/create_studio.py "Studio Adı" ["Adres"] ["Logo URL"] ["Google Maps URL"]
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()

async def create_studio(name: str, address: str = None, logoUrl: str = None, googleMapsUrl: str = None):
    prisma = Prisma()
    await prisma.connect()
    
    try:
        new_studio = await prisma.studio.create(
            data={
                "name": name,
                "address": address,
                "logoUrl": logoUrl,
                "googleMapsUrl": googleMapsUrl
            }
        )
        print("✅ Studio başarıyla oluşturuldu!")
        print(f"   ID: {new_studio.id}")
        print(f"   İsim: {new_studio.name}")
        print(f"   Adres: {new_studio.address}")
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")
    finally:
        await prisma.disconnect()

def main():
    if len(sys.argv) < 2:
        print("📋 Kullanım:")
        print("   python scripts/create_studio.py \"Studio Adı\" [\"Adres\"] [\"Logo URL\"] [\"Google Maps URL\"]")
        print("\n💡 Örnek:")
        print("   python scripts/create_studio.py \"Merkez Studio\" \"Kadıköy, İstanbul\"")
        sys.exit(1)

    name = sys.argv[1]
    address = sys.argv[2] if len(sys.argv) > 2 else None
    logoUrl = sys.argv[3] if len(sys.argv) > 3 else None
    googleMapsUrl = sys.argv[4] if len(sys.argv) > 4 else None

    import asyncio
    asyncio.run(create_studio(name, address, logoUrl, googleMapsUrl))

if __name__ == "__main__":
    main()