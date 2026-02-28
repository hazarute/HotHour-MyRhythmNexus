import uuid
import pytest
import pytest_asyncio
from decimal import Decimal
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


async def create_user(email: str, phone: str, password: str, full_name: str = "Booking User", gender: str = "FEMALE"):
    hashed_password = security.get_password_hash(password)
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": full_name,
            "hashedPassword": hashed_password,
            "role": "USER",
            "gender": gender,
            "isVerified": True,
        }
    )


async def create_active_auction(title: str = "Booking Auction", current_price: Decimal = Decimal("89.90")):
    now = datetime.now(timezone.utc)
    return await db.db.auction.create(
        data={
            "title": title,
            "description": "Integration test auction",
            "allowedGender": "ANY",
            "startPrice": Decimal("120.00"),
            "floorPrice": Decimal("60.00"),
            "currentPrice": current_price,
            "startTime": now - timedelta(minutes=5),
            "endTime": now + timedelta(minutes=55),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("2.50"),
            "status": "ACTIVE",
        }
    )


@pytest.mark.asyncio
async def test_user_can_book_active_auction():
    email = f"booker+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+900{uuid.uuid4().hex[:7]}"
    password = "BookPass123!"

    user = await create_user(email=email, phone=phone, password=password)
    auction = await create_active_auction(current_price=Decimal("79.90"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction.id, "user_id": user.id},
            headers=headers,
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["auction_id"] == auction.id
    assert body["user_id"] == user.id
    assert body["locked_price"] == "79.90"
    assert body["status"] == "PENDING_ON_SITE"
    assert body["booking_code"].startswith("HOT-")

    updated_auction = await db.db.auction.find_unique(where={"id": auction.id})
    assert updated_auction is not None
    assert str(updated_auction.status) == "SOLD"


@pytest.mark.asyncio
async def test_duplicate_booking_returns_conflict():
    email = f"booker+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+901{uuid.uuid4().hex[:7]}"
    password = "BookPass123!"

    user = await create_user(email=email, phone=phone, password=password)
    auction = await create_active_auction(title="Conflict Auction", current_price=Decimal("69.90"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        first = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction.id, "user_id": user.id},
            headers=headers,
        )
        assert first.status_code == 201, first.text

        second = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction.id, "user_id": user.id},
            headers=headers,
        )

    assert second.status_code == 409, second.text
    assert "already booked" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_gender_restricted_auction_blocks_ineligible_user():
    email = f"booker+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+902{uuid.uuid4().hex[:7]}"
    password = "BookPass123!"

    # Male user
    user = await create_user(email=email, phone=phone, password=password, gender="MALE")

    now = datetime.now(timezone.utc)
    auction = await db.db.auction.create(
        data={
            "title": "Women Only Session",
            "description": "Gender restricted session",
            "allowedGender": "FEMALE",
            "startPrice": Decimal("120.00"),
            "floorPrice": Decimal("60.00"),
            "currentPrice": Decimal("89.90"),
            "startTime": now - timedelta(minutes=5),
            "endTime": now + timedelta(minutes=55),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("2.50"),
            "status": "ACTIVE",
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction.id, "user_id": user.id},
            headers=headers,
        )

    assert response.status_code == 403, response.text
    assert "yalnızca kadın" in response.json()["detail"].lower()
