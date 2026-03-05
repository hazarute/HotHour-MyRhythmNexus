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

async def create_user_in_db(role: str = "USER"):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    phone_suffix = "".join([s for s in uuid.uuid4().hex if s.isdigit()][:9])
    if len(phone_suffix) < 9:
        phone_suffix += "1" * (9 - len(phone_suffix))
    phone = f"+905{phone_suffix}"
    
    hashed = security.get_password_hash("TestPass123!")
    user = await db.db.user.create(
        data={
            "email": email,
            "phone": phone,
            "fullName": "Test Admin" if role == "ADMIN" else "Test User",
            "hashedPassword": hashed,
            "role": role,
            "gender": "FEMALE",
            "isVerified": True,
        }
    )
    return user

async def get_token_headers(user):
    token = security.create_access_token(subject=user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_get_all_users_as_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    headers = await get_token_headers(admin_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify passwords aren't dumped
        admin_in_list = next((u for u in data if u["id"] == admin_user.id), None)
        assert admin_in_list is not None
        assert "hashedPassword" not in admin_in_list
        assert admin_in_list["email"] == admin_user.email

@pytest.mark.asyncio
async def test_get_all_users_as_normal_user():
    normal_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(normal_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/", headers=headers)
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_user_as_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)
    
    update_data = {
        "full_name": "Updated User Name",
        "email": target_user.email,
        "phone": target_user.phone,
        "role": "USER",
        "gender": "MALE"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(f"/api/v1/users/{target_user.id}", json=update_data, headers=headers)
        assert response.status_code == 200, f"Error: {response.text}"
        json_data = response.json()
        assert json_data["fullName"] == "Updated User Name"
        assert json_data["gender"] == "MALE"
        
        check_user = await db.db.user.find_unique(where={"id": target_user.id})
        assert check_user.fullName == "Updated User Name"
        assert check_user.gender == "MALE"

@pytest.mark.asyncio
async def test_update_user_as_normal():
    normal_user = await create_user_in_db(role="USER")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(normal_user)
    
    update_data = {
        "full_name": "Should not work",
        "email": target_user.email,
        "phone": target_user.phone,
        "role": "USER",
        "gender": "MALE"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(f"/api/v1/users/{target_user.id}", json=update_data, headers=headers)
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_user_as_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/users/{target_user.id}", headers=headers)
        assert response.status_code == 200
        
        # Verify deletion from DB
        check_user = await db.db.user.find_unique(where={"id": target_user.id})
        assert check_user is None

@pytest.mark.asyncio
async def test_admin_cannot_delete_self():
    admin_user = await create_user_in_db(role="ADMIN")
    headers = await get_token_headers(admin_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/users/{admin_user.id}", headers=headers)
        assert response.status_code == 400
        assert "Kendinizi silemezsiniz" in response.text
