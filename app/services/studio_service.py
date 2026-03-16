from typing import Optional
from app.core.db import db
from app.models.studio import StudioCreate, StudioUpdate
from app.core.timezone import now_tr
import logging

logger = logging.getLogger(__name__)

class StudioService:
    async def _attach_sector_relations(self, studio):
        if not studio or getattr(studio, "id", None) is None:
            return studio

        try:
            sector_links = await db.studiosector.find_many(where={"studioId": studio.id})
            enriched_links = []
            for link in sector_links:
                sector = await db.sector.find_unique(where={"id": getattr(link, "sectorId", None)})
                try:
                    link.sector = sector
                except Exception:
                    pass
                enriched_links.append(link)

            try:
                studio.sectors = enriched_links
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error attaching sector relations for studio {getattr(studio, 'id', None)}: {e}")
            raise

        return studio

    def _build_include(
        self,
        include_users: bool = False,
        include_auctions: bool = False,
        include_sectors: bool = False,
    ):
        include = {}
        if include_users:
            include["users"] = True
        if include_auctions:
            include["auctions"] = True
        if include_sectors:
            include["sectors"] = {"include": {"sector": True}}
        return include or None

    async def get_studio_by_id(
        self,
        studio_id: int,
        include_users: bool = False,
        include_auctions: bool = False,
        include_sectors: bool = False,
    ):
        """
        Get studio by its ID.
        """
        try:
            include = self._build_include(
                include_users=include_users,
                include_auctions=include_auctions,
                include_sectors=include_sectors,
            )
            return await db.studio.find_unique(where={"id": studio_id}, include=include)
        except Exception as e:
            logger.error(f"Error fetching studio by id {studio_id}: {e}")
            raise
            
    async def get_all_studios(
        self,
        include_users: bool = True,
        include_auctions: bool = True,
        include_sectors: bool = False,
    ):
        """
        Get all studios.
        """
        try:
            include = self._build_include(
                include_users=include_users,
                include_auctions=include_auctions,
                include_sectors=include_sectors,
            )
            studios = await db.studio.find_many(include=include)
            if include_sectors:
                enriched_studios = []
                for studio in studios:
                    enriched_studios.append(await self._attach_sector_relations(studio))
                return enriched_studios

            return studios
        except Exception as e:
             logger.error(f"Error fetching all studios: {e}")
             raise

    async def update_studio(self, studio_id: int, data: StudioUpdate):
        """
        Update an existing studio.
        """
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return await self.get_studio_by_id(studio_id)
            
        try:
            return await db.studio.update(
                where={"id": studio_id},
                data=update_data
            )
        except Exception as e:
            logger.error(f"Error updating studio {studio_id}: {e}")
            raise

    async def get_studio_with_sectors(self, studio_id: int):
        studio = await self.get_studio_by_id(studio_id, include_sectors=True)
        return await self._attach_sector_relations(studio)

    async def replace_studio_sectors(self, studio_id: int, sector_ids: list[int]):
        studio = await self.get_studio_by_id(studio_id)
        if not studio:
            return None

        unique_sector_ids = sorted(set(sector_ids))
        if unique_sector_ids:
            sectors = await db.sector.find_many(where={"id": {"in": unique_sector_ids}, "isActive": True})
            found_ids = sorted(getattr(sector, "id", None) for sector in sectors)
            if found_ids != unique_sector_ids:
                missing = sorted(set(unique_sector_ids) - set(found_ids))
                raise ValueError(f"Geçersiz veya pasif sektör id değerleri: {missing}")

        await db.studiosector.delete_many(where={"studioId": studio_id})

        for sector_id in unique_sector_ids:
            await db.studiosector.create(
                data={
                    "studioId": studio_id,
                    "sectorId": sector_id,
                    "assignedAt": now_tr(),
                }
            )

        return await self.get_studio_with_sectors(studio_id)

studio_service = StudioService()