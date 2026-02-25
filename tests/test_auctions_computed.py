import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta, timezone
from app.main import app
from app.core import db
from app.core import security
from decimal import Decimal


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()
    yield
    if db.db.is_connected():
        await db.db.disconnect()


async def create_user_in_db(email: str, phone: str, full_name: str, password: str, role: str = "USER", gender: str = "FEMALE"):
    hashed = security.get_password_hash(password)
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": full_name,
            "hashedPassword": hashed,
            "role": role,
            "gender": gender,
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
async def test_list_auctions_includes_computed_price():
    email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    # Use future dates for auction
    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=1)).isoformat()
    end_time = (now + timedelta(hours=3)).isoformat()

    payload = {
        "title": "Computed Auction",
        "description": "Testing computed price",
        "start_price": "100.00",
        "floor_price": "10.00",
        "start_time": start_time,
        "end_time": end_time,
        "drop_interval_mins": 30,
        "drop_amount": "5.00",
    }

    # create admin user directly in DB
    await create_user_in_db(email, phone, "Admin User", password, role="ADMIN")
    created_id = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as admin
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create auction
        r2 = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert r2.status_code == 201, r2.text
        data = r2.json()
        created_id = data.get("id")

        # List auctions with computed prices
        r3 = await client.get("/api/v1/auctions/?include_computed=true")
        assert r3.status_code == 200
        items = r3.json()
        # find created
        found = next((i for i in items if i.get("id") == created_id), None)
        assert found is not None
        assert "computedPrice" in found
        # ensure computedPrice is parseable as Decimal
        Decimal(found.get("computedPrice"))

    # Cleanup
    if created_id:
        await delete_auction_in_db(created_id)
    await delete_user_in_db(email)
