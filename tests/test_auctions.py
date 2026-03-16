import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta, timezone
from app.main import app
from app.core import db
from app.core import security
from app.core.timezone import now_tr


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()
    yield
    if db.db.is_connected():
        await db.db.disconnect()


async def create_user_in_db(
    email: str,
    phone: str,
    full_name: str,
    password: str,
    role: str = "USER",
    gender: str = "FEMALE",
    studio_id: int | None = None,
):
    hashed = security.get_password_hash(password)
    return await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": full_name,
            "hashedPassword": hashed,
            "role": role,
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


async def create_studio_in_db(name: str | None = None):
    return await db.db.studio.create(
        data={
            "name": name or f"Studio {uuid.uuid4().hex[:6]}",
            "address": "123 Test Street",
        }
    )


async def assign_sector_to_studio(studio_id: int, sector_id: int):
    return await db.db.studiosector.create(
        data={
            "studioId": studio_id,
            "sectorId": sector_id,
            "assignedAt": now_tr(),
        }
    )


@pytest.mark.asyncio
async def test_admin_can_create_auction():
    email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    # Use future dates for auction
    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=1)).isoformat()
    end_time = (now + timedelta(hours=3)).isoformat()

    payload = {
        "title": "Test Auction",
        "description": "Testing auction create",
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
        assert data.get("title") == payload["title"]

        # List auctions and ensure the created one is present
        r3 = await client.get("/api/v1/auctions/")
        assert r3.status_code == 200
        items = r3.json()
        assert any(item.get("id") == created_id for item in items)

    # Cleanup
    if created_id:
        await delete_auction_in_db(created_id)
    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_non_admin_cannot_create_auction():
    # Create a regular user via DB
    email = f"user+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+200{uuid.uuid4().hex[:7]}"
    password = "UserPass123!"

    await create_user_in_db(email, phone, "Regular User", password, role="USER")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login
        r2 = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r2.status_code == 200, r2.text
        token = r2.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to create auction
        payload = {
            "title": "Should Fail",
            "description": "Non-admin create",
            "start_price": "50.00",
            "floor_price": "5.00",
            "start_time": "2026-02-11T10:00:00Z",
            "end_time": "2026-02-11T11:00:00Z",
        }
        r3 = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert r3.status_code == 403

    # Cleanup user
    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_admin_can_create_auction_with_service_category():
    email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    service_sector = await db.db.sector.create(
        data={
            "name": "Güzellik",
            "slug": f"guzellik-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )
    service_category = await db.db.servicecategory.create(
        data={
            "name": "Cilt Bakımı",
            "slug": f"cilt-bakimi-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": service_sector.id,
        }
    )

    now = datetime.now(timezone.utc)
    start_time = (now + timedelta(hours=1)).isoformat()
    end_time = (now + timedelta(hours=3)).isoformat()

    payload = {
        "title": "Test Auction",
        "description": "Testing auction create",
        "start_price": "100.00",
        "floor_price": "10.00",
        "start_time": start_time,
        "end_time": end_time,
        "drop_interval_mins": 30,
        "drop_amount": "5.00",
        "serviceCategoryId": service_category.id,
    }

    await create_user_in_db(email, phone, "Admin User", password, role="ADMIN")
    created_id = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r2 = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert r2.status_code == 201, r2.text
        data = r2.json()
        created_id = data.get("id")
        assert data.get("serviceCategoryId") == service_category.id

    if created_id:
        await delete_auction_in_db(created_id)
    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_admin_with_studio_can_only_create_auction_for_own_sector_category():
    email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    beauty = await db.db.sector.create(
        data={
            "name": "Güzellik",
            "slug": f"guzellik-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )
    fitness = await db.db.sector.create(
        data={
            "name": "Fitness",
            "slug": f"fitness-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )

    beauty_category = await db.db.servicecategory.create(
        data={
            "name": "Cilt Bakımı",
            "slug": f"cilt-bakimi-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": beauty.id,
        }
    )
    fitness_category = await db.db.servicecategory.create(
        data={
            "name": "Reformer Pilates",
            "slug": f"reformer-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": fitness.id,
        }
    )

    studio = await create_studio_in_db("Scoped Admin Studio")
    await assign_sector_to_studio(studio.id, beauty.id)
    await create_user_in_db(email, phone, "Scoped Admin", password, role="ADMIN", studio_id=studio.id)

    now = datetime.now(timezone.utc)
    base_payload = {
        "title": "Scoped Auction",
        "description": "Scoped category validation",
        "start_price": "100.00",
        "floor_price": "10.00",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=3)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "5.00",
    }
    created_id = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        allowed_response = await client.post(
            "/api/v1/auctions/",
            json={**base_payload, "serviceCategoryId": beauty_category.id},
            headers=headers,
        )
        assert allowed_response.status_code == 201, allowed_response.text
        created_id = allowed_response.json()["id"]

        blocked_response = await client.post(
            "/api/v1/auctions/",
            json={**base_payload, "title": "Blocked Scoped Auction", "serviceCategoryId": fitness_category.id},
            headers=headers,
        )
        assert blocked_response.status_code == 400, blocked_response.text
        assert "işletmenizin sektörleriyle eşleşmiyor" in blocked_response.json()["detail"]

    if created_id:
        await delete_auction_in_db(created_id)
    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_admin_with_studio_sectors_must_select_service_category():
    email = f"admin+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+100{uuid.uuid4().hex[:7]}"
    password = "AdminPass123!"

    beauty = await db.db.sector.create(
        data={
            "name": "Güzellik",
            "slug": f"guzellik-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )
    studio = await create_studio_in_db("Required Category Studio")
    await assign_sector_to_studio(studio.id, beauty.id)
    await create_user_in_db(email, phone, "Scoped Admin", password, role="ADMIN", studio_id=studio.id)

    now = datetime.now(timezone.utc)
    payload = {
        "title": "Scoped Auction Without Category",
        "description": "Scoped category requirement",
        "start_price": "100.00",
        "floor_price": "10.00",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=3)).isoformat(),
        "drop_interval_mins": 30,
        "drop_amount": "5.00",
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/auctions/", json=payload, headers=headers)
        assert response.status_code == 400, response.text
        assert "hizmet kategorisi seçmelisiniz" in response.json()["detail"]

    await delete_user_in_db(email)


@pytest.mark.asyncio
async def test_list_auctions_can_filter_by_sector_and_service_category():
    beauty = await db.db.sector.create(
        data={
            "name": "Güzellik",
            "slug": f"guzellik-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )
    fitness = await db.db.sector.create(
        data={
            "name": "Fitness",
            "slug": f"fitness-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )

    cilt_bakimi = await db.db.servicecategory.create(
        data={
            "name": "Cilt Bakımı",
            "slug": f"cilt-bakimi-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": beauty.id,
        }
    )
    reformer = await db.db.servicecategory.create(
        data={
            "name": "Reformer Pilates",
            "slug": f"reformer-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": fitness.id,
        }
    )

    beauty_studio = await create_studio_in_db("Beauty Studio")
    fitness_studio = await create_studio_in_db("Fitness Studio")

    await db.db.studiosector.create(data={"studioId": beauty_studio.id, "sectorId": beauty.id, "assignedAt": now_tr()})
    await db.db.studiosector.create(data={"studioId": fitness_studio.id, "sectorId": fitness.id, "assignedAt": now_tr()})

    now = datetime.now(timezone.utc)
    common_data = {
        "description": "Filter test",
        "allowedGender": "ANY",
        "startPrice": "100.00",
        "floorPrice": "50.00",
        "currentPrice": "100.00",
        "startTime": now - timedelta(minutes=30),
        "endTime": now + timedelta(hours=1),
        "scheduledAt": now + timedelta(hours=2),
        "dropIntervalMins": 30,
        "dropAmount": "5.00",
        "turboEnabled": False,
        "turboTriggerMins": 120,
        "turboDropAmount": "0.00",
        "turboIntervalMins": 10,
        "status": "ACTIVE",
    }

    beauty_auction = await db.db.auction.create(
        data={
            **common_data,
            "title": "Beauty Auction",
            "allowedGender": "FEMALE",
            "studioId": beauty_studio.id,
            "serviceCategoryId": cilt_bakimi.id,
        }
    )
    fitness_auction = await db.db.auction.create(
        data={
            **common_data,
            "title": "Fitness Auction",
            "allowedGender": "MALE",
            "studioId": fitness_studio.id,
            "serviceCategoryId": reformer.id,
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sector_response = await client.get("/api/v1/auctions/", params={"sector": beauty.slug})
        assert sector_response.status_code == 200, sector_response.text
        sector_items = sector_response.json()
        assert any(item["id"] == beauty_auction.id for item in sector_items)
        assert all(item["id"] != fitness_auction.id for item in sector_items)

        category_response = await client.get("/api/v1/auctions/", params={"service_category": cilt_bakimi.slug})
        assert category_response.status_code == 200, category_response.text
        category_items = category_response.json()
        assert any(item["id"] == beauty_auction.id for item in category_items)
        assert all(item["id"] != fitness_auction.id for item in category_items)

        allowed_gender_response = await client.get("/api/v1/auctions/", params={"allowed_gender": "FEMALE"})
        assert allowed_gender_response.status_code == 200, allowed_gender_response.text
        allowed_gender_items = allowed_gender_response.json()
        assert any(item["id"] == beauty_auction.id for item in allowed_gender_items)
        assert all(item["id"] != fitness_auction.id for item in allowed_gender_items)

        combined_response = await client.get(
            "/api/v1/auctions/",
            params={"sector": beauty.slug, "service_category": cilt_bakimi.slug, "allowed_gender": "FEMALE"},
        )
        assert combined_response.status_code == 200, combined_response.text
        combined_items = combined_response.json()
        assert len(combined_items) == 1
        assert combined_items[0]["id"] == beauty_auction.id


@pytest.mark.asyncio
async def test_get_auction_detail_includes_service_category_and_studio_sectors():
    wellness = await db.db.sector.create(
        data={
            "name": "Wellness",
            "slug": f"wellness-{uuid.uuid4().hex[:6]}",
            "isActive": True,
        }
    )
    category = await db.db.servicecategory.create(
        data={
            "name": "Reformer Pilates",
            "slug": f"reformer-{uuid.uuid4().hex[:6]}",
            "isActive": True,
            "sectorId": wellness.id,
        }
    )
    studio = await create_studio_in_db("Detail Studio")
    await db.db.studiosector.create(data={"studioId": studio.id, "sectorId": wellness.id, "assignedAt": now_tr()})

    now = datetime.now(timezone.utc)
    auction = await db.db.auction.create(
        data={
            "title": "Detail Auction",
            "description": "Nested relation response test",
            "allowedGender": "ANY",
            "startPrice": "100.00",
            "floorPrice": "50.00",
            "currentPrice": "90.00",
            "startTime": now - timedelta(minutes=15),
            "endTime": now + timedelta(hours=1),
            "scheduledAt": now + timedelta(hours=2),
            "dropIntervalMins": 20,
            "dropAmount": "5.00",
            "turboEnabled": False,
            "turboTriggerMins": 120,
            "turboDropAmount": "0.00",
            "turboIntervalMins": 10,
            "status": "ACTIVE",
            "studioId": studio.id,
            "serviceCategoryId": category.id,
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/auctions/{auction.id}")

    assert response.status_code == 200, response.text
    payload = response.json()
    print("\nPAYLOAD", payload)
    assert payload["serviceCategoryId"] == category.id
    assert payload["serviceCategory"]["id"] == category.id
    assert payload["serviceCategory"]["sector"]["id"] == wellness.id
    assert payload["studio"]["id"] == studio.id
    assert len(payload["studio"]["sectors"]) == 1
    assert payload["studio"]["sectors"][0]["sector"]["id"] == wellness.id
