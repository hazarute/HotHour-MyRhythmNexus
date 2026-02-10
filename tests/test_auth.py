import uuid
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core import db


def test_register_and_login():
    email = f"test+{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+999{uuid.uuid4().hex[:7]}"
    password = "TestPass123!"
    payload = {
        "email": email,
        "full_name": "Test User",
        "phone": phone,
        "password": password,
    }

    with TestClient(app) as client:
        # Register
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert data.get("email") == email
        assert "id" in data

        # Login
        r2 = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r2.status_code == 200, r2.text
        token_data = r2.json()
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
