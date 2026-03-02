import uuid
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core import security, db


def _random_email():
    return f"test+{uuid.uuid4().hex[:8]}@example.com"


def test_refresh_and_revoke_flow():
    email = _random_email()
    phone = "+905000000000"
    password = "TestPass123!"
    payload = {
        "email": email,
        "full_name": "Refresh Test",
        "phone": phone,
        "password": password,
        "gender": "FEMALE"
    }

    with TestClient(app) as client:
        # Register
        r = client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 201, r.text
        data = r.json()
        assert "refresh_token" in data
        refresh_token = data["refresh_token"]

        # Verify email so login allowed
        verification_token = security.create_verification_token(email)
        vr = client.get(f"/api/v1/auth/verify-email?token={verification_token}")
        assert vr.status_code == 200

        # Login - ensure we get refresh token
        login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200
        login_data = login.json()
        assert "refresh_token" in login_data
        rt = login_data["refresh_token"]

        # Use refresh endpoint to get new tokens
        refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
        assert refresh_resp.status_code == 200, refresh_resp.text
        new_data = refresh_resp.json()
        assert "access_token" in new_data
        assert "refresh_token" in new_data

        # Revoke the refresh token
        revoke_resp = client.post("/api/v1/auth/revoke", json={"refresh_token": new_data["refresh_token"]})
        assert revoke_resp.status_code == 200

        # After revocation, trying to refresh with same token should fail
        fail_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": new_data["refresh_token"]})
        assert fail_resp.status_code == 401

    # Cleanup
    async def _cleanup():
        if not db.db.is_connected():
            await db.db.connect()
        try:
            await db.db.user.delete(where={"email": email})
        except Exception:
            pass

    asyncio.run(_cleanup())
