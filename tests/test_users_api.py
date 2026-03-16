import uuid
import pytest
import pytest_asyncio
from typing import Any, cast
from unittest.mock import AsyncMock, patch
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


def record_attr(record: Any, field_name: str):
    return getattr(cast(Any, record), field_name)

async def get_token_headers(user):
    token = security.create_access_token(subject=record_attr(user, "id"))
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_get_all_users_as_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    headers = await get_token_headers(admin_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users", headers=headers)
        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify passwords aren't dumped
        admin_in_list = next((u for u in data if u["id"] == record_attr(admin_user, "id")), None)
        assert admin_in_list is not None
        assert "hashedPassword" not in admin_in_list
        assert admin_in_list["email"] == record_attr(admin_user, "email")

@pytest.mark.asyncio
async def test_get_all_users_as_normal_user():
    normal_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(normal_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users", headers=headers)
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_user_as_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)
    
    update_data = {
        "full_name": "Updated User Name",
        "phone": record_attr(target_user, "phone"),
        "gender": "MALE"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(f"/api/v1/users/{record_attr(target_user, 'id')}", json=update_data, headers=headers)
        assert response.status_code == 200, f"Error: {response.text}"
        json_data = response.json()
        assert json_data["fullName"] == "Updated User Name"
        assert json_data["gender"] == "MALE"
        
        check_user = await db.db.user.find_unique(where={"id": record_attr(target_user, "id")})
        assert check_user is not None
        assert record_attr(check_user, "fullName") == "Updated User Name"
        assert record_attr(check_user, "gender") == "MALE"
        assert record_attr(check_user, "email") == record_attr(target_user, "email")

@pytest.mark.asyncio
async def test_update_user_rejects_email_change_payload():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)

    update_data = {
        "full_name": "Updated User Name",
        "email": "changed@example.com",
        "phone": record_attr(target_user, "phone"),
        "gender": "MALE"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(f"/api/v1/users/{record_attr(target_user, 'id')}", json=update_data, headers=headers)
        assert response.status_code == 422

        check_user = await db.db.user.find_unique(where={"id": record_attr(target_user, "id")})
        assert check_user is not None
        assert record_attr(check_user, "email") == record_attr(target_user, "email")

@pytest.mark.asyncio
async def test_update_user_as_normal():
    normal_user = await create_user_in_db(role="USER")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(normal_user)
    
    update_data = {
        "full_name": "Should not work",
        "phone": record_attr(target_user, "phone"),
        "gender": "MALE"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(f"/api/v1/users/{record_attr(target_user, 'id')}", json=update_data, headers=headers)
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_user_rejects_role_change_payload():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)

    update_data = {
        "full_name": "Updated User Name",
        "phone": record_attr(target_user, "phone"),
        "role": "ADMIN",
        "gender": "MALE"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(f"/api/v1/users/{record_attr(target_user, 'id')}", json=update_data, headers=headers)
        assert response.status_code == 422

        check_user = await db.db.user.find_unique(where={"id": record_attr(target_user, "id")})
        assert check_user is not None
        assert record_attr(check_user, "role") == "USER"

@pytest.mark.asyncio
async def test_admin_cannot_update_other_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    other_admin = await create_user_in_db(role="ADMIN")
    headers = await get_token_headers(admin_user)

    update_data = {
        "full_name": "Blocked Update",
        "phone": record_attr(other_admin, "phone"),
        "gender": "MALE"
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(f"/api/v1/users/{record_attr(other_admin, 'id')}", json=update_data, headers=headers)
        assert response.status_code == 403
        assert "Diğer admin kullanıcıların bilgileri düzenlenemez" in response.text

        check_user = await db.db.user.find_unique(where={"id": record_attr(other_admin, "id")})
        assert check_user is not None
        assert record_attr(check_user, "fullName") == record_attr(other_admin, "fullName")

@pytest.mark.asyncio
async def test_delete_user_as_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/users/{record_attr(target_user, 'id')}", headers=headers)
        assert response.status_code == 403
        
        check_user = await db.db.user.find_unique(where={"id": record_attr(target_user, "id")})
        assert check_user is not None

@pytest.mark.asyncio
async def test_admin_cannot_delete_self():
    admin_user = await create_user_in_db(role="ADMIN")
    headers = await get_token_headers(admin_user)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/users/{record_attr(admin_user, 'id')}", headers=headers)
        assert response.status_code == 403
        assert "Kullanıcı silme işlemi desteklenmiyor" in response.text

@pytest.mark.asyncio
async def test_admin_can_resend_verification_email_for_unverified_user():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)
    await db.db.user.update(where={"id": record_attr(target_user, "id")}, data={"isVerified": False})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("app.api.users.send_verification_email", new_callable=AsyncMock) as mock_send_email:
            response = await client.post(f"/api/v1/users/{record_attr(target_user, 'id')}/resend-verification", headers=headers)
            assert response.status_code == 200, response.text
            assert response.json()["detail"] == "Doğrulama e-postası yeniden gönderildi."
            mock_send_email.assert_awaited_once()

@pytest.mark.asyncio
async def test_admin_cannot_resend_verification_email_for_other_admin():
    admin_user = await create_user_in_db(role="ADMIN")
    other_admin = await create_user_in_db(role="ADMIN")
    headers = await get_token_headers(admin_user)
    await db.db.user.update(where={"id": record_attr(other_admin, "id")}, data={"isVerified": False})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(f"/api/v1/users/{record_attr(other_admin, 'id')}/resend-verification", headers=headers)
        assert response.status_code == 403
        assert "Diğer admin kullanıcılar için doğrulama işlemi yapılamaz" in response.text

@pytest.mark.asyncio
async def test_admin_cannot_resend_verification_email_for_verified_user():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(f"/api/v1/users/{record_attr(target_user, 'id')}/resend-verification", headers=headers)
        assert response.status_code == 400
        assert "zaten doğrulanmış" in response.text

@pytest.mark.asyncio
async def test_admin_can_reset_user_password_to_default_value():
    admin_user = await create_user_in_db(role="ADMIN")
    target_user = await create_user_in_db(role="USER")
    headers = await get_token_headers(admin_user)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(f"/api/v1/users/{record_attr(target_user, 'id')}/reset-password", headers=headers)
        assert response.status_code == 200, response.text
        assert response.json()["detail"] == "Kullanıcı şifresi varsayılan değere sıfırlandı."

        updated_user = await db.db.user.find_unique(where={"id": record_attr(target_user, "id")})
        assert updated_user is not None
        assert security.verify_password("sifredegistir", record_attr(updated_user, "hashedPassword"))

@pytest.mark.asyncio
async def test_admin_cannot_reset_other_admin_password():
    admin_user = await create_user_in_db(role="ADMIN")
    other_admin = await create_user_in_db(role="ADMIN")
    headers = await get_token_headers(admin_user)

    original_admin_password = record_attr(other_admin, "hashedPassword")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(f"/api/v1/users/{record_attr(other_admin, 'id')}/reset-password", headers=headers)
        assert response.status_code == 403
        assert "Diğer admin kullanıcıların şifresi sıfırlanamaz" in response.text

        updated_user = await db.db.user.find_unique(where={"id": record_attr(other_admin, "id")})
        assert updated_user is not None
        assert record_attr(updated_user, "hashedPassword") == original_admin_password
