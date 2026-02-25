"""
Pytest configuration and global fixtures.

Handles DB connection and test lifecycle.
"""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def db_session():
    """Connect to DB before tests and disconnect after"""
    # Force connection for direct DB access in tests
    if not db.is_connected():
        await db.connect()
    
    yield
    
    # Cleanup after session
    # For function scope, we can check if we want to disconnect, 
    # but keeping it connected is usually fine until end of session.
    # However, to be safe and isolated:
    # await db.disconnect() 
    # But disconnecting every time might be slow. 
    # Let's just ensure it's connected.
    pass

@pytest.fixture
async def client() -> AsyncClient:
    """Async client fixture for making HTTP requests"""
    # Use ASGITransport to adapt the ASGI app for httpx
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
