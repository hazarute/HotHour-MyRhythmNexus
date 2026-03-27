from fastapi import HTTPException, status
from app.services.booking_service import booking_service
from app.services.booking_service import ReservationAccessDeniedError


async def get_reservation_or_404(reservation_id: int):
    reservation = await booking_service.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found"
        )
    return reservation


async def ensure_reservation_owner(reservation, user):
    if not reservation or reservation.get("user_id") != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own reservations"
        )
    return reservation


async def get_reservation_or_403(reservation_id: int, user):
    reservation = await get_reservation_or_404(reservation_id)
    return await ensure_reservation_owner(reservation, user)


async def get_reservation_by_code_or_403(booking_code: str, user):
    reservation = await booking_service.get_reservation_by_code(booking_code)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking code {booking_code} not found"
        )
    await ensure_reservation_owner(reservation, user)
    return reservation
