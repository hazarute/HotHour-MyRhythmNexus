"""
Integration tests for Auction Validation with API Endpoints

Tests that validation rules are enforced correctly through the API.
"""

import uuid
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core import db, security


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()
    yield
    if db.db.is_connected():
        await db.db.disconnect()


async def create_admin_user(
    email: str,
    phone: str,
    full_name: str,
    password: str,
    gender: str = "FEMALE",
    studio_id: int | None = None,
):
    """Create admin user directly in DB for testing"""
    hashed = security.get_password_hash(password)
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": full_name,
            "hashedPassword": hashed,
            "role": "ADMIN",
            "gender": gender,
            "isVerified": True,
            "studioId": studio_id,
        }
    )


async def delete_user_in_db(email: str):
    try:
        await db.db.user.delete(where={"email": email})
    except Exception:
        pass


async def delete_auction_in_db(auction_id: int):
    try:
        await db.db.auction.delete(where={"id": auction_id})
    except Exception:
        pass


@pytest.mark.asyncio
async def test_create_valid_auction():
    """Valid auction creation should succeed"""
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    await create_admin_user(email, phone, "Admin User", password)

    now = datetime.now(timezone.utc)
    payload = {
        "title": "Valid Auction",
        "description": "This is a valid auction",
        "start_price": "100.00",
        "floor_price": "50.00",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "10.00",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r2 = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert r2.status_code == 201
        data = r2.json()
        assert data["title"] == "Valid Auction"
        # Status can be either DRAFT or ACTIVE depending on start_time
        assert data["status"] in ["DRAFT", "ACTIVE"]

    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_start_price_must_exceed_floor_price_api():
    """API should reject auction when start_price <= floor_price"""
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    await create_admin_user(email, phone, "Admin User", password)

    now = datetime.now(timezone.utc)
    payload = {
        "title": "Invalid Auction",
        "description": "Start price less than floor",
        "start_price": "50.00",
        "floor_price": "100.00",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "10.00",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r2 = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert r2.status_code == 400
        assert "greater than floor_price" in r2.json()["detail"]

    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_turbo_mode_validation_api():
    """API should validate turbo mode parameters"""
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    await create_admin_user(email, phone, "Admin User", password)

    now = datetime.now(timezone.utc)
    payload = {
        "title": "Invalid Turbo Auction",
        "description": "Invalid turbo mode",
        "start_price": "100.00",
        "floor_price": "50.00",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=5)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "10.00",
        "turbo_enabled": True,
        "turbo_drop_amount": "60.00",
        "turbo_interval_mins": 10,
        "turbo_trigger_mins": 120,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r2 = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert r2.status_code == 400
        assert "turbo_drop_amount" in r2.json()["detail"]

    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_valid_turbo_auction_api():
    """Valid auction with turbo mode should succeed"""
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    await create_admin_user(email, phone, "Admin User", password)

    now = datetime.now(timezone.utc)
    payload = {
        "title": "Turbo Auction",
        "description": "Valid turbo mode auction",
        "start_price": "100.00",
        "floor_price": "50.00",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=5)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "10.00",
        "turbo_enabled": True,
        "turbo_drop_amount": "5.00",
        "turbo_interval_mins": 10,
        "turbo_trigger_mins": 120,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r2 = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert r2.status_code == 201
        data = r2.json()
        assert data["title"] == "Turbo Auction"

    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_status_only_cancel_skips_full_turbo_duration_validation():
    """Status-only cancel should succeed even if legacy turbo timing is currently invalid by new rules."""
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    await create_admin_user(email, phone, "Admin User", password)

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=10)
    end_time = now + timedelta(minutes=110)  # < 180 mins total window

    created_auction = await db.db.auction.create(
        data={
            "title": "Legacy Turbo Active Auction",
            "description": "Status-only cancel regression",
            "allowedGender": "ANY",
            "startPrice": Decimal("500.00"),
            "floorPrice": Decimal("200.00"),
            "currentPrice": Decimal("480.00"),
            "startTime": start_time,
            "endTime": end_time,
            "scheduledAt": end_time,
            "dropIntervalMins": 30,
            "dropAmount": Decimal("20.00"),
            "turboEnabled": True,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("10.00"),
            "turboIntervalMins": 10,
            "status": "ACTIVE",
        }
    )
    auction_id = int(getattr(created_auction, "id"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        cancel_res = await client.put(
            f"/api/v1/auctions/{auction_id}",
            json={"status": "CANCELLED"},
            headers=headers,
        )

        assert cancel_res.status_code == 200, cancel_res.text
        assert cancel_res.json()["status"] == "CANCELLED"

    await delete_auction_in_db(auction_id)
    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_cancel_status_only_update_allows_legacy_uncategorized_studio_auction():
    email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    sector = await db.db.sector.create(
        data={
            "name": f"Guzellik {uuid.uuid4().hex[:4]}",
            "slug": f"guzellik-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )
    studio = await db.db.studio.create(
        data={
            "name": f"Studio {uuid.uuid4().hex[:6]}",
            "address": "123 Test Street",
        }
    )
    await db.db.studiosector.create(
        data={
            "studioId": studio.id,
            "sectorId": sector.id,
            "assignedAt": datetime.now(timezone.utc),
        }
    )
    await create_admin_user(
        email,
        phone,
        "Admin User",
        password,
        studio_id=studio.id,
    )

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=45)
    end_time = now + timedelta(minutes=45)
    created_auction = await db.db.auction.create(
        data={
            "title": "Legacy Uncategorized Auction",
            "description": "Status-only cancel should bypass category requirement",
            "allowedGender": "ANY",
            "startPrice": Decimal("300.00"),
            "floorPrice": Decimal("120.00"),
            "currentPrice": Decimal("260.00"),
            "startTime": start_time,
            "endTime": end_time,
            "scheduledAt": end_time,
            "dropIntervalMins": 15,
            "dropAmount": Decimal("15.00"),
            "turboEnabled": False,
            "status": "ACTIVE",
            "studioId": studio.id,
        }
    )
    auction_id = int(getattr(created_auction, "id"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        cancel_res = await client.put(
            f"/api/v1/auctions/{auction_id}",
            json={"status": "CANCELLED"},
            headers=headers,
        )

        assert cancel_res.status_code == 200, cancel_res.text
        assert cancel_res.json()["status"] == "CANCELLED"

    await delete_auction_in_db(auction_id)
    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_admin_can_update_existing_auction_after_studio_sector_changes_when_category_is_unchanged():
    email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    beauty = await db.db.sector.create(
        data={
            "name": f"Guzellik {uuid.uuid4().hex[:4]}",
            "slug": f"guzellik-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )
    fitness = await db.db.sector.create(
        data={
            "name": f"Fitness {uuid.uuid4().hex[:4]}",
            "slug": f"fitness-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )

    beauty_category = await db.db.servicecategory.create(
        data={
            "name": f"Cilt Bakimi {uuid.uuid4().hex[:4]}",
            "slug": f"cilt-bakimi-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": beauty.id,
        }
    )
    await db.db.servicecategory.create(
        data={
            "name": f"Pilates {uuid.uuid4().hex[:4]}",
            "slug": f"pilates-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": fitness.id,
        }
    )

    studio = await db.db.studio.create(
        data={
            "name": f"Studio {uuid.uuid4().hex[:6]}",
            "address": "123 Test Street",
        }
    )
    await db.db.studiosector.create(
        data={
            "studioId": studio.id,
            "sectorId": beauty.id,
            "assignedAt": datetime.now(timezone.utc),
        }
    )
    await create_admin_user(
        email,
        phone,
        "Admin User",
        password,
        studio_id=studio.id,
    )

    now = datetime.now(timezone.utc)
    start_time = now + timedelta(hours=2)
    end_time = now + timedelta(hours=5)
    created_auction = await db.db.auction.create(
        data={
            "title": "Historical Category Auction",
            "description": "Should remain manageable after sector change",
            "allowedGender": "ANY",
            "startPrice": Decimal("300.00"),
            "floorPrice": Decimal("150.00"),
            "currentPrice": Decimal("300.00"),
            "startTime": start_time,
            "endTime": end_time,
            "scheduledAt": end_time,
            "dropIntervalMins": 30,
            "dropAmount": Decimal("15.00"),
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": Decimal("0.00"),
            "turboIntervalMins": 10,
            "status": "DRAFT",
            "studioId": studio.id,
            "serviceCategoryId": beauty_category.id,
        }
    )

    await db.db.studiosector.delete_many(where={"studioId": studio.id})
    await db.db.studiosector.create(
        data={
            "studioId": studio.id,
            "sectorId": fitness.id,
            "assignedAt": datetime.now(timezone.utc),
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        update_res = await client.put(
            f"/api/v1/auctions/{created_auction.id}",
            json={
                "title": "Historical Category Auction Updated",
                "start_price": "280.00",
                "floor_price": "140.00",
                "drop_amount": "14.00",
                "drop_interval_mins": 30,
            },
            headers=headers,
        )

        assert update_res.status_code == 200, update_res.text
        payload = update_res.json()
        assert payload["title"] == "Historical Category Auction Updated"
        assert payload["serviceCategoryId"] == beauty_category.id

    await delete_auction_in_db(created_auction.id)
    await delete_user_in_db(email)
