"""
Tesler: İptal Sonrası Yeniden Rezervasyon Kısıtı (10 Gün Kuralı)

Kapsam:
- Kullanıcı kendi iptal ettiği bir rezervasyondan sonra cancelledAt ve cancelSource alanları doğru kapydediliyor mu?
- Aynı stüdyo + aynı hizmet kategorisinde yeniden booking yapıldığında 10 günlük kısıt devreye giriyor mu?
- Admin iptalleri ve sistem iptalleri bu kısıtı tetiklemiyor mu?
- Farklı stüdyo veya farklı kategori için kısıt uygulanmıyor mu?
"""

import uuid
import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core import db, security


# ─── Fixtures / Helpers ──────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()
    yield
    if db.db.is_connected():
        await db.db.disconnect()


async def _create_user(email: str, phone: str, password: str = "Pass123!", role: str = "USER", gender: str = "FEMALE"):
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": "Test User",
            "hashedPassword": security.get_password_hash(password),
            "role": role,
            "gender": gender,
            "isVerified": True,
        }
    )


async def _create_studio():
    return await db.db.studio.create(data={"name": f"Studio-{uuid.uuid4().hex[:6]}"})


async def _create_sector():
    return await db.db.sector.create(
        data={"name": f"Sector-{uuid.uuid4().hex[:6]}", "slug": f"sector-{uuid.uuid4().hex[:6]}", "isActive": True}
    )


async def _create_service_category(studio_id: int = None, sector_id: int | None = None):
    """Sector gerektirmeyen basit bir hizmet kategorisi oluşturur."""
    return await db.db.servicecategory.create(
        data={
            "name": f"Cat-{uuid.uuid4().hex[:6]}",
            "slug": f"cat-{uuid.uuid4().hex[:6]}",
            "sectorId": sector_id,
        }
    )


async def _create_active_auction(studio_id: int = None, service_category_id: int = None, title: str = "Test Auction"):
    now = datetime.now(timezone.utc)
    data = {
        "title": title,
        "allowedGender": "ANY",
        "startPrice": Decimal("200.00"),
        "floorPrice": Decimal("50.00"),
        "currentPrice": Decimal("150.00"),
        "startTime": now - timedelta(minutes=5),
        "endTime": now + timedelta(hours=2),
        "dropIntervalMins": 60,
        "dropAmount": Decimal("10.00"),
        "status": "ACTIVE",
    }
    if studio_id:
        data["studioId"] = studio_id
    if service_category_id:
        data["serviceCategoryId"] = service_category_id
    return await db.db.auction.create(data=data)


async def _login_and_book(client: AsyncClient, email: str, password: str, auction_id: int, user_id: int) -> dict:
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, f"Login failed: {login.text}"
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/reservations/book",
        json={"auction_id": auction_id, "user_id": user_id},
        headers=headers,
    )
    return {"response": resp, "token": token, "headers": headers}


# ─── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_cancel_saves_cancellation_fields():
    """
    Kullanıcı kendi rezervasyonunu iptal ettiğinde cancelledAt ve cancelSource='USER'
    DB'ye doğru kaydedilmeli.
    """
    email = f"cancel+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+900{uuid.uuid4().hex[:8]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    auction = await _create_active_auction()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await _login_and_book(client, email, password, auction.id, user.id)
        assert result["response"].status_code == 201, result["response"].text
        reservation_id = result["response"].json()["id"]

        cancel_resp = await client.delete(
            f"/api/v1/reservations/{reservation_id}",
            headers=result["headers"],
        )
        assert cancel_resp.status_code == 204, cancel_resp.text

    reservation = await db.db.reservation.find_unique(where={"id": reservation_id})
    assert reservation is not None
    assert reservation.cancelSource == "USER"
    assert reservation.cancelledAt is not None


@pytest.mark.asyncio
async def test_admin_cancel_saves_admin_cancel_source():
    """
    Admin iptal ettiğinde cancelSource='ADMIN' olmalı.
    """
    email = f"user+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+901{uuid.uuid4().hex[:8]}"
    admin_email = f"admin+{uuid.uuid4().hex[:8]}@test.com"
    admin_phone = f"+902{uuid.uuid4().hex[:8]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    admin = await _create_user(email=admin_email, phone=admin_phone, password=password, role="ADMIN")
    auction = await _create_active_auction()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await _login_and_book(client, email, password, auction.id, user.id)
        assert result["response"].status_code == 201
        reservation_id = result["response"].json()["id"]

        admin_login = await client.post("/api/v1/auth/login", json={"email": admin_email, "password": password})
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        cancel_resp = await client.post(
            f"/api/v1/reservations/admin/{reservation_id}/cancel",
            headers=admin_headers,
        )
        assert cancel_resp.status_code == 200, cancel_resp.text

    reservation = await db.db.reservation.find_unique(where={"id": reservation_id})
    assert reservation.cancelSource == "ADMIN"
    assert reservation.cancelledAt is not None


