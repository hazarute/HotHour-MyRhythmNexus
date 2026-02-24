import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core import db, security
from app.main import app


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()
    yield
    if db.db.is_connected():
        await db.db.disconnect()


async def create_user(email: str, phone: str, password: str, role: str = "USER"):
    hashed_password = security.get_password_hash(password)
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": "E2E User",
            "hashedPassword": hashed_password,
            "role": role,
        }
    )


@pytest.mark.asyncio
async def test_e2e_login_view_book_flow():
    admin_email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    user_email = f"user+{uuid.uuid4().hex[:8]}@example.com"
    admin_password = "AdminPass123!"
    user_password = "UserPass123!"

    admin = await create_user(
        email=admin_email,
        phone=f"+700{uuid.uuid4().hex[:7]}",
        password=admin_password,
        role="ADMIN",
    )
    user = await create_user(
        email=user_email,
        phone=f"+701{uuid.uuid4().hex[:7]}",
        password=user_password,
        role="USER",
    )

    now = datetime.now(timezone.utc)
    auction_payload = {
        "title": "E2E Auction Session",
        "description": "End-to-end flow test",
        "start_price": "120.00",
        "floor_price": "80.00",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "drop_interval_mins": 15,
        "drop_amount": "5.00",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        admin_login = await client.post(
            "/api/v1/auth/login", json={"email": admin_email, "password": admin_password}
        )
        assert admin_login.status_code == 200, admin_login.text
        admin_token = admin_login.json()["access_token"]

        create_auction = await client.post(
            "/api/v1/auctions/",
            json=auction_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_auction.status_code == 201, create_auction.text
        auction_id = create_auction.json()["id"]

        await db.db.auction.update(
            where={"id": auction_id},
            data={"status": "ACTIVE"},
        )

        user_login = await client.post(
            "/api/v1/auth/login", json={"email": user_email, "password": user_password}
        )
        assert user_login.status_code == 200, user_login.text
        user_token = user_login.json()["access_token"]

        auctions = await client.get("/api/v1/auctions/")
        assert auctions.status_code == 200, auctions.text
        auction_items = auctions.json()
        assert any(item["id"] == auction_id for item in auction_items)

        book = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction_id, "user_id": user.id},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert book.status_code == 201, book.text
        booking_data = book.json()

    assert booking_data["auction_id"] == auction_id
    assert booking_data["user_id"] == user.id
    assert booking_data["status"] == "PENDING_ON_SITE"
    assert booking_data["booking_code"].startswith("HOT-")
