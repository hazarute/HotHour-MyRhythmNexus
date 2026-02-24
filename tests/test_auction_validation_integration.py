"""
Integration tests for Auction Validation with API Endpoints

Tests that validation rules are enforced correctly through the API.
"""

import uuid
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone
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


async def create_admin_user(email: str, phone: str, full_name: str, password: str):
    """Create admin user directly in DB for testing"""
    hashed = security.get_password_hash(password)
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": full_name,
            "hashedPassword": hashed,
            "role": "ADMIN",
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
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "10.00",
        "turbo_enabled": True,
        "turbo_drop_amount": "60.00",
        "turbo_interval_mins": 5,
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
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "5.00",
        "turbo_enabled": True,
        "turbo_drop_amount": "10.00",
        "turbo_interval_mins": 5,
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
