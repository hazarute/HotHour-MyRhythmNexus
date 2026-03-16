from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.models.sector import SectorResponse


class ServiceCategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    isActive: bool = True
    sectorId: Optional[int] = None


class ServiceCategoryCreate(ServiceCategoryBase):
    pass


class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    isActive: Optional[bool] = None
    sectorId: Optional[int] = None


class ServiceCategoryResponse(ServiceCategoryBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    sector: Optional[SectorResponse] = None

    class Config:
        from_attributes = True