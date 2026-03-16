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


async def create_studio(name_prefix: str):
    return await db.db.studio.create(
        data={
            "name": f"{name_prefix} {uuid.uuid4().hex[:6]}",
            "address": "Tenant Test Address",
        }
    )


async def create_user(email_prefix: str, role: str, studio_id: int | None = None):
    password = "AdminPass123!"
    user = await db.db.user.create(
        data={
            "email": f"{email_prefix}+{uuid.uuid4().hex[:8]}@example.com",
            "phone": f"+905{uuid.uuid4().int % 1000000000:09d}",
            "fullName": f"{role} User",
            "hashedPassword": security.get_password_hash(password),
            "role": role,
            "gender": "FEMALE",
            "isVerified": True,
            "studioId": studio_id,
        }
    )
    return user, password


async def create_auction(studio_id: int, title: str):
    now = datetime.now(timezone.utc)
    return await db.db.auction.create(
        data={
            "title": title,
            "description": "Reservation tenant isolation test",
            "allowedGender": "ANY",
            "startPrice": "100.00",
            "floorPrice": "50.00",
            "currentPrice": "95.00",
            "startTime": now - timedelta(minutes=30),
            "endTime": now + timedelta(hours=1),
            "scheduledAt": now + timedelta(hours=2),
            "dropIntervalMins": 30,
            "dropAmount": "5.00",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": "0.00",
            "turboIntervalMins": 10,
            "status": "SOLD",
            "studioId": studio_id,
        }
    )


async def create_reservation(auction_id: int, user_id: int, code_prefix: str):
    return await db.db.reservation.create(
        data={
            "auctionId": auction_id,
            "userId": user_id,
            "lockedPrice": "95.00",
            "bookingCode": f"{code_prefix}-{uuid.uuid4().hex[:6]}",
            "status": "COMPLETED",
        }
    )


@pytest.mark.asyncio
async def test_admin_reservations_are_scoped_to_own_studio():
    studio_a = await create_studio("Studio A")
    studio_b = await create_studio("Studio B")

    admin_a, admin_password = await create_user("admin-a", "ADMIN", studio_a.id)
    guest, _ = await create_user("guest", "USER")

    auction_a = await create_auction(studio_a.id, "Studio A Auction")
    auction_b = await create_auction(studio_b.id, "Studio B Auction")

    reservation_a = await create_reservation(auction_a.id, guest.id, "RESA")
    await create_reservation(auction_b.id, guest.id, "RESB")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_a.email, "password": admin_password},
        )
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        all_response = await client.get("/api/v1/reservations/admin/all", headers=headers)
        assert all_response.status_code == 200, all_response.text
        items = all_response.json()
        assert len(items) == 1
        assert items[0]["id"] == reservation_a.id
        assert items[0]["studio_id"] == studio_a.id

        detail_response = await client.get(f"/api/v1/reservations/admin/{reservation_a.id}", headers=headers)
        assert detail_response.status_code == 200, detail_response.text
        assert detail_response.json()["id"] == reservation_a.id


@pytest.mark.asyncio
async def test_admin_cannot_access_other_studio_reservation_detail():
    studio_a = await create_studio("Studio A")
    studio_b = await create_studio("Studio B")

    admin_a, admin_password = await create_user("admin-a", "ADMIN", studio_a.id)
    guest, _ = await create_user("guest", "USER")

    auction_b = await create_auction(studio_b.id, "Studio B Auction")
    reservation_b = await create_reservation(auction_b.id, guest.id, "RESB")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_a.email, "password": admin_password},
        )
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        detail_response = await client.get(f"/api/v1/reservations/admin/{reservation_b.id}", headers=headers)
        assert detail_response.status_code == 404, detail_response.text


@pytest.mark.asyncio
async def test_admin_cannot_cancel_or_check_in_other_studio_reservation():
    studio_a = await create_studio("Studio A")
    studio_b = await create_studio("Studio B")

    admin_a, admin_password = await create_user("admin-a", "ADMIN", studio_a.id)
    guest, _ = await create_user("guest", "USER")

    auction_b = await create_auction(studio_b.id, "Studio B Auction")
    reservation_b = await create_reservation(auction_b.id, guest.id, "RESB")
    await db.db.reservation.update(
        where={"id": reservation_b.id},
        data={"status": "PENDING_ON_SITE"},
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_a.email, "password": admin_password},
        )
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        cancel_response = await client.post(f"/api/v1/reservations/admin/{reservation_b.id}/cancel", headers=headers)
        assert cancel_response.status_code == 403, cancel_response.text

        checkin_response = await client.post(f"/api/v1/reservations/admin/{reservation_b.id}/check-in", headers=headers)
        assert checkin_response.status_code == 403, checkin_response.text


@pytest.mark.asyncio
async def test_admin_can_cancel_and_check_in_own_studio_reservation():
    studio_a = await create_studio("Studio A")

    admin_a, admin_password = await create_user("admin-a", "ADMIN", studio_a.id)
    guest, _ = await create_user("guest", "USER")

    auction_a = await create_auction(studio_a.id, "Studio A Auction")
    reservation_a = await create_reservation(auction_a.id, guest.id, "RESA")
    await db.db.reservation.update(
        where={"id": reservation_a.id},
        data={"status": "PENDING_ON_SITE"},
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_a.email, "password": admin_password},
        )
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        checkin_response = await client.post(f"/api/v1/reservations/admin/{reservation_a.id}/check-in", headers=headers)
        assert checkin_response.status_code == 200, checkin_response.text
        assert checkin_response.json()["status"] == "COMPLETED"

        await db.db.reservation.update(
            where={"id": reservation_a.id},
            data={"status": "PENDING_ON_SITE"},
        )

        cancel_response = await client.post(f"/api/v1/reservations/admin/{reservation_a.id}/cancel", headers=headers)
        assert cancel_response.status_code == 200, cancel_response.text
        assert cancel_response.json()["status"] == "CANCELLED"