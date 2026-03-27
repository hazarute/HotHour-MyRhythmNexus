from typing import Dict, Optional

from app.core.db import db
from app.models.enums import AuctionStatus, ReservationStatus
from app.utils.booking_utils import generate_booking_code
from app.services import socket_service

# DDD Parçalarımız (Departmanlarımız)
from app.services.booking.booking_exceptions import BookingError, AuctionAlreadyBookedError
from app.services.booking.booking_repository import booking_repository
from app.services.booking.booking_lifecycle import booking_lifecycle_manager

class BookingService:
    """
    ŞEF (ORCHESTRATOR): Rezervasyon (Booking) sisteminin ana yönetim sınıfı.
    Görevi: Gelen tüm işlemlerin doğrulamalarını (Lifecycle) yaptırmak, veriyi ayarlamak
    ve veritabanına yazdırmalarını (Repository) sağlamaktır. Kendisi asla detaylı kural ve sorgu yazmaz.
    """

    # --- REPOSITORY (Proxy) METODLARI --- 
    # Sistemin geri kalanı (Controller ve Route'lar) hala booking_service üzerinden veri istiyor.
    # Biz de bu istekleri Repository'ye yönlendiriyoruz (Delege Ediyoruz).
    
    async def get_reservation(self, reservation_id: int) -> Optional[Dict]:
        return await booking_repository.get_reservation(reservation_id)
    
    async def get_reservation_by_code(self, booking_code: str) -> Optional[Dict]:
        return await booking_repository.get_reservation_by_code(booking_code)
    
    async def get_user_reservations(self, user_id: int, base_url: str | None = None) -> list[Dict]:
        reservations = await booking_repository.get_user_reservations(user_id)

        if base_url:
            for res in reservations:
                studio = res.get("studio")
                if isinstance(studio, dict):
                    logo = studio.get("logoUrl")
                    if logo and str(logo).startswith("/uploads/"):
                        studio["logoUrl"] = f"{base_url}{logo}"
                        res["studio"] = studio
        return reservations

    async def get_all_reservations(self, studio_id: int | None = None) -> list[Dict]:
        return await booking_repository.get_all_reservations(studio_id)

    async def get_reservation_with_details(self, reservation_id: int, studio_id: int | None = None) -> Optional[Dict]:
        return await booking_repository.get_reservation_with_details(reservation_id, studio_id)

    # --- LIFECYCLE (Proxy) METODLARI ---
    async def auto_cancel_overdue_pending_reservations(self) -> int:
        return await booking_lifecycle_manager.auto_cancel_overdue_pending_reservations()

    async def cancel_reservation(self, reservation_id: int, cancel_source: str = "SYSTEM", studio_id: int | None = None) -> bool:
        return await booking_lifecycle_manager.cancel_reservation(reservation_id, cancel_source, studio_id)

    async def check_in_reservation(self, reservation_id: int, studio_id: int | None = None) -> bool:
        return await booking_lifecycle_manager.check_in_reservation(reservation_id, studio_id)

    # --- ANA İŞLEM (Orchestrator Logic) ---
    async def book_auction(self, auction_id: int, user_id: int) -> Dict:
        """Core Business Logic: Müzayedeyi satın alma işlemini orkestre eder."""
        
        # 1. Yaşam döngüsü kurallarını doğrula (Admin mi? Kadın oturumu mu? Müsait mi?)
        validation_result = await booking_lifecycle_manager.validate_booking_eligibility(auction_id, user_id)
        auction = validation_result["auction"]

        # 2. Ücret Sabitleme ve Kod Üretimi
        locked_price = getattr(auction, 'currentPrice', getattr(auction, 'startPrice', 0))
        booking_code = generate_booking_code()

        # 3. İşlem Kaydı (Atomic DB Transaction)
        try:
            reservation = await db.reservation.create(
                data={
                    "auctionId": auction_id,
                    "userId": user_id,
                    "lockedPrice": locked_price,
                    "bookingCode": booking_code,
                    "status": ReservationStatus.PENDING_ON_SITE.value,
                }
            )

            await db.auction.update(
                where={"id": auction_id},
                data={"status": AuctionStatus.SOLD.value}
            )
            
            result = {
                "id": reservation.id,
                "auction_id": reservation.auctionId,
                "user_id": reservation.userId,
                "locked_price": reservation.lockedPrice,
                "booking_code": reservation.bookingCode,
                "status": reservation.status,
                "reserved_at": reservation.reservedAt,
            }

            # 4. Soket Bildirimleri
            await socket_service.emit_booking_confirmed(
                user_id=user_id,
                auction_id=auction_id,
                booking_code=reservation.bookingCode,
                locked_price=reservation.lockedPrice,
                status=reservation.status,
            )
            await socket_service.emit_auction_booked(
                auction_id=auction_id,
                booking_code=reservation.bookingCode,
                locked_price=str(reservation.lockedPrice),
            )
            await socket_service.emit_reservation_created(
                reservation_id=reservation.id,
                booking_code=reservation.bookingCode,
                user_id=user_id,
                auction_id=auction_id,
                status=str(getattr(reservation.status, "name", reservation.status)),
            )

            return result
        
        except Exception as e:
            error_msg = str(e).lower()
            if "unique constraint" in error_msg or "duplicate key" in error_msg:
                raise AuctionAlreadyBookedError(
                    f"Auction {auction_id} is already reserved or race condition detected"
                )
            raise BookingError(f"Booking failed: {str(e)}")

booking_service = BookingService()