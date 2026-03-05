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
# Gender dağılımı: %50 ANY | %35 FEMALE | %15 MALE
# 20 elemanlık döngü: 10 ANY, 7 FEMALE, 3 MALE
GENDER_DISTRIBUTION_PATTERN = ["ANY"] * 10 + ["FEMALE"] * 7 + ["MALE"] * 3

RESERVATION_SCENARIOS = [
    ("HIIT Cardio Burn", PaymentStatus.COMPLETED),
    ("Spinning Blast 45", PaymentStatus.PENDING_ON_SITE),
    ("Özel Hamile Pilatesi", PaymentStatus.COMPLETED),
    ("Mega Reformer Weekend", PaymentStatus.NO_SHOW),
    ("Total Body Strength", PaymentStatus.CANCELLED),
]


def _deleted_count(result) -> int:
    if isinstance(result, int):
        return result
    return int(getattr(result, "count", 0) or 0)


def _normalize_enum_name(value) -> str:
    raw = str(value or "").upper()
    return raw.split(".")[-1]


def _pick_eligible_user(users, allowed_gender: str):
    normalized_allowed = _normalize_enum_name(allowed_gender)
    if normalized_allowed == "ANY":
        return random.choice(users) if users else None

    eligible_users = [
        user for user in users
        if _normalize_enum_name(getattr(user, "gender", "")) == normalized_allowed
    ]

    if not eligible_users:
        return None

    return random.choice(eligible_users)


def _with_project_defaults(data: dict, index: int) -> dict:
    normalized = dict(data)

    end_time = normalized.get("endTime")
    scheduled_at = normalized.get("scheduledAt")

    if scheduled_at is None and end_time is not None:
        normalized["scheduledAt"] = end_time + timedelta(minutes=45)

    if normalized.get("allowedGender") is None:
        normalized["allowedGender"] = GENDER_DISTRIBUTION_PATTERN[index % len(GENDER_DISTRIBUTION_PATTERN)]

    if not normalized.get("turboEnabled", False):
        normalized["turboDropAmount"] = Decimal("0.00")
        normalized["turboTriggerMins"] = 120
        normalized["turboIntervalMins"] = 10
        normalized["turboStartedAt"] = None

    return normalized


async def _seed_reservations(users, auctions):
    if not users:
        print("⚠️ Kullanıcı bulunamadı. Reservation seed adımı atlandı.")
        return 0

    if not auctions:
        print("⚠️ Rezervasyon için uygun auction bulunamadı.")
        return 0

    by_title = {getattr(auction, "title", ""): auction for auction in auctions}

    print(f"\nRezervasyonlar oluşturuluyor... ({len(RESERVATION_SCENARIOS)} hedef senaryo, {len(users)} kullanıcı)")
    reservation_count = 0

    for title, status in RESERVATION_SCENARIOS:
        auction = by_title.get(title)
        if auction is None:
            print(f"⚠️ Auction bulunamadı, rezervasyon senaryosu atlandı: {title}")
            continue

        auction_status = str(getattr(auction, "status", "")).upper()
        if auction_status not in {"ACTIVE", "SOLD", "EXPIRED"}:
            print(f"⚠️ Reservation için uygun status değil, atlandı: {title} ({auction_status})")
            continue

        allowed_gender = getattr(auction, "allowedGender", "ANY")
        user = _pick_eligible_user(users, allowed_gender)
        if user is None:
            print(f"⚠️ Uygun kullanıcı bulunamadı, rezervasyon atlandı: {getattr(auction, 'title', '-') } ({allowed_gender})")
            continue

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
        except Exception as error:
            print(f"⚠️ Reservation hatası ({getattr(auction, 'title', '-') }): {error}")

    return reservation_count

