"""
Pytest configuration and global fixtures.

Handles DB connection and test lifecycle.
"""

import asyncio
from app.core.db import db


# Note: DB connection is managed at test session start via lifespan hook
# in app.main and through manual connection in tests.
# No special pytest fixtures needed - tests either use TestClient (which handles lifecycle)
# or explicit await db.connect() for direct async operations.

# For sync tests using TestClient, the app's lifespan hook in main.py handles connection
# For cleanup, tests manually call asyncio.run(db.connect()) and then delete their data



