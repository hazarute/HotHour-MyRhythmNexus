from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.enums import PaymentStatus


class ReservationBase(BaseModel):
    auction_id: int
    user_id: int
    locked_price: Decimal
    booking_code: str


class ReservationCreate(BaseModel):
    auction_id: int
    user_id: int


class ReservationResponse(ReservationBase):
    id: int
    status: PaymentStatus
    reserved_at: datetime

    class Config:
        from_attributes = True


class ReservationDetail(ReservationResponse):
    """Extended reservation info with auction & user details"""
    auction_title: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True
