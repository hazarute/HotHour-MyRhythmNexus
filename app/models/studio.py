from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

class StudioResponse(StudioBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
