import sys
import os
import asyncio
import random
from datetime import timedelta
from decimal import Decimal

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db
from app.core.timezone import now_tr
from prisma.enums import PaymentStatus


TURBO_SHOWCASE_TITLE = "Turbo Sculpt Reformer"


def _deleted_count(result) -> int:
    if isinstance(result, int):
        return result
    return int(getattr(result, "count", 0) or 0)


async def _seed_reservations(users, auctions):
    if not users:
        print("⚠️ Kullanıcı bulunamadı. Reservation seed adımı atlandı.")
        return 0

    reservable_auctions = [
        auction for auction in auctions
        if getattr(auction, "status", None) in {"ACTIVE", "SOLD", "EXPIRED"}
    ]

    if not reservable_auctions:
        print("⚠️ Rezervasyon için uygun auction bulunamadı.")
        return 0

    print(f"\nRezervasyonlar oluşturuluyor... ({len(reservable_auctions)} uygun oturum, {len(users)} kullanıcı)")
    reservation_count = 0

    for auction in reservable_auctions:
        if getattr(auction, "title", None) == TURBO_SHOWCASE_TITLE:
            continue

        user = random.choice(users)
        status = random.choice([
            PaymentStatus.PENDING_ON_SITE,
            PaymentStatus.COMPLETED,
            PaymentStatus.CANCELLED,
        ])

        auction_id = getattr(auction, "id", None)
        if auction_id is None:
            continue

        current_price = getattr(auction, "currentPrice", Decimal("0.00"))
        booking_code = f"RES-{auction_id}-{random.randint(1000, 9999)}"

        try:
            await db.reservation.create(
                data={
                    "auctionId": auction_id,
                    "userId": getattr(user, "id", None),
                    "lockedPrice": current_price,
                    "bookingCode": booking_code,
                    "status": status,
                }
            )
            print(f"✅ Rezervasyon: {booking_code} -> {getattr(user, 'fullName', 'Kullanıcı')} ({status})")

            if status != PaymentStatus.CANCELLED:
                await db.auction.update(
                    where={"id": auction_id},
                    data={"status": "SOLD"},
                )

            reservation_count += 1
            if reservation_count >= 5:
                break
        except Exception as error:
            print(f"⚠️ Reservation hatası ({getattr(auction, 'title', '-') }): {error}")

    return reservation_count

