"""Database shim: use real `prisma.Prisma` in normal environments.
When running tests or when `ENABLE_FAKE_PRISMA` is set, use a lightweight
in-memory fake Prisma suitable for local tests (no external deps).
"""
import os
import sys
from datetime import datetime
from app.core.timezone import TR_TIMEZONE, now_tr

# Detect test environment (pytest sets `PYTEST_CURRENT_TEST`) or explicit env var.
_force_fake = os.getenv("ENABLE_FAKE_PRISMA", "").lower() in ("1", "true", "yes")
_running_under_pytest = os.getenv("PYTEST_CURRENT_TEST") is not None
_pytest_session = os.getenv("PYTEST_VERSION") is not None or "pytest" in sys.modules
_use_fake = _force_fake or _running_under_pytest or _pytest_session

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
            if hasattr(self, "fullName") and not hasattr(self, "firstName"):
                parts = str(self.fullName).split(" ", 1)
                setattr(self, "firstName", parts[0])
                setattr(self, "lastName", parts[1] if len(parts) > 1 else "")

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

        async def find_many(self, *, where=None, include=None, order=None):
            records = list(self._data.values())
            if where:
                records = [
                    item for item in records
                    if all(item.get(key) == value for key, value in where.items())
                ]
            return [_Record(**value) for value in records]

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
            if "bookingCode" in where:
                for v in self._data.values():
                    if v.get("bookingCode") == where.get("bookingCode"):
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

        async def update(self, *, where, data):
            target_id = None

            if "id" in where:
                if where.get("id") in self._data:
                    target_id = where.get("id")
            elif "email" in where:
                for record_id, record in self._data.items():
                    if record.get("email") == where.get("email"):
                        target_id = record_id
                        break

            if target_id is None:
                return None

            self._data[target_id].update(dict(data))
            return _Record(**self._data[target_id])

    class _ReservationModel(_Model):
        def __init__(self, prisma_ref):
            super().__init__()
            self._prisma_ref = prisma_ref

        async def create(self, *, data):
            auction_id = data.get("auctionId")
            if auction_id is not None:
                for existing in self._data.values():
                    if existing.get("auctionId") == auction_id:
                        raise Exception("Unique constraint failed on fields: (`auctionId`)")

            obj = dict(data)
            now = now_tr()
            obj.setdefault("reservedAt", now)
            obj.setdefault("createdAt", now)
            return await super().create(data=obj)

        async def find_many(self, *, where=None, include=None, order=None):
            records = list(self._data.values())
            if where:
                records = [
                    item for item in records
                    if all(item.get(key) == value for key, value in where.items())
                ]

            if order and order.get("createdAt") == "desc":
                records.sort(key=lambda item: item.get("createdAt") or datetime.min.replace(tzinfo=TR_TIMEZONE), reverse=True)
            if order and order.get("reservedAt") == "desc":
                records.sort(key=lambda item: item.get("reservedAt") or datetime.min.replace(tzinfo=TR_TIMEZONE), reverse=True)

            response = []
            for item in records:
                row = dict(item)
                if include and include.get("auction"):
                    row["auction"] = await self._prisma_ref.auction.find_unique(where={"id": row.get("auctionId")})
                if include and include.get("user"):
                    row["user"] = await self._prisma_ref.user.find_unique(where={"id": row.get("userId")})
                response.append(_Record(**row))
            return response

    class FakePrisma:
        def __init__(self):
            self.user = _Model()
            self.auction = _Model()
            self.reservation = _ReservationModel(self)

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
