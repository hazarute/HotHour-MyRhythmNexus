"""
Transparent Proxy for backward compatibility.
Sistemdeki diğer modüllerin (controller, webhook vb.) 
'from app.services.booking_service import booking_service' şeklindeki eski importlarını 
ayakta tutar ve yeni Booking Domain klasörüne tüneller.

Aynı zamanda hata sınıflarını (BookingError vb.) da buraya proxy ederiz,
böylece endpoint yakalamaları (except) çökmez.
"""

from app.services.booking.booking_service import booking_service
from app.services.booking.booking_exceptions import (
    BookingError,
    AuctionNotFoundError,
    AuctionNotActiveError,
    AuctionAlreadyBookedError,
    UserNotFoundError,
    AdminCannotBookError,
    GenderNotEligibleError,
    ReservationAccessDeniedError,
    RecentCancellationRestrictionError,
    RecentSectorBookingRestrictionError,
)

__all__ = [
    "booking_service",
    "BookingError",
    "AuctionNotFoundError",
    "AuctionNotActiveError",
    "AuctionAlreadyBookedError",
    "UserNotFoundError",
    "AdminCannotBookError",
    "GenderNotEligibleError",
    "ReservationAccessDeniedError",
    "RecentCancellationRestrictionError",
    "RecentSectorBookingRestrictionError",
]