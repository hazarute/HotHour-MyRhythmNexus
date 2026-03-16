from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SectorBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    isActive: bool = True


class SectorCreate(SectorBase):
    pass


class SectorUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    isActive: Optional[bool] = None


class SectorResponse(SectorBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True