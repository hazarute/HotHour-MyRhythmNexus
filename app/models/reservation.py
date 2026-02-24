from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING_ON_SITE = "PENDING_ON_SITE"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"


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
