class BookingError(Exception):
    """Base exception for booking errors"""
    pass

class AuctionNotFoundError(BookingError):
    """Raised when auction is not found"""
    pass

class AuctionNotActiveError(BookingError):
    """Raised when auction is not in ACTIVE status"""
    pass

class AuctionAlreadyBookedError(BookingError):
    """Raised when auction is already reserved (race condition or already booked)"""
    pass

class UserNotFoundError(BookingError):
    """Raised when user is not found"""
    pass

class AdminCannotBookError(BookingError):
    """Raised when admin user attempts to book an auction"""
    pass

class GenderNotEligibleError(BookingError):
    """Raised when user's gender is not eligible for this auction"""
    pass


class ReservationAccessDeniedError(BookingError, PermissionError):
    """Raised when an admin tries to manage a reservation outside their studio scope."""
    pass