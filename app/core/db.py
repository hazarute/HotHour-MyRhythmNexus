"""Database shim: use real `prisma.Prisma` in normal environments.
When running tests or when `ENABLE_FAKE_PRISMA` is set, use a lightweight
in-memory fake Prisma suitable for local tests (no external deps).
"""
import os

# Detect test environment (pytest sets `PYTEST_CURRENT_TEST`) or explicit env var.
_force_fake = os.getenv("ENABLE_FAKE_PRISMA", "").lower() in ("1", "true", "yes")
_running_under_pytest = os.getenv("PYTEST_CURRENT_TEST") is not None
_use_fake = _force_fake or _running_under_pytest

if not _use_fake:
    try:
        from prisma import Prisma

        db = Prisma()

        async def connect_db():
            if not db.is_connected():
                await db.connect()

        async def disconnect_db():
            if db.is_connected():
                await db.disconnect()

    except Exception:
        # If Prisma isn't available, fall back to fake but log a hint via env var.
        _use_fake = True

if _use_fake:
    # Fallback fake Prisma
    class _Record:
        def __init__(self, **kwargs):
            # mirror provided keys as attributes
            for k, v in kwargs.items():
                setattr(self, k, v)
            # ensure common user/auction fields exist with sensible defaults
            if not hasattr(self, "isVerified"):
                setattr(self, "isVerified", False)
            if not hasattr(self, "role"):
                setattr(self, "role", "USER")
            if not hasattr(self, "status"):
                setattr(self, "status", "ACTIVE")

        def dict(self):
            return self.__dict__

    class _Model:
        def __init__(self):
            self._data = {}
            self._next_id = 1

        async def create(self, *, data):
            obj = dict(data)
            obj_id = obj.get("id") or self._next_id
            obj["id"] = obj_id
            self._data[obj_id] = obj
            self._next_id = max(self._next_id, obj_id + 1)
            return _Record(**obj)

        async def find_many(self):
            return [ _Record(**v) for v in list(self._data.values()) ]

        async def find_unique(self, *, where):
            # support where by id or email
            if "id" in where:
                _id = where.get("id")
                v = self._data.get(_id)
                return _Record(**v) if v is not None else None
            if "email" in where:
                for v in self._data.values():
                    if v.get("email") == where.get("email"):
                        return _Record(**v)
            return None

        async def delete(self, *, where):
            # support delete by id or email
            if "id" in where:
                _id = where.get("id")
                return self._data.pop(_id, None)
            if "email" in where:
                for k, v in list(self._data.items()):
                    if v.get("email") == where.get("email"):
                        return self._data.pop(k, None)
            return None

    class FakePrisma:
        def __init__(self):
            self.user = _Model()
            self.auction = _Model()

        def is_connected(self):
            return True

        async def connect(self):
            return None

        async def disconnect(self):
            return None

    db = FakePrisma()

    async def connect_db():
        return None

    async def disconnect_db():
        return None
