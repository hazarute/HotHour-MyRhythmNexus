#!/usr/bin/env python3
"""
Gercekci, deterministik ve taksonomiyle tutarli mock veri seed scripti.

Bu script:
- isletmeleri sektorleriyle birlikte hazirlar
- firsatlari dogru hizmet kategorileriyle olusturur
- musteri kullanicilarini gercek senaryo gibi ekler
- rezervasyonlari cinsiyet ve durum kurallarina uygun baglar
"""

import asyncio
import os
import sys
from datetime import timedelta
from decimal import Decimal

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db
from app.core.timezone import now_tr
from prisma.enums import PaymentStatus


def money(value: str) -> Decimal:
    return Decimal(value)


STUDIO_SCENARIOS = [
    {
        "name": "Neon Fit Academy",
        "address": "Levazim Mah. Kore Sehitleri Cad. No:14 Besiktas / Istanbul",
        "logoUrl": "https://api.dicebear.com/7.x/initials/svg?seed=NF&backgroundColor=FF7B00",
        "googleMapsUrl": "https://maps.google.com/?q=Neon+Fit+Academy+Besiktas",
        "sector_slugs": ["fitness"],
    },
    {
        "name": "Atelier Reformer House",
        "address": "Tesvikiye Cad. No:38 Sisli / Istanbul",
        "logoUrl": "https://api.dicebear.com/7.x/initials/svg?seed=AR&backgroundColor=E7D7C1",
        "googleMapsUrl": "https://maps.google.com/?q=Atelier+Reformer+House",
        "sector_slugs": ["wellness", "recovery"],
    },
    {
        "name": "Ritim Dans Evi",
        "address": "Moda Cad. No:92 Kadikoy / Istanbul",
        "logoUrl": "https://api.dicebear.com/7.x/initials/svg?seed=RD&backgroundColor=1E1E2E",
        "googleMapsUrl": "https://maps.google.com/?q=Ritim+Dans+Evi",
        "sector_slugs": ["dance", "wellness"],
    },
    {
        "name": "Urban Recovery Lab",
        "address": "Atasehir Bulvari No:21 Atasehir / Istanbul",
        "logoUrl": "https://api.dicebear.com/7.x/initials/svg?seed=UR&backgroundColor=2B6777",
        "googleMapsUrl": "https://maps.google.com/?q=Urban+Recovery+Lab",
        "sector_slugs": ["recovery", "fitness"],
    },
]


CUSTOMER_SCENARIOS = [
    {
        "email": "zeynep.arslan@example.com",
        "phone": "+905550000101",
        "fullName": "Zeynep Arslan",
        "gender": "FEMALE",
    },
    {
        "email": "melis.kaya@example.com",
        "phone": "+905550000102",
        "fullName": "Melis Kaya",
        "gender": "FEMALE",
    },
    {
        "email": "derya.ozkan@example.com",
        "phone": "+905550000103",
        "fullName": "Derya Ozkan",
        "gender": "FEMALE",
    },
    {
        "email": "ece.sahin@example.com",
        "phone": "+905550000104",
        "fullName": "Ece Sahin",
        "gender": "FEMALE",
    },
    {
        "email": "emre.alkan@example.com",
        "phone": "+905550000105",
        "fullName": "Emre Alkan",
        "gender": "MALE",
    },
    {
        "email": "can.demir@example.com",
        "phone": "+905550000106",
        "fullName": "Can Demir",
        "gender": "MALE",
    },
    {
        "email": "mert.kaplan@example.com",
        "phone": "+905550000107",
        "fullName": "Mert Kaplan",
        "gender": "MALE",
    },
    {
        "email": "selin.yildiz@example.com",
        "phone": "+905550000108",
        "fullName": "Selin Yildiz",
        "gender": "FEMALE",
    },
]


