from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.sector import SectorResponse

class StudioBase(BaseModel):
    name: str
    address: Optional[str] = None
    logoUrl: Optional[str] = None
    googleMapsUrl: Optional[str] = None

class StudioCreate(StudioBase):
    pass

class StudioUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    logoUrl: Optional[str] = None
    googleMapsUrl: Optional[str] = None


class StudioSectorAssignment(BaseModel):
    sectorIds: List[int]


class StudioSectorResponse(BaseModel):
    studioId: int
    sectorId: int
    assignedAt: datetime
    sector: Optional[SectorResponse] = None

    class Config:
        from_attributes = True

class StudioResponse(StudioBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    sectors: Optional[List[StudioSectorResponse]] = None
    
    class Config:
        from_attributes = True
