"""
Reservations API Endpoints (Booking endpoints for HotHour auctions)
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.models.reservation import ReservationCreate, ReservationResponse
from app.core.deps import get_current_user
from app.services.booking_service import (
    booking_service,
    AuctionNotFoundError,
    AuctionNotActiveError,
    AuctionAlreadyBookedError,
    UserNotFoundError,
    AdminCannotBookError,
    GenderNotEligibleError,
    BookingError,
)

router = APIRouter(prefix="/api/v1/reservations", tags=["reservations"])


@router.post("/book", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def book_auction(
    data: ReservationCreate,
    current_user = Depends(get_current_user)  # Prisma User object
):
    """
    Book (reserve) an auction at the current price.
    
    The user placing the request must match the user_id in the request.
    
    Request Body:
    - auction_id: ID of auction to reserve
    - user_id: ID of user (must match current authenticated user)
    
    Returns:
    - 201: Reservation created successfully
    - 400: Auction not found, not active, or already booked (race condition)
    - 401: Unauthorized
    - 403: Forbidden (booking for another user)
    - 404: User not found
    """
    
    # Ensure user can only book for themselves
    # current_user is a Prisma User object
    if data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only book reservations for themselves"
        )
    
    try:
        reservation = await booking_service.book_auction(
            auction_id=data.auction_id,
            user_id=data.user_id
        )
        return reservation
    except AuctionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auction {data.auction_id} not found"
        )
    except AuctionNotActiveError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Auction {data.auction_id} is not active"
        )
    except AuctionAlreadyBookedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This auction is already booked. Another user booked it first (or race condition)."
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {data.user_id} not found"
        )
    except AdminCannotBookError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except GenderNotEligibleError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except BookingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{booking_code}/trigger-manual", response_model=ReservationResponse)
async def trigger_manual_booking(
    booking_code: str,
    current_user = Depends(get_current_user)  # Prisma User object
):
    """
    Manually trigger/confirm a booking by booking code.
    (For testing/manual override purposes)
    
    Returns:
    - 200: Reservation found
    - 404: Booking code not found
    """
    reservation = await booking_service.get_reservation_by_code(booking_code)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking code {booking_code} not found"
        )
    
    # Verify ownership
    if reservation["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own reservations"
        )
    
    return reservation


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    current_user = Depends(get_current_user)  # Prisma User object
):
    """
    Get details of a specific reservation by ID.
    
    Returns:
    - 200: Reservation found
    - 404: Reservation not found
    - 403: Unauthorized (not your reservation)
    """
    reservation = await booking_service.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found"
        )
    
    # Verify ownership
    if reservation["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own reservations"
        )
    
    return reservation


@router.get("/admin/all")
async def get_all_reservations(current_user = Depends(get_current_user)):
    """
    Get ALL reservations (Admin only).
    
    Returns:
    - 200: List of reservations with user details
    - 403: Forbidden (if not admin)
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    reservations = await booking_service.get_all_reservations()
    return reservations


@router.get("/admin/notifications/cancellations")
async def get_admin_cancellation_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    current_user = Depends(get_current_user),
):
    """
    Admin: Get cancellation-related notifications generated by system automation.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return await booking_service.get_admin_cancellation_notifications(
        admin_user_id=current_user.id,
        limit=limit,
    )


@router.post("/admin/notifications/{notification_id}/read")
async def mark_admin_notification_as_read(
    notification_id: int,
    current_user = Depends(get_current_user),
):
    """
    Admin: Mark a cancellation notification as read.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    success = await booking_service.mark_notification_as_read(
        notification_id=notification_id,
        admin_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {"message": "Notification marked as read"}


@router.delete("/admin/notifications/{notification_id}")
async def delete_admin_notification(
    notification_id: int,
    current_user = Depends(get_current_user),
):
    """
    Admin: Delete one cancellation notification.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    success = await booking_service.delete_admin_notification(
        notification_id=notification_id,
        admin_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {"message": "Notification deleted"}


@router.delete("/admin/notifications/read/all")
async def delete_admin_read_notifications(
    current_user = Depends(get_current_user),
):
    """
    Admin: Delete all read cancellation notifications.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    deleted_count = await booking_service.delete_admin_read_notifications(
        admin_user_id=current_user.id,
    )
    return {"deleted_count": deleted_count}


@router.get("/admin/{reservation_id}")
async def get_admin_reservation_details(
    reservation_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get detailed reservation info for admin.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    reservation = await booking_service.get_reservation_with_details(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found"
        )
    return reservation



@router.get("/my/all")
async def get_my_reservations(current_user = Depends(get_current_user)):
    """
    Get all reservations for the current user.
    
    Returns:
    - 200: List of reservations
    """
    reservations = await booking_service.get_user_reservations(current_user.id)
    return {
        "user_id": current_user.id,
        "reservations": reservations,
        "count": len(reservations)
    }


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reservation(
    reservation_id: int,
    current_user = Depends(get_current_user)  # Prisma User object
):
    """
    Cancel a reservation.
    
    Returns:
    - 204: Cancelled successfully
    - 404: Reservation not found
    - 403: Unauthorized (not your reservation)
    """
    reservation = await booking_service.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found"
        )
    
    # Verify ownership
    if reservation["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own reservations"
        )
    
    await booking_service.cancel_reservation(reservation_id, cancel_source="USER")


@router.post("/admin/{reservation_id}/check-in")
async def admin_check_in_reservation(
    reservation_id: int,
    current_user = Depends(get_current_user)
):
    """
    Admin: Mark a reservation as Checked In (COMPLETED).
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    success = await booking_service.check_in_reservation(reservation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    return {"message": "Reservation checked in successfully", "status": "COMPLETED"}


@router.post("/admin/{reservation_id}/cancel")
async def admin_cancel_reservation(
    reservation_id: int,
    current_user = Depends(get_current_user)
):
    """
    Admin: Cancel a reservation.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    success = await booking_service.cancel_reservation(reservation_id, cancel_source="ADMIN")
    if not success:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    return {"message": "Reservation cancelled successfully", "status": "CANCELLED"}
