import sys
import os
import asyncio
from datetime import datetime

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db
from prisma.enums import Role, AuctionStatus

async def list_data():
    print("Veritabanına bağlanılıyor...")
    await db.connect()

    print("\n" + "="*50)
    print("📊 VERİTABANI DURUM RAPORU")
    print("="*50)

    # 1. KULLANICILAR
    users = await db.user.find_many()
    print(f"\n👤 KULLANICILAR ({len(users)})")
    print("-" * 50)
    if not users:
        print("   (Veri yok)")
    else:
        print(f"   {'ID':<5} {'Role':<10} {'Email':<30} {'Ad Soyad'}")
        for u in users:
            # Handle potential Enum object vs string
            role_str = u.role.name if hasattr(u.role, 'name') else str(u.role)
            print(f"   {u.id:<5} {role_str:<10} {u.email:<30} {u.fullName}")

    # 2. AÇIK ARTIRMALAR
    auctions = await db.auction.find_many(order={'id': 'asc'})
    print(f"\n🏷️  AÇIK ARTIRMALAR ({len(auctions)})")
    print("-" * 50)
    if not auctions:
        print("   (Veri yok)")
    else:
        print(f"   {'ID':<5} {'Durum':<10} {'Fiyat':<10} {'Başlık'}")
        for a in auctions:
            # Handle potential Enum object vs string
            status_str = a.status.name if hasattr(a.status, 'name') else str(a.status)
            price_display = f"{a.currentPrice}₺"
            print(f"   {a.id:<5} {status_str:<10} {price_display:<10} {a.title}")

    # 3. REZERVASYONLAR
    reservations = await db.reservation.find_many(include={'user': True, 'auction': True})
    print(f"\n🎫 REZERVASYONLAR ({len(reservations)})")
    print("-" * 50)
    if not reservations:
        print("   (Veri yok)")
    else:
        print(f"   {'ID':<5} {'Kullanıcı':<20} {'Oturum ID':<10} {'Fiyat'}")
        for r in reservations:
            user_name = r.user.fullName if r.user else "Bilinmiyor"
            auction_id = r.auction.id if r.auction else "-"
            print(f"   {r.id:<5} {user_name:<20} {auction_id:<10} {r.lockedPrice}₺")

    print("\n" + "="*50 + "\n")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(list_data())