async def seed_auctions():
    print("Veritabanına bağlanılıyor...")
    await db.connect()

    print("Mevcut rezervasyonlar temizleniyor...")
    deleted_reservations = await db.reservation.delete_many(where={})
    deleted_reservations_count = _deleted_count(deleted_reservations)
    print(f"✅ {deleted_reservations_count} rezervasyon silindi.")

    print("Mevcut oturumlar temizleniyor...")
    deleted_auctions = await db.auction.delete_many(where={})
    deleted_auctions_count = _deleted_count(deleted_auctions)
    print(f"✅ {deleted_auctions_count} açık artırma silindi.")

    now = now_tr()
    
    auctions_data = [
        # ACTIVE - normal akış
        {
            "title": "Sabah Pilates Reformer",
            "description": "Güne enerjik başlamak için birebir. Esra Hoca ile core bölgesini güçlendir.",
            "startPrice": Decimal("500.00"),
            "floorPrice": Decimal("250.00"),
            "currentPrice": Decimal("480.00"),
            "startTime": now - timedelta(minutes=15),
            "endTime": now + timedelta(minutes=45),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("10.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("6.00"),
            "turboIntervalMins": 10
        },
        # ACTIVE - turbo başladı
        {
            "title": "HIIT Cardio Burn",
            "description": "30 dakikalık yüksek yoğunluklu antrenman. Terlemeye hazır olun!",
            "startPrice": Decimal("300.00"),
            "floorPrice": Decimal("100.00"),
            "currentPrice": Decimal("120.00"),
            "startTime": now - timedelta(minutes=50),
            "endTime": now + timedelta(minutes=10),
            "dropIntervalMins": 2,
            "dropAmount": Decimal("5.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("3.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(minutes=5),
        },
        # ACTIVE - turbo görünürlüğü için ek fake senaryo
        {
            "title": "Turbo Sculpt Reformer",
            "description": "Turbo modda ilerleyen, hızlı fiyat değişimi olan vitrin seansı.",
            "startPrice": Decimal("640.00"),
            "floorPrice": Decimal("320.00"),
            "currentPrice": Decimal("410.00"),
            "startTime": now - timedelta(hours=1, minutes=10),
            "endTime": now + timedelta(minutes=35),
            "dropIntervalMins": 12,
            "dropAmount": Decimal("11.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("6.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(minutes=12),
        },
        # ACTIVE - turbo eşiğinde (tam 120 dk)
        {
            "title": "Spinning Blast 45",
            "description": "Kardiyo odaklı spinning seansı. Turbo sınır senaryosu.",
            "startPrice": Decimal("420.00"),
            "floorPrice": Decimal("210.00"),
            "currentPrice": Decimal("390.00"),
            "startTime": now - timedelta(hours=1),
            "endTime": now + timedelta(minutes=120),
            "dropIntervalMins": 15,
            "dropAmount": Decimal("12.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("7.00"),
            "turboIntervalMins": 10
        },
        # ACTIVE - floor fiyatına yakın
        {
            "title": "Power Stretch Express",
            "description": "Kısa ama yoğun esneme rutini.",
            "startPrice": Decimal("260.00"),
            "floorPrice": Decimal("140.00"),
            "currentPrice": Decimal("145.00"),
            "startTime": now - timedelta(hours=2),
            "endTime": now + timedelta(minutes=30),
            "dropIntervalMins": 10,
            "dropAmount": Decimal("8.00"),
            "status": "ACTIVE",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # DRAFT - yakın başlangıç
        {
            "title": "Advanced Yoga Flow",
            "description": "İleri seviye asanalar ve akış serileri. Deneyimli katılımcılar için.",
            "startPrice": Decimal("400.00"),
            "floorPrice": Decimal("200.00"),
            "currentPrice": Decimal("400.00"),
            "startTime": now + timedelta(minutes=20),
            "endTime": now + timedelta(hours=2, minutes=20),
            "dropIntervalMins": 10,
            "dropAmount": Decimal("20.00"),
            "status": "DRAFT",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # DRAFT - uzun süreli, turbo uygun
        {
            "title": "Mat Pilates Marathon",
            "description": "Uzun seans, dinamik fiyat testleri için ideal.",
            "startPrice": Decimal("800.00"),
            "floorPrice": Decimal("320.00"),
            "currentPrice": Decimal("800.00"),
            "startTime": now + timedelta(hours=4),
            "endTime": now + timedelta(hours=10),
            "dropIntervalMins": 30,
            "dropAmount": Decimal("24.00"),
            "status": "DRAFT",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("14.00"),
            "turboIntervalMins": 10
        },
        # DRAFT - açıklama boş senaryosu
        {
            "title": "Reformer Teknik Atölyesi",
            "description": None,
            "startPrice": Decimal("550.00"),
            "floorPrice": Decimal("275.00"),
            "currentPrice": Decimal("550.00"),
            "startTime": now + timedelta(days=1, hours=2),
            "endTime": now + timedelta(days=1, hours=5),
            "dropIntervalMins": 20,
            "dropAmount": Decimal("18.00"),
            "status": "DRAFT",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("10.00"),
            "turboIntervalMins": 10
        },
        # DRAFT - başlangıç geçmiş (scheduler transition testi)
        {
            "title": "Piloxing Fusion",
            "description": "Başlangıç zamanı geçmiş ama status DRAFT: scheduler düzeltmesi için.",
            "startPrice": Decimal("370.00"),
            "floorPrice": Decimal("180.00"),
            "currentPrice": Decimal("370.00"),
            "startTime": now - timedelta(minutes=8),
            "endTime": now + timedelta(hours=2, minutes=22),
            "dropIntervalMins": 12,
            "dropAmount": Decimal("11.00"),
            "status": "DRAFT",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # SOLD - geçmiş oturum
        {
            "title": "Özel Hamile Pilatesi",
            "description": "Güvenli ve etkili egzersizlerle hamilelik sürecini destekleyin.",
            "startPrice": Decimal("600.00"),
            "floorPrice": Decimal("400.00"),
            "currentPrice": Decimal("450.00"),
            "startTime": now - timedelta(hours=3),
            "endTime": now - timedelta(hours=2),
            "dropIntervalMins": 10,
            "dropAmount": Decimal("25.00"),
            "status": "SOLD",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # SOLD - turbo aktif senaryo
        {
            "title": "Mega Reformer Weekend",
            "description": "Yüksek fiyatlı ve turbo destekli seans, satışla kapanmış.",
            "startPrice": Decimal("950.00"),
            "floorPrice": Decimal("500.00"),
            "currentPrice": Decimal("620.00"),
            "startTime": now - timedelta(hours=6),
            "endTime": now - timedelta(hours=4),
            "dropIntervalMins": 20,
            "dropAmount": Decimal("20.00"),
            "status": "SOLD",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("12.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(hours=4, minutes=50),
        },
        # EXPIRED - floor seviyesinde bitiş
        {
            "title": "Total Body Strength",
            "description": "Tüm vücut kas gruplarını çalıştıran ağırlık antrenmanı.",
            "startPrice": Decimal("450.00"),
            "floorPrice": Decimal("225.00"),
            "currentPrice": Decimal("225.00"),
            "startTime": now - timedelta(days=1),
            "endTime": now - timedelta(days=1, hours=1),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("10.00"),
            "status": "EXPIRED",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # EXPIRED - turbo eşiğine girmeden bitmiş
        {
            "title": "TRX Core Challenge",
            "description": "Kısa süreli yüksek yoğunluk; turbo devreye girmeden biter.",
            "startPrice": Decimal("340.00"),
            "floorPrice": Decimal("170.00"),
            "currentPrice": Decimal("210.00"),
            "startTime": now - timedelta(hours=5),
            "endTime": now - timedelta(hours=3, minutes=30),
            "dropIntervalMins": 15,
            "dropAmount": Decimal("9.00"),
            "status": "EXPIRED",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("5.00"),
            "turboIntervalMins": 10
        },
        # CANCELLED - gelecekte planlanmış ama iptal
        {
            "title": "Akşam Yogası - Rahatlama",
            "description": "Günün stresini atmak için yavaş akış ve meditasyon.",
            "startPrice": Decimal("350.00"),
            "floorPrice": Decimal("150.00"),
            "currentPrice": Decimal("350.00"),
            "startTime": now + timedelta(days=1, hours=19),
            "endTime": now + timedelta(days=1, hours=20),
            "dropIntervalMins": 15,
            "dropAmount": Decimal("15.00"),
            "status": "CANCELLED",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # CANCELLED - aktifken iptal edilmiş
        {
            "title": "Functional Mobility Flow",
            "description": "Orta seviye mobilite seansı, operasyonel iptal senaryosu.",
            "startPrice": Decimal("390.00"),
            "floorPrice": Decimal("210.00"),
            "currentPrice": Decimal("330.00"),
            "startTime": now - timedelta(minutes=35),
            "endTime": now + timedelta(hours=1, minutes=25),
            "dropIntervalMins": 10,
            "dropAmount": Decimal("10.00"),
            "status": "CANCELLED",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        }
    ]

    for data in auctions_data:
        try:
            auction = await db.auction.create(data=data)
            print(f"Oluşturuldu: {getattr(auction, 'title', '-') } - ID: {getattr(auction, 'id', '-')}")
        except Exception as e:
            print(f"Hata oluştu ({data['title']}): {e}")

    users = await db.user.find_many()
    auctions = await db.auction.find_many()
    reservation_count = await _seed_reservations(users, auctions)
    print(f"\n🎉 Toplam {reservation_count} rezervasyon eklendi.")

    await db.disconnect()
    print("\nVeri ekleme tamamlandı! 🚀 (Auction + Reservation)")

if __name__ == "__main__":
    asyncio.run(seed_auctions())
