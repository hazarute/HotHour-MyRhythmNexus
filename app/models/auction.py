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


class AuctionCreate(AuctionBase):
    pass


class AuctionResponse(AuctionBase):
    id: int
    status: str
    computedPrice: Optional[Decimal] = None
    priceDetails: Optional[dict] = None

    class Config:
        from_attributes = True
