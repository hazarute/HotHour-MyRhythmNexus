from app.core.db import db
import logging


logger = logging.getLogger(__name__)


class SectorService:
    async def list_sectors(self, active_only: bool = True):
        where = {"isActive": True} if active_only else None

        try:
            sectors = await db.sector.find_many(where=where)
            return sorted(sectors, key=lambda sector: (str(getattr(sector, "name", "")).lower(), getattr(sector, "id", 0)))
        except Exception as e:
            logger.error(f"Error listing sectors: {e}")
            raise

    async def get_sector_by_slug(self, slug: str, active_only: bool = True):
        where = {"slug": slug}
        if active_only:
            where["isActive"] = True

        try:
            return await db.sector.find_unique(where=where)
        except Exception as e:
            logger.error(f"Error fetching sector by slug {slug}: {e}")
            raise


sector_service = SectorService()