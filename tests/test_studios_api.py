import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core import db
from app.core import security

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()
    yield

async def create_studio_in_db():
    name = f"Test Studio {uuid.uuid4().hex[:6]}"
    studio = await db.db.studio.create(
        data={
            "name": name,
            "address": "123 Test Street",
            "logoUrl": "https://example.com/logo.png",
            "googleMapsUrl": "https://maps.example.com/test",
        }
    )
    return studio

async def create_user_in_db(role: str = "USER", studio_id: str = None):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    phone_suffix = "".join([s for s in uuid.uuid4().hex if s.isdigit()][:9])
    if len(phone_suffix) < 9:
        phone_suffix += "1" * (9 - len(phone_suffix))
    phone = f"+905{phone_suffix}"

    hashed = security.get_password_hash("TestPass123!")
    user_data = {
        "email": email,
        "phone": phone,
        "fullName": "Test Admin" if role == "ADMIN" else "Test User",
        "hashedPassword": hashed,
        "role": role,
        "gender": "FEMALE",
        "isVerified": True,
    }
    
    if studio_id:
        user_data["studioId"] = studio_id

    user = await db.db.user.create(data=user_data)
    return user

async def get_token_headers(user):
    token = security.create_access_token(subject=user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_get_my_studio_as_admin_with_studio():
    studio = await create_studio_in_db()
    admin_user = await create_user_in_db(role="ADMIN", studio_id=studio.id)
    headers = await get_token_headers(admin_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/studios/me", headers=headers)
        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        assert data["id"] == studio.id
        assert data["name"] == studio.name
        assert data["address"] == studio.address

@pytest.mark.asyncio
async def test_get_my_studio_as_admin_without_studio():
    admin_user = await create_user_in_db(role="ADMIN", studio_id=None)
    headers = await get_token_headers(admin_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/studios/me", headers=headers)
        assert response.status_code == 404
        assert "yok" in response.text.lower() or "bulunamad" in response.text.lower()

@pytest.mark.asyncio
async def test_get_my_studio_as_normal_user():
    studio = await create_studio_in_db()
    normal_user = await create_user_in_db(role="USER", studio_id=studio.id)
    headers = await get_token_headers(normal_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/studios/me", headers=headers)
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_my_studio_as_admin():
    studio = await create_studio_in_db()
    admin_user = await create_user_in_db(role="ADMIN", studio_id=studio.id)
    headers = await get_token_headers(admin_user)

    update_data = {
        "name": "Updated Studio Name",
        "address": "456 Updated Ave",
        "logoUrl": "https://example.com/updated.png"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/api/v1/studios/me", json=update_data, headers=headers)
        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        assert data["name"] == "Updated Studio Name"
        assert data["address"] == "456 Updated Ave"
        assert data["logoUrl"] == "https://example.com/updated.png"

        # Verify DB
        updated_studio = await db.db.studio.find_unique(where={"id": studio.id})
        assert updated_studio.name == "Updated Studio Name"
        assert updated_studio.address == "456 Updated Ave"
        assert updated_studio.logoUrl == "https://example.com/updated.png"

@pytest.mark.asyncio
async def test_update_my_studio_as_admin_without_studio():
    admin_user = await create_user_in_db(role="ADMIN", studio_id=None)
    headers = await get_token_headers(admin_user)

    update_data = {
        "name": "Should not work",
        "address": "No address"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/api/v1/studios/me", json=update_data, headers=headers)
        assert response.status_code == 403
        assert "yok" in response.text.lower() or "olmad"  in response.text.lower()
