from typing import Optional
from app.core.db import db
from app.models.studio import StudioCreate, StudioUpdate
import logging

logger = logging.getLogger(__name__)

class StudioService:
    async def get_studio_by_id(self, studio_id: int):
        """
        Get studio by its ID.
        """
        try:
            return await db.studio.find_unique(where={"id": studio_id})
        except Exception as e:
            logger.error(f"Error fetching studio by id {studio_id}: {e}")
            raise
            
    async def get_all_studios(self):
        """
        Get all studios.
        """
        try:
            return await db.studio.find_many(
                include={"users": True, "auctions": True}
            )
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

studio_service = StudioService()