@pytest.mark.asyncio
async def test_user_cancel_then_rebook_same_studio_category_is_blocked():
    """
    Kullanıcı aynı stüdyo + aynı hizmet kategorisinden rezervasyonunu iptal edip
    yeni bir fırsatı booklama yapmaya çalışırsa 400 döner.
    """
    email = f"abuser+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+903{uuid.uuid4().hex[:8]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    studio = await _create_studio()
    category = await _create_service_category()

    auction1 = await _create_active_auction(studio_id=studio.id, service_category_id=category.id, title="Fırsat 1")
    auction2 = await _create_active_auction(studio_id=studio.id, service_category_id=category.id, title="Fırsat 2")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Fırsatı al
        result = await _login_and_book(client, email, password, auction1.id, user.id)
        assert result["response"].status_code == 201
        reservation_id = result["response"].json()["id"]

        # 1. Fırsatı iptal et
        cancel_resp = await client.delete(
            f"/api/v1/reservations/{reservation_id}",
            headers=result["headers"],
        )
        assert cancel_resp.status_code == 204

        # 2. Fırsatı booklama yapmaya çalış — aynı stüdyo + kategori
        rebook_resp = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction2.id, "user_id": user.id},
            headers=result["headers"],
        )

    assert rebook_resp.status_code == 400, rebook_resp.text
    assert "10 gün" in rebook_resp.json()["detail"]


@pytest.mark.asyncio
async def test_admin_cancel_does_not_trigger_user_restriction():
    """
    Admin iptal ettiğinde kullanıcının aynı kategoriden yeniden rezervasyon yapması
    engellenmemeli (kısıt sadece USER kaynaklı iptallerde aktif).
    """
    email = f"nodeny+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+904{uuid.uuid4().hex[:8]}"
    admin_email = f"admin+{uuid.uuid4().hex[:8]}@test.com"
    admin_phone = f"+905{uuid.uuid4().hex[:8]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    admin = await _create_user(email=admin_email, phone=admin_phone, password=password, role="ADMIN")
    studio = await _create_studio()
    category = await _create_service_category()

    auction1 = await _create_active_auction(studio_id=studio.id, service_category_id=category.id, title="Admin Cancel 1")
    auction2 = await _create_active_auction(studio_id=studio.id, service_category_id=category.id, title="Admin Cancel 2")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await _login_and_book(client, email, password, auction1.id, user.id)
        assert result["response"].status_code == 201
        reservation_id = result["response"].json()["id"]

        # Admin iptal ediyor
        admin_login = await client.post("/api/v1/auth/login", json={"email": admin_email, "password": password})
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        cancel_resp = await client.post(
            f"/api/v1/reservations/admin/{reservation_id}/cancel",
            headers=admin_headers,
        )
        assert cancel_resp.status_code == 200

        # Kullanıcı aynı kategori+stüdyodan tekrar booklama yapabilmeli
        rebook_resp = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction2.id, "user_id": user.id},
            headers=result["headers"],
        )

    assert rebook_resp.status_code == 201, rebook_resp.text


@pytest.mark.asyncio
async def test_user_book_then_rebook_same_sector_is_blocked():
    """
    Kullanıcı bir sektörde rezervasyon yaptıysa, 10 gün boyunca aynı sektördeki
    başka fırsatlara tekrar rezervasyon yapamamalı.
    """
    email = f"sectorblock+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+9055{uuid.uuid4().hex[:7]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    studio_a = await _create_studio()
    studio_b = await _create_studio()
    sector_x = await _create_sector()
    sector_y = await _create_sector()
    cat_a = await _create_service_category(sector_id=sector_x.id)
    cat_b = await _create_service_category(sector_id=sector_x.id)
    cat_c = await _create_service_category(sector_id=sector_y.id)

    auction_a = await _create_active_auction(studio_id=studio_a.id, service_category_id=cat_a.id, title="Sector X Auction 1")
    auction_b = await _create_active_auction(studio_id=studio_b.id, service_category_id=cat_b.id, title="Sector X Auction 2")
    auction_c = await _create_active_auction(studio_id=studio_b.id, service_category_id=cat_c.id, title="Sector Y Auction")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first_booking = await _login_and_book(client, email, password, auction_a.id, user.id)
        assert first_booking["response"].status_code == 201, first_booking["response"].text

        same_sector_resp = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction_b.id, "user_id": user.id},
            headers=first_booking["headers"],
        )
        assert same_sector_resp.status_code == 400, same_sector_resp.text
        assert "10 gun" in same_sector_resp.json()["detail"].lower() or "10 gün" in same_sector_resp.json()["detail"].lower()
        assert "sektor" in same_sector_resp.json()["detail"].lower() or "sektör" in same_sector_resp.json()["detail"].lower()

        different_sector_resp = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction_c.id, "user_id": user.id},
            headers=first_booking["headers"],
        )

    assert different_sector_resp.status_code == 201, different_sector_resp.text


