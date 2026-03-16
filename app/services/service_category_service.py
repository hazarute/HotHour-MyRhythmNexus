from app.core.db import db
from app.services.sector_service import sector_service
import logging


logger = logging.getLogger(__name__)


class ServiceCategoryService:
    async def list_service_categories(
        self,
        active_only: bool = True,
        sector_slug: str | None = None,
        sector_ids: list[int] | None = None,
    ):
        where = {"isActive": True} if active_only else {}

        if sector_slug:
            sector = await sector_service.get_sector_by_slug(sector_slug, active_only=active_only)
            if not sector:
                return []
            where["sectorId"] = sector.id
        elif sector_ids:
            where["sectorId"] = {"in": sorted(set(sector_ids))}

        try:
            categories = await db.servicecategory.find_many(
                where=where or None,
                include={"sector": True},
            )
            return sorted(categories, key=lambda category: (str(getattr(category, "name", "")).lower(), getattr(category, "id", 0)))
        except Exception as e:
            logger.error(f"Error listing service categories: {e}")
            raise

    async def get_service_category_by_id(self, service_category_id: int, active_only: bool = True):
        try:
            category = await db.servicecategory.find_unique(
                where={"id": service_category_id},
                include={"sector": True},
            )
            if active_only and category and not getattr(category, "isActive", False):
                return None
            return category
        except Exception as e:
            logger.error(f"Error fetching service category {service_category_id}: {e}")
            raise

    async def get_studio_sector_ids(self, studio_id: int) -> list[int]:
        try:
            studio_sectors = await db.studiosector.find_many(where={"studioId": studio_id})
            return sorted(
                {
                    getattr(studio_sector, "sectorId", None)
                    for studio_sector in studio_sectors
                    if getattr(studio_sector, "sectorId", None) is not None
                }
            )
        except Exception as e:
            logger.error(f"Error fetching sector links for studio {studio_id}: {e}")
            raise

    async def list_service_categories_for_studio(self, studio_id: int, active_only: bool = True):
        sector_ids = await self.get_studio_sector_ids(studio_id)
        if not sector_ids:
            return []
        return await self.list_service_categories(active_only=active_only, sector_ids=sector_ids)

    async def studio_requires_service_category(self, studio_id: int) -> bool:
        return len(await self.get_studio_sector_ids(studio_id)) > 0

    async def is_service_category_allowed_for_studio(
        self,
        studio_id: int,
        service_category_id: int,
        active_only: bool = True,
    ) -> bool:
        service_category = await self.get_service_category_by_id(service_category_id, active_only=active_only)
        if not service_category:
            return False

        sector_ids = await self.get_studio_sector_ids(studio_id)
        if not sector_ids:
            return False

        return getattr(service_category, "sectorId", None) in set(sector_ids)


service_category_service = ServiceCategoryService()