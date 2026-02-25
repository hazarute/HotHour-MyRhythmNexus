import pytest
from httpx import AsyncClient
from app.main import app
from app.core import security
from app.services.user_service import user_service
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_email_verification_flow(client: AsyncClient, db_session):
    """
    Test the full email verification flow:
    1. Register a new user
    2. specific verification token generation
    3. Verify email endpoint
    4. Check DB status
    """
    # 1. Register User
    user_data = {
        "email": "test_verify@example.com",
        "full_name": "Test Verify",
        "phone": "5551112233",
        "gender": "FEMALE",
        "password": "Password123!"
    }

    # Mock email sending to avoid actual network calls
    with patch("app.core.email.FastMail.send_message", new_callable=AsyncMock) as mock_send_email:
        # Register response
        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201, response.text
        
        # Check that background task was triggered (queued)
        # Note: BackgroundTasks in FastAPI execute after the response is sent. 
        # In TestClient/AsyncClient, they might not run automatically unless explicitly handled or if using a synchronization mechanism.
        # However, we are mainly testing the API logic here. Only valid registration triggers it.

    # 2. Check User status in DB (should be unverified initially)
    user = await user_service.get_user_by_email(user_data["email"])
    assert user is not None
    assert user.isVerified is False # Default should be false
    
    # 3. Generate a valid verification token 
    # (In real flow, this is sent via email. Here we generate it to test the verify endpoint)
    token = security.create_verification_token(user.email)
    
    # 4. Call Verify Endpoint with valid token
    verify_response = await client.get(f"/api/v1/auth/verify-email?token={token}")
    assert verify_response.status_code == 200
    assert verify_response.json()["message"] == "Email adresi başarıyla doğrulandı"
    
    # 5. Check DB status again (should be verified)
    # Re-fetch user
    updated_user = await user_service.get_user_by_email(user_data["email"])
    assert updated_user.isVerified is True

@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: AsyncClient):
    """Test verification with invalid token"""
    response = await client.get("/api/v1/auth/verify-email?token=invalid_token_string")
    assert response.status_code == 400
    assert "Geçersiz" in response.json()["detail"]

@pytest.mark.asyncio
async def test_verify_email_wrong_type_token(client: AsyncClient):
    """Test using an access token instead of verification token"""
    # Create an access token (type='access')
    access_token = security.create_access_token("some_user_id")
    
    response = await client.get(f"/api/v1/auth/verify-email?token={access_token}")
    assert response.status_code == 400
    assert "Geçersiz" in response.json()["detail"]

@pytest.mark.asyncio
async def test_verify_already_verified(client: AsyncClient):
    """Test verifying a user that is already verified"""
    # 1. Create a user manually or via register and verify
    user_data = {
        "email": "already_verified@example.com",
        "full_name": "Already Verified",
        "phone": "5559998877",
        "gender": "MALE",
        "password": "Password123!"
    }
    
    # Register
    with patch("app.core.email.FastMail.send_message", new_callable=AsyncMock):
        await client.post("/api/v1/auth/register", json=user_data)

    # Manually set verified
    await user_service.verify_user(user_data["email"])
    
    # Generate token
    token = security.create_verification_token(user_data["email"])
    
    # Try to verify again
    response = await client.get(f"/api/v1/auth/verify-email?token={token}")
    assert response.status_code == 200
    assert response.json()["message"] == "Email adresi zaten doğrulanmış"