async def seed_auctions():
    print("Veritabanına bağlanılıyor...")
    await db.connect()

    print("\n" + "="*80)
    print("SEED KONFIGÜRASYONU")
    print("="*80)
    print(f"Gender Dağılımı: %50 ANY | %35 FEMALE | %15 MALE")
    print(f"Turbo Minimum Süresi: 180 dakika | Trigger: 120 dk öncesi | Interval: 10 dk")
    print(f"Test Senaryoları: 15 farklı durum (ACTIVE, DRAFT, SOLD, EXPIRED, CANCELLED)")
    print("="*80 + "\n")

    print("Mevcut rezervasyonlar temizleniyor...")
    deleted_reservations = await db.reservation.delete_many(where={})
    deleted_reservations_count = _deleted_count(deleted_reservations)
    print(f"✅ {deleted_reservations_count} rezervasyon silindi.")

    print("Mevcut oturumlar temizleniyor...")
    deleted_auctions = await db.auction.delete_many(where={})
    deleted_auctions_count = _deleted_count(deleted_auctions)
    print(f"✅ {deleted_auctions_count} açık artırma silindi.")

    now = now_tr()
    
    # --- AUCTION TEST SENARYOLARI ---
    # Açıklama: Bu veriler Frontend Form bağlamında doğru yapılandırma test etmek için tasarlanmıştır.
    # Turbo Mode Kuralı: Minimum 180 dakika (3 saat) süresi gerekli, son 120 dakikada etkinleştirilir.
    # Gender Koşulu: FEMALE, MALE, ANY - index'e göre dağıtılır.
    # Status Türleri: DRAFT, ACTIVE, SOLD, EXPIRED, CANCELLED
    
    auctions_data = [
        # ACTIVE - normal akış
        {
            "title": "Sabah Pilates Reformer",
            "description": "Güne enerjik başlamak için birebir. Esra Hoca ile core bölgesini güçlendir.",
            "startPrice": Decimal("500.00"),
            "floorPrice": Decimal("250.00"),
            "currentPrice": Decimal("480.00"),
            "startTime": now - timedelta(minutes=30),
            "endTime": now + timedelta(minutes=60),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("10.00"),
            "status": "ACTIVE",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # ACTIVE - turbo başladı (remaining <= 120)
        {
            "title": "HIIT Cardio Burn",
            "description": "30 dakikalık yüksek yoğunluklu antrenman. Terlemeye hazır olun!",
            "startPrice": Decimal("300.00"),
            "floorPrice": Decimal("100.00"),
            "currentPrice": Decimal("180.00"),
            "startTime": now - timedelta(hours=2, minutes=20),
            "endTime": now + timedelta(minutes=100),
            "dropIntervalMins": 20,
            "dropAmount": Decimal("12.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("7.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(minutes=8),
        },
        # ACTIVE - turbo eşiğine henüz girmedi (remaining > 120)
        {
            "title": "Turbo Sculpt Reformer",
            "description": "Turbo modda ilerleyen, hızlı fiyat değişimi olan vitrin seansı.",
            "startPrice": Decimal("640.00"),
            "floorPrice": Decimal("320.00"),
            "currentPrice": Decimal("590.00"),
            "startTime": now - timedelta(minutes=90),
            "endTime": now + timedelta(minutes=150),
            "dropIntervalMins": 20,
            "dropAmount": Decimal("14.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("8.00"),
            "turboIntervalMins": 10,
        },
        # ACTIVE - turbo eşiğinde (tam 120 dk)
        {
            "title": "Spinning Blast 45",
            "description": "Kardiyo odaklı spinning seansı. Turbo sınır senaryosu.",
            "startPrice": Decimal("420.00"),
            "floorPrice": Decimal("210.00"),
            "currentPrice": Decimal("360.00"),
            "startTime": now - timedelta(hours=1, minutes=30),
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
            "endTime": now + timedelta(hours=9),
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
            "endTime": now + timedelta(days=1, hours=6),
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
            "endTime": now + timedelta(hours=2, minutes=52),
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
            "startTime": now - timedelta(hours=4),
            "endTime": now - timedelta(hours=2, minutes=30),
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
            "startTime": now - timedelta(hours=8),
            "endTime": now - timedelta(hours=4),
            "dropIntervalMins": 20,
            "dropAmount": Decimal("20.00"),
            "status": "SOLD",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("12.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(hours=5, minutes=40),
        },
        # EXPIRED - floor seviyesinde bitiş
        {
            "title": "Total Body Strength",
            "description": "Tüm vücut kas gruplarını çalıştıran ağırlık antrenmanı.",
            "startPrice": Decimal("450.00"),
            "floorPrice": Decimal("225.00"),
            "currentPrice": Decimal("225.00"),
            "startTime": now - timedelta(hours=4),
            "endTime": now - timedelta(hours=1),
            "dropIntervalMins": 10,
            "dropAmount": Decimal("10.00"),
            "status": "EXPIRED",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10
        },
        # EXPIRED - turbo destekli, geçmişte tamamlanmış
        {
            "title": "TRX Core Challenge",
            "description": "Kısa süreli yüksek yoğunluk; turbo devreye girmeden biter.",
            "startPrice": Decimal("340.00"),
            "floorPrice": Decimal("170.00"),
            "currentPrice": Decimal("210.00"),
            "startTime": now - timedelta(hours=7),
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


    print('Mock Stüdyolar hazırlanıyor...')
    base_studios_data = [
        {'name': 'Ritim Dans & Pilates Stüdyosu', 'logoUrl': 'https://api.dicebear.com/7.x/initials/svg?seed=RD&backgroundColor=1E1E2E', 'googleMapsUrl': 'https://maps.google.com/?q=Ritim+Dans', 'address': 'Kadıköy, İstanbul'},
        {'name': 'Neon Fit Academy', 'logoUrl': 'https://api.dicebear.com/7.x/initials/svg?seed=NF&backgroundColor=FF7B00', 'googleMapsUrl': 'https://maps.google.com/?q=Neon+Fit', 'address': 'Beşiktaş, İstanbul'},
        {'name': 'Zen Space Yoga', 'logoUrl': 'https://api.dicebear.com/7.x/initials/svg?seed=ZS&backgroundColor=8000FF', 'googleMapsUrl': 'https://maps.google.com/?q=Zen+Space', 'address': 'Şişli, İstanbul'}
    ]
    
    mock_studios = []
    for s_data in base_studios_data:
        existing = await db.studio.find_first(where={'name': s_data['name']})
        if not existing:
            existing = await db.studio.create(data=s_data)
        mock_studios.append(existing)

    print(f'✅ {len(mock_studios)} mock stüdyo hazır.')

    normalized_auctions = [

        _with_project_defaults(data, index)
        for index, data in enumerate(auctions_data)
    ]


    for data in normalized_auctions:
        random_studio = random.choice(mock_studios)
        data['studioId'] = random_studio.id
        try:

            auction = await db.auction.create(data=data)
            print(
                f"✅ {getattr(auction, 'title', '-'):40s} | "
                f"ID:{str(getattr(auction, 'id', '-')):3s} | "
                f"Gender:{getattr(auction, 'allowedGender', 'ANY'):6s} | "
                f"Status:{getattr(auction, 'status', 'DRAFT'):8s} | "
                f"Turbo:{str(getattr(auction, 'turboEnabled', False)):5s}"
            )
        except Exception as e:
            print(f"⚠️  Error creating {data['title']}: {e}")

    print("\nMock Kullanıcılar (Müşteriler) hazırlanıyor...")
    # Dummy bcrypt hash for '123456'
    dummy_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq"
    
    mock_users_data = [
        {"email": "female_mock@test.com", "phone": "5550001122", "fullName": "Ceren Yılmaz", "gender": "FEMALE", "hashedPassword": dummy_hash, "isVerified": True},
        {"email": "male_mock@test.com", "phone": "5550001133", "fullName": "Burak Yılmaz", "gender": "MALE", "hashedPassword": dummy_hash, "isVerified": True}
    ]
    
    for u_data in mock_users_data:
        existing_u = await db.user.find_first(where={"email": u_data["email"]})
        if not existing_u:
            await db.user.create(data=u_data)
            print(f"✅ Mock Kullanıcı Oluşturuldu: {u_data['fullName']} ({u_data['gender']})")

    users = await db.user.find_many()
    auctions = await db.auction.find_many()
    
    print(f"\n{'='*80}")
    print(f"REZERVASYONLAR EKLENIYOR...")
    print(f"{'='*80}\n")
    
    reservation_count = await _seed_reservations(users, auctions)
    
    print(f"\n{'='*80}")
    print(f"SEED İŞLEMİ TAMAMLANDI")
    print(f"{'='*80}")
    print(f"✅ Toplam {len(auctions)} oturum oluşturuldu")
    print(f"✅ Toplam {reservation_count} rezervasyon eklendi")
    print(f"{'='*80}\n")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_auctions())
