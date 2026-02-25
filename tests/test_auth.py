import uuid
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core import db


def test_register_and_login():
    email = f"test+{uuid.uuid4().hex[:8]}@example.com"
    phone_suffix = "".join([s for s in uuid.uuid4().hex if s.isdigit()][:9])
    if len(phone_suffix) < 9:
        phone_suffix = "123456789"
    phone = f"+905{phone_suffix}"
    password = "TestPass123!"
    payload = {
        "email": email,
        "full_name": "Test User",
        "phone": phone,
        "password": password,
        "gender": "MALE"
    }

    with TestClient(app) as client:
        # Register
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert "access_token" in data
        assert "user" in data
        user_data = data["user"]
        assert user_data.get("email") == email
        assert "id" in user_data

        # Login
        r2 = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r2.status_code == 200, r2.text
        token_data = r2.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert "access_token" in token_data

    # Cleanup - remove created user
    async def _cleanup():
        if not db.db.is_connected():
            await db.db.connect()
        try:
            await db.db.user.delete(where={"email": email})
        except Exception:
            pass

    asyncio.run(_cleanup())
