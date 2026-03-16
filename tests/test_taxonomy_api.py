import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core import db


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connect():
    if not db.db.is_connected():
        await db.db.connect()

    await db.db.sector.delete_many()
    await db.db.servicecategory.delete_many()

    yield

    await db.db.servicecategory.delete_many()
    await db.db.sector.delete_many()


@pytest.mark.asyncio
async def test_list_sectors_returns_only_active_by_default():
    await db.db.sector.create(
        data={
            "name": "Güzellik",
            "slug": "guzellik",
            "description": "Bakım ve güzellik hizmetleri",
            "isActive": True,
        }
    )
    await db.db.sector.create(
        data={
            "name": "Arşiv",
            "slug": "arsiv",
            "description": "Pasif sektör",
            "isActive": False,
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/sectors")

    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items) == 1
    assert items[0]["slug"] == "guzellik"


@pytest.mark.asyncio
async def test_list_service_categories_can_filter_by_sector_slug():
    beauty = await db.db.sector.create(
        data={
            "name": "Güzellik",
            "slug": "guzellik",
            "isActive": True,
        }
    )
    fitness = await db.db.sector.create(
        data={
            "name": "Fitness",
            "slug": "fitness",
            "isActive": True,
        }
    )

    await db.db.servicecategory.create(
        data={
            "name": "Cilt Bakımı",
            "slug": "cilt-bakimi",
            "isActive": True,
            "sectorId": beauty.id,
        }
    )
    await db.db.servicecategory.create(
        data={
            "name": "Reformer Pilates",
            "slug": "reformer-pilates",
            "isActive": True,
            "sectorId": fitness.id,
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/service-categories", params={"sector_slug": "guzellik"})

    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items) == 1
    assert items[0]["slug"] == "cilt-bakimi"