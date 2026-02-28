import uuid
from decimal import Decimal
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core import db, security
from app.services.booking_service import booking_service


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()
    yield
    if db.db.is_connected():
        await db.db.disconnect()


async def create_user(
    *,
    email: str,
    phone: str,
    password: str,
    full_name: str,
    role: str = "USER",
    gender: str = "FEMALE",
):
    hashed_password = security.get_password_hash(password)
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": full_name,
            "hashedPassword": hashed_password,
            "role": role,
            "gender": gender,
            "isVerified": True,
        }
    )


async def login_token(client: AsyncClient, email: str, password: str) -> str:
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_user_cancelled_reservation_creates_admin_notification():
    uid = uuid.uuid4().hex[:8]
    user_email = f"notify-user+{uid}@example.com"
    admin_email = f"notify-admin+{uid}@example.com"
    user_phone = f"+930{uuid.uuid4().hex[:7]}"
    admin_phone = f"+931{uuid.uuid4().hex[:7]}"
    user_password = "UserPass123!"
    admin_password = "AdminPass123!"

    user = await create_user(
        email=user_email,
        phone=user_phone,
        password=user_password,
        full_name="Notify User",
    )
    await create_user(
        email=admin_email,
        phone=admin_phone,
        password=admin_password,
        full_name="Notify Admin",
        role="ADMIN",
    )

    now = datetime.now(timezone.utc)
    auction = await db.db.auction.create(
        data={
            "title": f"Notif Test Auction {uid}",
            "description": "Notification cancellation flow",
            "allowedGender": "ANY",
            "startPrice": Decimal("120.00"),
            "floorPrice": Decimal("60.00"),
            "currentPrice": Decimal("89.90"),
            "startTime": now - timedelta(minutes=5),
            "endTime": now + timedelta(minutes=55),
            "scheduledAt": now + timedelta(minutes=30),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("2.50"),
            "status": "ACTIVE",
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_token = await login_token(client, user_email, user_password)
        admin_token = await login_token(client, admin_email, admin_password)

        book_response = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction.id, "user_id": user.id},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert book_response.status_code == 201, book_response.text
        reservation_id = book_response.json()["id"]

        cancel_response = await client.delete(
            f"/api/v1/reservations/{reservation_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert cancel_response.status_code == 204, cancel_response.text

        notifications_response = await client.get(
            "/api/v1/reservations/admin/notifications/cancellations?limit=20",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert notifications_response.status_code == 200, notifications_response.text
        payload = notifications_response.json()

    hit = next(
        (
            item for item in payload["notifications"]
            if item.get("reservation_id") == reservation_id
            and item.get("type") == "USER_CANCELLED_BY_CUSTOMER"
        ),
        None,
    )
    assert hit is not None


@pytest.mark.asyncio
async def test_no_show_auto_cancel_creates_admin_notification():
    uid = uuid.uuid4().hex[:8]
    user_email = f"auto-user+{uid}@example.com"
    admin_email = f"auto-admin+{uid}@example.com"
    user_phone = f"+940{uuid.uuid4().hex[:7]}"
    admin_phone = f"+941{uuid.uuid4().hex[:7]}"
    user_password = "UserPass123!"
    admin_password = "AdminPass123!"

    user = await create_user(
        email=user_email,
        phone=user_phone,
        password=user_password,
        full_name="Auto User",
    )
    await create_user(
        email=admin_email,
        phone=admin_phone,
        password=admin_password,
        full_name="Auto Admin",
        role="ADMIN",
    )

    now = datetime.now(timezone.utc)
    auction = await db.db.auction.create(
        data={
            "title": f"Auto No Show Auction {uid}",
            "description": "No show auto cancel flow",
            "allowedGender": "ANY",
            "startPrice": Decimal("150.00"),
            "floorPrice": Decimal("70.00"),
            "currentPrice": Decimal("99.90"),
            "startTime": now - timedelta(hours=1),
            "endTime": now + timedelta(hours=1),
            "scheduledAt": now - timedelta(minutes=1),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("2.50"),
            "status": "ACTIVE",
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_token = await login_token(client, user_email, user_password)
        admin_token = await login_token(client, admin_email, admin_password)

        book_response = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction.id, "user_id": user.id},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert book_response.status_code == 201, book_response.text
        reservation_id = book_response.json()["id"]

        cancelled_count = await booking_service.auto_cancel_overdue_pending_reservations()
        assert cancelled_count >= 1

        reservation = await db.db.reservation.find_unique(where={"id": reservation_id})
        assert reservation is not None
        assert str(reservation.status) == "CANCELLED"

        notifications_response = await client.get(
            "/api/v1/reservations/admin/notifications/cancellations?limit=20",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert notifications_response.status_code == 200, notifications_response.text
        payload = notifications_response.json()

    hit = next(
        (
            item for item in payload["notifications"]
            if item.get("reservation_id") == reservation_id
            and item.get("type") == "AUTO_CANCEL_NO_SHOW"
        ),
        None,
    )
    assert hit is not None


@pytest.mark.asyncio
async def test_admin_can_delete_single_notification_and_list_refills():
    uid = uuid.uuid4().hex[:8]
    user_email = f"delete-user+{uid}@example.com"
    admin_email = f"delete-admin+{uid}@example.com"
    user_phone = f"+950{uuid.uuid4().hex[:7]}"
    admin_phone = f"+951{uuid.uuid4().hex[:7]}"
    user_password = "UserPass123!"
    admin_password = "AdminPass123!"

    user = await create_user(
        email=user_email,
        phone=user_phone,
        password=user_password,
        full_name="Delete User",
    )
    await create_user(
        email=admin_email,
        phone=admin_phone,
        password=admin_password,
        full_name="Delete Admin",
        role="ADMIN",
    )

    now = datetime.now(timezone.utc)

    auction1 = await db.db.auction.create(
        data={
            "title": f"Delete Notif A {uid}",
            "description": "delete notif flow a",
            "allowedGender": "ANY",
            "startPrice": Decimal("120.00"),
            "floorPrice": Decimal("60.00"),
            "currentPrice": Decimal("89.90"),
            "startTime": now - timedelta(minutes=5),
            "endTime": now + timedelta(minutes=55),
            "scheduledAt": now + timedelta(minutes=30),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("2.50"),
            "status": "ACTIVE",
        }
    )
    auction2 = await db.db.auction.create(
        data={
            "title": f"Delete Notif B {uid}",
            "description": "delete notif flow b",
            "allowedGender": "ANY",
            "startPrice": Decimal("130.00"),
            "floorPrice": Decimal("65.00"),
            "currentPrice": Decimal("95.90"),
            "startTime": now - timedelta(minutes=5),
            "endTime": now + timedelta(minutes=55),
            "scheduledAt": now + timedelta(minutes=30),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("2.50"),
            "status": "ACTIVE",
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_token = await login_token(client, user_email, user_password)
        admin_token = await login_token(client, admin_email, admin_password)

        book_a = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction1.id, "user_id": user.id},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert book_a.status_code == 201, book_a.text
        reservation_a = book_a.json()["id"]

        cancel_a = await client.delete(
            f"/api/v1/reservations/{reservation_a}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert cancel_a.status_code == 204, cancel_a.text

        book_b = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction2.id, "user_id": user.id},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert book_b.status_code == 201, book_b.text
        reservation_b = book_b.json()["id"]

        cancel_b = await client.delete(
            f"/api/v1/reservations/{reservation_b}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert cancel_b.status_code == 204, cancel_b.text

        list_before = await client.get(
            "/api/v1/reservations/admin/notifications/cancellations?limit=20",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert list_before.status_code == 200, list_before.text
        payload_before = list_before.json()
        assert len(payload_before["notifications"]) >= 2

        target_notification_id = payload_before["notifications"][0]["id"]
        delete_response = await client.delete(
            f"/api/v1/reservations/admin/notifications/{target_notification_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert delete_response.status_code == 200, delete_response.text

        list_after = await client.get(
            "/api/v1/reservations/admin/notifications/cancellations?limit=20",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert list_after.status_code == 200, list_after.text
        payload_after = list_after.json()

    assert all(item["id"] != target_notification_id for item in payload_after["notifications"])


@pytest.mark.asyncio
async def test_admin_can_bulk_delete_read_notifications():
    uid = uuid.uuid4().hex[:8]
    user_email = f"bulk-user+{uid}@example.com"
    admin_email = f"bulk-admin+{uid}@example.com"
    user_phone = f"+960{uuid.uuid4().hex[:7]}"
    admin_phone = f"+961{uuid.uuid4().hex[:7]}"
    user_password = "UserPass123!"
    admin_password = "AdminPass123!"

    user = await create_user(
        email=user_email,
        phone=user_phone,
        password=user_password,
        full_name="Bulk User",
    )
    await create_user(
        email=admin_email,
        phone=admin_phone,
        password=admin_password,
        full_name="Bulk Admin",
        role="ADMIN",
    )

    now = datetime.now(timezone.utc)
    auction = await db.db.auction.create(
        data={
            "title": f"Bulk Clear Auction {uid}",
            "description": "bulk clear flow",
            "allowedGender": "ANY",
            "startPrice": Decimal("120.00"),
            "floorPrice": Decimal("60.00"),
            "currentPrice": Decimal("89.90"),
            "startTime": now - timedelta(minutes=5),
            "endTime": now + timedelta(minutes=55),
            "scheduledAt": now + timedelta(minutes=30),
            "dropIntervalMins": 5,
            "dropAmount": Decimal("2.50"),
            "status": "ACTIVE",
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_token = await login_token(client, user_email, user_password)
        admin_token = await login_token(client, admin_email, admin_password)

        book_response = await client.post(
            "/api/v1/reservations/book",
            json={"auction_id": auction.id, "user_id": user.id},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert book_response.status_code == 201, book_response.text
        reservation_id = book_response.json()["id"]

        cancel_response = await client.delete(
            f"/api/v1/reservations/{reservation_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert cancel_response.status_code == 204, cancel_response.text

        list_response = await client.get(
            "/api/v1/reservations/admin/notifications/cancellations?limit=20",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert list_response.status_code == 200, list_response.text
        notifications = list_response.json()["notifications"]
        assert notifications

        first_notification_id = notifications[0]["id"]
        read_response = await client.post(
            f"/api/v1/reservations/admin/notifications/{first_notification_id}/read",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert read_response.status_code == 200, read_response.text

        clear_response = await client.delete(
            "/api/v1/reservations/admin/notifications/read/all",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert clear_response.status_code == 200, clear_response.text
        assert clear_response.json().get("deleted_count", 0) >= 1

        list_after = await client.get(
            "/api/v1/reservations/admin/notifications/cancellations?limit=20",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert list_after.status_code == 200, list_after.text
        payload_after = list_after.json()

    assert all(item["id"] != first_notification_id for item in payload_after["notifications"])