RESERVATION_SCENARIOS = [
    {
        "auction_title": "06:30 Kurumsal HIIT Express",
        "user_email": "zeynep.arslan@example.com",
        "status": PaymentStatus.COMPLETED,
    },
    {
        "auction_title": "Oglen Arasi Power Cycle 45",
        "user_email": "melis.kaya@example.com",
        "status": PaymentStatus.PENDING_ON_SITE,
    },
    {
        "auction_title": "Hamilelikte Reformer Destegi",
        "user_email": "derya.ozkan@example.com",
        "status": PaymentStatus.COMPLETED,
    },
    {
        "auction_title": "Cumartesi Guc Kampi",
        "user_email": "emre.alkan@example.com",
        "status": PaymentStatus.NO_SHOW,
    },
    {
        "auction_title": "Runner Mobility Reset",
        "user_email": "can.demir@example.com",
        "status": PaymentStatus.CANCELLED,
    },
]


def build_auction_scenarios(now):
    return [
        {
            "title": "06:30 Kurumsal HIIT Express",
            "studio_name": "Neon Fit Academy",
            "service_category_slug": "hiit",
            "description": "Plaza calisanlari icin sabah erken saatte yapilan, 35 dakikalik yuksek tempolu grup dersi.",
            "allowedGender": "ANY",
            "startPrice": money("380.00"),
            "floorPrice": money("210.00"),
            "currentPrice": money("332.00"),
            "startTime": now - timedelta(minutes=35),
            "endTime": now + timedelta(minutes=85),
            "scheduledAt": now + timedelta(minutes=130),
            "dropIntervalMins": 10,
            "dropAmount": money("12.00"),
            "status": "ACTIVE",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Oglen Arasi Power Cycle 45",
            "studio_name": "Neon Fit Academy",
            "service_category_slug": "spinning",
            "description": "Ofis arasina sigan 45 dakikalik spinning seansi. Hedef, yuksek kalori yakimi ve tempo kontrolu.",
            "allowedGender": "FEMALE",
            "startPrice": money("420.00"),
            "floorPrice": money("220.00"),
            "currentPrice": money("356.00"),
            "startTime": now - timedelta(hours=2),
            "endTime": now + timedelta(minutes=100),
            "scheduledAt": now + timedelta(minutes=145),
            "dropIntervalMins": 15,
            "dropAmount": money("14.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": money("8.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(minutes=6),
        },
        {
            "title": "Cumartesi Guc Kampi",
            "studio_name": "Neon Fit Academy",
            "service_category_slug": "strength-training",
            "description": "Hafta sonu icin planlanan tam vucut kuvvet kampi. Serbest agirlik ve istasyon calismalari icerir.",
            "allowedGender": "ANY",
            "startPrice": money("640.00"),
            "floorPrice": money("360.00"),
            "currentPrice": money("490.00"),
            "startTime": now - timedelta(hours=7),
            "endTime": now - timedelta(hours=4, minutes=30),
            "scheduledAt": now - timedelta(hours=4),
            "dropIntervalMins": 20,
            "dropAmount": money("18.00"),
            "status": "SOLD",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": money("10.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(hours=5, minutes=15),
        },
        {
            "title": "Aksam Atletik Kondisyon 101",
            "studio_name": "Neon Fit Academy",
            "service_category_slug": "hiit",
            "description": "Yeni baslayan erkek uyeler icin interval kondisyon dersi. Temel nefes ve ritim takibi anlatilir.",
            "allowedGender": "MALE",
            "startPrice": money("340.00"),
            "floorPrice": money("180.00"),
            "currentPrice": money("340.00"),
            "startTime": now + timedelta(hours=5),
            "endTime": now + timedelta(hours=7),
            "scheduledAt": now + timedelta(hours=7, minutes=30),
            "dropIntervalMins": 15,
            "dropAmount": money("11.00"),
            "status": "DRAFT",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Gune Baslangic Reformer",
            "studio_name": "Atelier Reformer House",
            "service_category_slug": "reformer-pilates",
            "description": "Calisma oncesi postur odakli reformer dersi. Core aktivasyonu ve kontrollu gecisler uzerine kurulu.",
            "allowedGender": "FEMALE",
            "startPrice": money("560.00"),
            "floorPrice": money("320.00"),
            "currentPrice": money("472.00"),
            "startTime": now - timedelta(minutes=50),
            "endTime": now + timedelta(minutes=70),
            "scheduledAt": now + timedelta(minutes=120),
            "dropIntervalMins": 10,
            "dropAmount": money("12.00"),
            "status": "ACTIVE",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Hamilelikte Reformer Destegi",
            "studio_name": "Atelier Reformer House",
            "service_category_slug": "reformer-pilates",
            "description": "Hamilelik doneminde uzman egitmen esliginde yapilan dusuk etkili reformer calismasi.",
            "allowedGender": "FEMALE",
            "startPrice": money("720.00"),
            "floorPrice": money("460.00"),
            "currentPrice": money("540.00"),
            "startTime": now - timedelta(hours=5),
            "endTime": now - timedelta(hours=3, minutes=30),
            "scheduledAt": now - timedelta(hours=3),
            "dropIntervalMins": 15,
            "dropAmount": money("16.00"),
            "status": "SOLD",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Ofis Sonrasi Mat Pilates",
            "studio_name": "Atelier Reformer House",
            "service_category_slug": "mat-pilates",
            "description": "Masa basi calisanlar icin omurga ve kalca odakli mat pilates rutini.",
            "allowedGender": "ANY",
            "startPrice": money("320.00"),
            "floorPrice": money("180.00"),
            "currentPrice": money("320.00"),
            "startTime": now + timedelta(hours=8),
            "endTime": now + timedelta(hours=10),
            "scheduledAt": now + timedelta(hours=10, minutes=30),
            "dropIntervalMins": 20,
            "dropAmount": money("10.00"),
            "status": "DRAFT",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Bel ve Boyun Rahatlatan Stretch",
            "studio_name": "Atelier Reformer House",
            "service_category_slug": "stretching",
            "description": "Uzun ekran kullanimi sonrasi boyun, sirt ve bel hattini rahatlatan dusuk tempolu esneme akisi.",
            "allowedGender": "ANY",
            "startPrice": money("290.00"),
            "floorPrice": money("170.00"),
            "currentPrice": money("246.00"),
            "startTime": now - timedelta(minutes=20),
            "endTime": now + timedelta(hours=1, minutes=10),
            "scheduledAt": now + timedelta(hours=1, minutes=55),
            "dropIntervalMins": 10,
            "dropAmount": money("8.00"),
            "status": "CANCELLED",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Baslangic Seviyesi Salsa Atolyesi",
            "studio_name": "Ritim Dans Evi",
            "service_category_slug": "dance-class",
            "description": "Partnerli temel adimlar, ritim takibi ve muzikaliteye giris iceren aksiyonlu grup atolyeleri.",
            "allowedGender": "ANY",
            "startPrice": money("360.00"),
            "floorPrice": money("190.00"),
            "currentPrice": money("308.00"),
            "startTime": now - timedelta(minutes=15),
            "endTime": now + timedelta(hours=1, minutes=45),
            "scheduledAt": now + timedelta(hours=2, minutes=30),
            "dropIntervalMins": 12,
            "dropAmount": money("9.00"),
            "status": "ACTIVE",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Nefes Odakli Sabah Yoga",
            "studio_name": "Ritim Dans Evi",
            "service_category_slug": "yoga",
            "description": "Dans egitmenleri ve masa basi calisanlar icin nefes, denge ve esneklik odakli yoga akisi.",
            "allowedGender": "ANY",
            "startPrice": money("340.00"),
            "floorPrice": money("180.00"),
            "currentPrice": money("180.00"),
            "startTime": now - timedelta(hours=4),
            "endTime": now - timedelta(hours=2, minutes=30),
            "scheduledAt": now - timedelta(hours=2),
            "dropIntervalMins": 10,
            "dropAmount": money("10.00"),
            "status": "EXPIRED",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Koreografi Teknik Kampi",
            "studio_name": "Ritim Dans Evi",
            "service_category_slug": "dance-class",
            "description": "Hafta sonu sahne provasi oncesi koreografi tekrar seansi. Grup uyumu ve ritim netligi uzerine kurulu.",
            "allowedGender": "FEMALE",
            "startPrice": money("500.00"),
            "floorPrice": money("260.00"),
            "currentPrice": money("500.00"),
            "startTime": now + timedelta(days=1, hours=3),
            "endTime": now + timedelta(days=1, hours=5),
            "scheduledAt": now + timedelta(days=1, hours=5, minutes=30),
            "dropIntervalMins": 20,
            "dropAmount": money("15.00"),
            "status": "DRAFT",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": money("9.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Runner Mobility Reset",
            "studio_name": "Urban Recovery Lab",
            "service_category_slug": "stretching",
            "description": "Kosucular icin ayak bilegi, kalca ve hamstring mobilitesi odakli toparlanma seansi.",
            "allowedGender": "ANY",
            "startPrice": money("310.00"),
            "floorPrice": money("160.00"),
            "currentPrice": money("196.00"),
            "startTime": now - timedelta(hours=6),
            "endTime": now - timedelta(hours=4, minutes=15),
            "scheduledAt": now - timedelta(hours=3, minutes=45),
            "dropIntervalMins": 10,
            "dropAmount": money("9.00"),
            "status": "EXPIRED",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": money("0.00"),
            "turboIntervalMins": 10,
        },
        {
            "title": "Fonksiyonel Kuvvet Dengeleme",
            "studio_name": "Urban Recovery Lab",
            "service_category_slug": "strength-training",
            "description": "Eski sakatlik sonrasi kontrollu sekilde kuvvet geri kazandiran, fizyoterapist destekli mini grup dersi.",
            "allowedGender": "MALE",
            "startPrice": money("470.00"),
            "floorPrice": money("250.00"),
            "currentPrice": money("398.00"),
            "startTime": now - timedelta(hours=1, minutes=10),
            "endTime": now + timedelta(minutes=95),
            "scheduledAt": now + timedelta(minutes=150),
            "dropIntervalMins": 15,
            "dropAmount": money("13.00"),
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": money("7.00"),
            "turboIntervalMins": 10,
            "turboStartedAt": now - timedelta(minutes=4),
        },
    ]


def _deleted_count(result) -> int:
    if isinstance(result, int):
        return result
    return int(getattr(result, "count", 0) or 0)


def _normalize_enum_name(value) -> str:
    raw = str(value or "").upper()
    return raw.split(".")[-1]


async def _load_taxonomy_maps():
    sectors = await db.sector.find_many(where={"isActive": True})
    categories = await db.servicecategory.find_many(where={"isActive": True}, include={"sector": True})

    sector_ids_by_slug = {getattr(sector, "slug", None): getattr(sector, "id", None) for sector in sectors}
    category_records_by_slug = {}

    for category in categories:
        sector = getattr(category, "sector", None)
        category_records_by_slug[getattr(category, "slug", None)] = {
            "id": getattr(category, "id", None),
            "name": getattr(category, "name", None),
            "sector_slug": getattr(sector, "slug", None),
        }

    return sector_ids_by_slug, category_records_by_slug


def _validate_seed_blueprint(sector_ids_by_slug, category_records_by_slug, auction_scenarios):
    studio_sector_map = {studio["name"]: set(studio["sector_slugs"]) for studio in STUDIO_SCENARIOS}
    user_email_set = {user["email"] for user in CUSTOMER_SCENARIOS}

    for studio in STUDIO_SCENARIOS:
        for sector_slug in studio["sector_slugs"]:
            if sector_slug not in sector_ids_by_slug:
                raise ValueError(f"Seed hatasi: sektor bulunamadi -> {sector_slug}")

    for scenario in auction_scenarios:
        studio_name = scenario["studio_name"]
        category_slug = scenario["service_category_slug"]

        if studio_name not in studio_sector_map:
            raise ValueError(f"Seed hatasi: tanimsiz isletme -> {studio_name}")

        category_record = category_records_by_slug.get(category_slug)
        if not category_record:
            raise ValueError(f"Seed hatasi: hizmet kategorisi bulunamadi -> {category_slug}")

        category_sector_slug = category_record.get("sector_slug")
        if category_sector_slug not in studio_sector_map[studio_name]:
            raise ValueError(
                "Seed hatasi: firsatin hizmet kategorisi, bagli oldugu isletmenin sektorleriyle uyusmuyor -> "
                f"{scenario['title']} / {studio_name} / {category_slug}"
            )

    for reservation in RESERVATION_SCENARIOS:
        if reservation["user_email"] not in user_email_set:
            raise ValueError(f"Seed hatasi: rezervasyon kullanicisi bulunamadi -> {reservation['user_email']}")

        if reservation["auction_title"] not in {scenario["title"] for scenario in auction_scenarios}:
            raise ValueError(f"Seed hatasi: rezervasyon firsati bulunamadi -> {reservation['auction_title']}")


async def _upsert_studios(sector_ids_by_slug):
    studios_by_name = {}

    print("Mock isletmeler hazirlaniyor...")
    for scenario in STUDIO_SCENARIOS:
        payload = {
            "name": scenario["name"],
            "address": scenario["address"],
            "logoUrl": scenario["logoUrl"],
            "googleMapsUrl": scenario["googleMapsUrl"],
        }

        existing_list = await db.studio.find_many(where={"name": scenario["name"]}, take=1)
        existing = existing_list[0] if existing_list else None
        if existing:
            existing_id = getattr(existing, "id", None)
            if existing_id is None:
                raise ValueError(f"Seed hatasi: isletme id okunamadi -> {scenario['name']}")
            studio = await db.studio.update(where={"id": existing_id}, data=payload)
        else:
            studio = await db.studio.create(data=payload)

        studio_id = getattr(studio, "id", None)
        if studio_id is None:
            raise ValueError(f"Seed hatasi: olusturulan isletmenin id degeri bos -> {scenario['name']}")

        await db.studiosector.delete_many(where={"studioId": studio_id})
        for sector_slug in scenario["sector_slugs"]:
            await db.studiosector.create(
                data={
                    "studioId": studio_id,
                    "sectorId": sector_ids_by_slug[sector_slug],
                }
            )

        studios_by_name[scenario["name"]] = {
            "record": studio,
            "sector_slugs": set(scenario["sector_slugs"]),
        }
        print(f"✅ Isletme hazir: {scenario['name']} -> {', '.join(scenario['sector_slugs'])}")

    return studios_by_name


async def _upsert_customers():
    dummy_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq"
    users_by_email = {}

    print("\nMock musteriler hazirlaniyor...")
    for scenario in CUSTOMER_SCENARIOS:
        payload = {
            "email": scenario["email"],
            "phone": scenario["phone"],
            "fullName": scenario["fullName"],
            "gender": scenario["gender"],
            "hashedPassword": dummy_hash,
            "isVerified": True,
        }

        existing = await db.user.find_unique(where={"email": scenario["email"]})
        if existing:
            existing_id = getattr(existing, "id", None)
            if existing_id is None:
                raise ValueError(f"Seed hatasi: kullanici id okunamadi -> {scenario['email']}")
            user = await db.user.update(where={"id": existing_id}, data=payload)
        else:
            user = await db.user.create(data=payload)

        users_by_email[scenario["email"]] = user
        print(f"✅ Musteri hazir: {scenario['fullName']} ({scenario['gender']})")

    return users_by_email


async def _seed_auctions(auction_scenarios, studios_by_name, category_records_by_slug):
    auctions_by_title = {}

    print("\nFirsatlar olusturuluyor...")
    for scenario in auction_scenarios:
        studio_context = studios_by_name[scenario["studio_name"]]
        category_record = category_records_by_slug[scenario["service_category_slug"]]

        auction = await db.auction.create(
            data={
                "title": scenario["title"],
                "description": scenario["description"],
                "allowedGender": scenario["allowedGender"],
                "startPrice": scenario["startPrice"],
                "floorPrice": scenario["floorPrice"],
                "currentPrice": scenario["currentPrice"],
                "startTime": scenario["startTime"],
                "endTime": scenario["endTime"],
                "scheduledAt": scenario["scheduledAt"],
                "dropIntervalMins": scenario["dropIntervalMins"],
                "dropAmount": scenario["dropAmount"],
                "status": scenario["status"],
                "turboEnabled": scenario["turboEnabled"],
                "turboTriggerMins": scenario["turboTriggerMins"],
                "turboDropAmount": scenario["turboDropAmount"],
                "turboIntervalMins": scenario["turboIntervalMins"],
                "turboStartedAt": scenario.get("turboStartedAt"),
                "studioId": studio_context["record"].id,
                "serviceCategoryId": category_record["id"],
            }
        )

        auctions_by_title[scenario["title"]] = auction
        print(
            f"✅ {scenario['title']:32s} | Isletme: {scenario['studio_name']:22s} | "
            f"Kategori: {category_record['name']:18s} | Durum: {scenario['status']}"
        )

    return auctions_by_title


async def _seed_reservations(users_by_email, auctions_by_title):
    print("\nRezervasyonlar olusturuluyor...")
    reservation_count = 0

    for index, scenario in enumerate(RESERVATION_SCENARIOS, start=1):
        auction = auctions_by_title[scenario["auction_title"]]
        user = users_by_email[scenario["user_email"]]

        allowed_gender = _normalize_enum_name(getattr(auction, "allowedGender", "ANY"))
        user_gender = _normalize_enum_name(getattr(user, "gender", ""))
        if allowed_gender != "ANY" and allowed_gender != user_gender:
            raise ValueError(
                f"Seed hatasi: {scenario['auction_title']} icin kullanici cinsiyet uyusmazligi var -> {scenario['user_email']}"
            )

        booking_code = f"SCN-{getattr(auction, 'id', index)}-{index:03d}"
        await db.reservation.create(
            data={
                "auctionId": getattr(auction, "id", None),
                "userId": getattr(user, "id", None),
                "lockedPrice": getattr(auction, "currentPrice", money("0.00")),
                "bookingCode": booking_code,
                "status": scenario["status"],
            }
        )

        if scenario["status"] != PaymentStatus.CANCELLED:
            await db.auction.update(
                where={"id": getattr(auction, "id", None)},
                data={"status": "SOLD"},
            )

        reservation_count += 1
        print(
            f"✅ {booking_code} -> {getattr(user, 'fullName', '-') } / "
            f"{scenario['auction_title']} ({scenario['status']})"
        )

    return reservation_count


async def seed_auctions():
    print("Veritabanina baglaniliyor...")
    await db.connect()

    try:
        auction_scenarios = build_auction_scenarios(now_tr())
        sector_ids_by_slug, category_records_by_slug = await _load_taxonomy_maps()

        if not sector_ids_by_slug or not category_records_by_slug:
            raise RuntimeError(
                "Aktif taxonomy bulunamadi. Once 'python scripts/taxonomy/seed_taxonomy.py --update-existing' calistirin."
            )

        _validate_seed_blueprint(sector_ids_by_slug, category_records_by_slug, auction_scenarios)

        print("\nMevcut rezervasyonlar temizleniyor...")
        deleted_reservations = await db.reservation.delete_many(where={})
        print(f"✅ {_deleted_count(deleted_reservations)} rezervasyon silindi.")

        print("Mevcut firsatlar temizleniyor...")
        deleted_auctions = await db.auction.delete_many(where={})
        print(f"✅ {_deleted_count(deleted_auctions)} firsat silindi.")

        studios_by_name = await _upsert_studios(sector_ids_by_slug)
        users_by_email = await _upsert_customers()
        auctions_by_title = await _seed_auctions(auction_scenarios, studios_by_name, category_records_by_slug)
        reservation_count = await _seed_reservations(users_by_email, auctions_by_title)

        print("\n" + "=" * 88)
        print("SEED ISLEMI TAMAMLANDI")
        print("=" * 88)
        print(f"✅ Isletme sayisi: {len(studios_by_name)}")
        print(f"✅ Musteri sayisi: {len(users_by_email)}")
        print(f"✅ Firsat sayisi: {len(auctions_by_title)}")
        print(f"✅ Rezervasyon sayisi: {reservation_count}")
        print("✅ Tum firsatlar, bagli olduklari hizmet kategorisi ve isletme sektorleriyle tutarli sekilde olusturuldu.")
        print("=" * 88 + "\n")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(seed_auctions())