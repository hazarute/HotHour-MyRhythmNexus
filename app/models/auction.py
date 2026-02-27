from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


class AuctionBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_price: Decimal
    floor_price: Decimal
    start_time: datetime
    end_time: datetime
    drop_interval_mins: Optional[int] = 60
    drop_amount: Optional[Decimal] = None
    turbo_enabled: Optional[bool] = False
    turbo_trigger_mins: Optional[int] = 120
    turbo_drop_amount: Optional[Decimal] = None
    turbo_interval_mins: Optional[int] = 5
    current_price: Optional[Decimal] = None


class AuctionCreate(AuctionBase):
    pass

class AuctionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    start_price: Optional[Decimal] = None
    floor_price: Optional[Decimal] = None
    drop_interval_mins: Optional[int] = None
    drop_amount: Optional[Decimal] = None
    turbo_enabled: Optional[bool] = None
    turbo_trigger_mins: Optional[int] = None
    turbo_drop_amount: Optional[Decimal] = None
    turbo_interval_mins: Optional[int] = None


class AuctionResponse(AuctionBase):
    id: int
    status: str
    computedPrice: Optional[Decimal] = None
    priceDetails: Optional[dict] = None
    
    # Allow camelCase aliasing for frontend ease if needed, but standard is keep consistency
    # For now, let's add current_price to AuctionBase so it gets picked up from DB model


    class Config:
        from_attributes = True
