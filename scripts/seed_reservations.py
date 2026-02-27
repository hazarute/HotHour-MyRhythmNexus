import sys
import os
import asyncio
import random

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db
from prisma.enums import PaymentStatus

async def seed_reservations():
    print("Veritabanına bağlanılıyor...")
    await db.connect()

    # Get Users
    users = await db.user.find_many()
    if not users:
        print("❌ Kullanıcı bulunamadı! Önce kullanıcı oluşturun.")
        await db.disconnect()
        return

    # Get Auctions
    auctions = await db.auction.find_many()
    if not auctions:
        print("❌ Açık artırma bulunamadı! Önce auction seed edin.")
        await db.disconnect()
        return

    # Create Reservations
    print(f"\nRezervasyonlar oluşturuluyor... ({len(auctions)} oturum, {len(users)} kullanıcı)")
    
    # Simple strategy: Try to book one auction for each user if available
    
    count = 0
    for auction in auctions:
        # Skip if already reserved (has One-to-One relation)
        existing = await db.reservation.find_unique(where={'auctionId': auction.id})
        if existing:
            continue
            
        # Pick a random user
        user = random.choice(users)
        
        # Determine status randomly
        status = random.choice([
            PaymentStatus.PENDING_ON_SITE,
            PaymentStatus.COMPLETED,
            PaymentStatus.CANCELLED
        ])

        # Booking code
        booking_code = f"RES-{auction.id}-{random.randint(1000, 9999)}"

        try:
            res = await db.reservation.create(
                data={
                    "auctionId": auction.id,
                    "userId": user.id,
                    "lockedPrice": auction.currentPrice,
                    "bookingCode": booking_code,
                    "status": status
                }
            )
            print(f"✅ Rezervasyon oluşturuldu: {booking_code} -> {user.fullName} ({status})")
            
            # Update auction status if needed
            if status != PaymentStatus.CANCELLED:
                 await db.auction.update(
                     where={'id': auction.id},
                     data={'status': 'SOLD'}
                 )
            
            count += 1
            if count >= 3: # Limit to 3 reservations
                break
                
        except Exception as e:
            print(f"⚠️ Hata ({auction.title}): {e}")

    print(f"\n🎉 Toplam {count} rezervasyon eklendi.")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_reservations())
