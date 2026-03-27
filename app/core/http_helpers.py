from fastapi import HTTPException, status
from app.services.booking_service import (
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


def raise_mapped_http(exc: Exception):
    """Map service-level exceptions to HTTPException and raise.

    If the exception is not recognized, re-raise it so it surfaces as a 500.
    """
    if isinstance(exc, AuctionNotFoundError) or isinstance(exc, UserNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, AuctionNotActiveError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, AuctionAlreadyBookedError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, (AdminCannotBookError, GenderNotEligibleError, ReservationAccessDeniedError)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, (RecentCancellationRestrictionError, RecentSectorBookingRestrictionError)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, BookingError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Unknown exception: re-raise to be handled by FastAPI/exception handlers (500)
    raise exc