@pytest.mark.asyncio
async def test_user_cancel_different_category_is_allowed():
    """
    Kullanıcı iptal ettiğinde FARKLI bir kategori için yeniden rezervasyon yapabilmeli.
    """
    email = f"diffcat+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+906{uuid.uuid4().hex[:8]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    studio = await _create_studio()
    cat_a = await _create_service_category()
    cat_b = await _create_service_category()

    auction_a = await _create_active_auction(studio_id=studio.id, service_category_id=cat_a.id, title="Cat A Auction")
    auction_b = await _create_active_auction(studio_id=studio.id, service_category_id=cat_b.id, title="Cat B Auction")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await _login_and_book(client, email, password, auction_a.id, user.id)
        assert result["response"].status_code == 201
        reservation_id = result["response"].json()["id"]

        # Kategori A'yı iptal et
        cancel_resp = await client.delete(
            f"/api/v1/reservations/{reservation_id}",
            headers=result["headers"],
        )
        assert cancel_resp.status_code == 204

        # Kategori B'den booklama yap — izin verilmeli
        rebook_resp = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction_b.id, "user_id": user.id},
            headers=result["headers"],
        )

    assert rebook_resp.status_code == 201, rebook_resp.text


@pytest.mark.asyncio
async def test_user_cancel_different_studio_is_allowed():
    """
    Kullanıcı iptal ettiğinde FARKLI bir stüdyodan (aynı kategori) rezervasyon yapabilmeli.
    """
    email = f"diffstudio+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+907{uuid.uuid4().hex[:8]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    studio_a = await _create_studio()
    studio_b = await _create_studio()
    category = await _create_service_category()

    auction_a = await _create_active_auction(studio_id=studio_a.id, service_category_id=category.id, title="Studio A Auction")
    auction_b = await _create_active_auction(studio_id=studio_b.id, service_category_id=category.id, title="Studio B Auction")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await _login_and_book(client, email, password, auction_a.id, user.id)
        assert result["response"].status_code == 201
        reservation_id = result["response"].json()["id"]

        # Stüdyo A'yı iptal et
        cancel_resp = await client.delete(
            f"/api/v1/reservations/{reservation_id}",
            headers=result["headers"],
        )
        assert cancel_resp.status_code == 204

        # Stüdyo B'den booklama yap — izin verilmeli
        rebook_resp = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction_b.id, "user_id": user.id},
            headers=result["headers"],
        )

    assert rebook_resp.status_code == 201, rebook_resp.text


@pytest.mark.asyncio
async def test_restriction_error_message_contains_10_days():
    """
    Kısıt hata mesajı '10 gün' ifadesini içermeli.
    """
    email = f"msgtest+{uuid.uuid4().hex[:8]}@test.com"
    phone = f"+908{uuid.uuid4().hex[:8]}"
    password = "Pass123!"

    user = await _create_user(email=email, phone=phone, password=password)
    studio = await _create_studio()
    category = await _create_service_category()

    auction1 = await _create_active_auction(studio_id=studio.id, service_category_id=category.id, title="Msg Test 1")
    auction2 = await _create_active_auction(studio_id=studio.id, service_category_id=category.id, title="Msg Test 2")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        result = await _login_and_book(client, email, password, auction1.id, user.id)
        reservation_id = result["response"].json()["id"]

        await client.delete(f"/api/v1/reservations/{reservation_id}", headers=result["headers"])

        rebook_resp = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction2.id, "user_id": user.id},
            headers=result["headers"],
        )

    assert rebook_resp.status_code == 400
    detail = rebook_resp.json()["detail"]
    assert "10 gün" in detail
    assert "iptal" in detail.lower()
