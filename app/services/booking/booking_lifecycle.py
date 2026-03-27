from typing import Optional, Dict

from app.core.db import db
from app.core.timezone import now_tr, to_tr_aware
from app.models.enums import AuctionStatus, ReservationStatus, Gender
from app.services import socket_service
from app.services.notification_service import notification_service
from app.services.booking.booking_exceptions import (
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

class BookingLifecycleManager:
    """
    Rezervasyon işlemlerinin, validasyon kurallarının, soket/bildirim (event) fırlatmalarının 
    ve durum (status) değişimi gibi karmaşık işlerin döndüğü yaşam döngüsü sınıfıdır.
    """

    @staticmethod
    def _ensure_admin_studio_access(reservation, studio_id: int | None):
        if studio_id is None or reservation is None:
            return

        auction = getattr(reservation, "auction", None)
        if getattr(auction, "studioId", None) != studio_id:
            raise ReservationAccessDeniedError("Bu rezervasyon üzerinde işlem yapma yetkiniz yok")

    @staticmethod
    async def _get_service_category_sector_id(category_id: int | None) -> int | None:
        if category_id is None:
            return None

        service_category = await db.servicecategory.find_unique(where={"id": category_id})
        if not service_category:
            return None

        return getattr(service_category, "sectorId", None)

    @staticmethod
    async def _ensure_no_recent_sector_booking(user_id: int, sector_id: int | None, current_auction_id: int):
        if sector_id is None:
            return

        from datetime import timedelta

        ten_days_ago = now_tr() - timedelta(days=10)
        sector_categories = await db.servicecategory.find_many(where={"sectorId": sector_id})
        sector_category_ids = [getattr(category, "id", None) for category in sector_categories if getattr(category, "id", None) is not None]
        if not sector_category_ids:
            return

        sector_auctions = await db.auction.find_many(where={"serviceCategoryId": {"in": sector_category_ids}})
        sector_auction_ids = [
            getattr(auction, "id", None)
            for auction in sector_auctions
            if getattr(auction, "id", None) is not None and getattr(auction, "id", None) != current_auction_id
        ]
        if not sector_auction_ids:
            return

        recent_bookings = await db.reservation.find_many(
            where={
                "userId": user_id,
                "reservedAt": {"gte": ten_days_ago},
                "auctionId": {"in": sector_auction_ids},
            },
            take=1,
        )
        if recent_bookings:
            raise RecentSectorBookingRestrictionError(
                "Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz. "
                "10 gun dolmadan ayni sektorden tekrar rezervasyon yapamazsiniz."
            )

    @staticmethod
    async def validate_booking_eligibility(auction_id: int, user_id: int) -> dict:
        """
        Rezervasyon yapılmadan önce tüm iş kurallarını (cinsiyet, yetki, stoku, status) test eder.
        Kurallara uyulmazsa `booking_exceptions.py` içerisinden custom Exception fırlatır.
        Başarılıysa auction ve user objelerini döner, böylece yeniden DB'den çekmek gerekmez.
        """
        auction = await db.auction.find_unique(where={"id": auction_id})
        if not auction:
            raise AuctionNotFoundError(f"Auction {auction_id} not found")
        
        if getattr(auction, 'status', None) != AuctionStatus.ACTIVE.value:
            existing_reservations = await db.reservation.find_many(where={"auctionId": auction_id})
            if existing_reservations:
                raise AuctionAlreadyBookedError(f"Auction {auction_id} is already reserved or race condition detected")
            raise AuctionNotActiveError(f"Auction {auction_id} is not active. Status: {getattr(auction, 'status', 'UNKNOWN')}")
        
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        user_role = str(getattr(user, "role", "") or "").upper()
        if user_role == "ADMIN":
            raise AdminCannotBookError("Admin kullanıcılar rezervasyon yapamaz.")

        allowed_gender = str(getattr(auction, "allowedGender", Gender.ANY.value) or Gender.ANY.value).upper()
        user_gender = str(getattr(user, "gender", "") or "").upper()
        
        if allowed_gender in {Gender.FEMALE.value, Gender.MALE.value} and user_gender != allowed_gender:
            if allowed_gender == Gender.FEMALE.value:
                raise GenderNotEligibleError("Bu oturum yalnızca kadın kullanıcılar içindir.")
            raise GenderNotEligibleError("Bu oturum yalnızca erkek kullanıcılar içindir.")

        # --- Kötüye Kullanım Koruması ---
        # Kullanıcı aynı stüdyo + hizmet kategorisinde son 10 gün içinde kendi isteğiyle
        # bir rezervasyon iptal ettiyse yeni rezervasyonu engelle.
        studio_id = getattr(auction, 'studioId', None)
        category_id = getattr(auction, 'serviceCategoryId', None)
        if studio_id is not None and category_id is not None:
            from datetime import timedelta
            ten_days_ago = now_tr() - timedelta(days=10)
            # 1. Adım: Aynı stüdyo + kategori kombinasyonundaki tüm fırsat ID'lerini bul
            matching_auctions = await db.auction.find_many(
                where={"studioId": studio_id, "serviceCategoryId": category_id},
            )
            matching_auction_ids = [getattr(a, 'id') for a in matching_auctions]
            # 2. Adım: Kullanıcının bu fırsatlardan herhangi birini son 10 günde USER olarak iptal edip etmediğini kontrol et
            if matching_auction_ids:
                recent_cancels = await db.reservation.find_many(
                    where={
                        "userId": user_id,
                        "cancelSource": "USER",
                        "cancelledAt": {"gte": ten_days_ago},
                        "auctionId": {"in": matching_auction_ids},
                    },
                    take=1,
                )
                if recent_cancels:
                    raise RecentCancellationRestrictionError(
                        "Bu hizmet kategorisinden son 10 gün içinde bir rezervasyonu iptal ettiniz. "
                        "10 gün sonra aynı kategoriden tekrar rezervasyon yapabilirsiniz."
                    )

        sector_id = await BookingLifecycleManager._get_service_category_sector_id(category_id)
        await BookingLifecycleManager._ensure_no_recent_sector_booking(
            user_id=user_id,
            sector_id=sector_id,
            current_auction_id=auction_id,
        )

        return {"auction": auction, "user": user}

    async def auto_cancel_overdue_pending_reservations(self) -> int:
        """
        Hizmet saatinden GRACE_MINUTES dakika sonra hâlâ PENDING_ON_SITE durumunda
        olan rezervasyonları otomatik iptal eder (no-show / gelmedi).
        """
        GRACE_MINUTES = 30
        now = now_tr()
        
        reservations = await db.reservation.find_many(
            where={"status": ReservationStatus.PENDING_ON_SITE.value},
            include={"auction": True, "user": True}
        )

        cancelled_count = 0
        for reservation in reservations:
            auction = getattr(reservation, 'auction', None)

            if not auction:
                continue

            scheduled_at = to_tr_aware(getattr(auction, "scheduledAt", None))
            end_time = to_tr_aware(getattr(auction, "endTime", None))
            service_time = scheduled_at or end_time

            if not service_time:
                continue

            from datetime import timedelta
            deadline = service_time + timedelta(minutes=GRACE_MINUTES)
            if now < deadline:
                continue

            print(f"[AutoCancel] Reservation {reservation.id} cancelled: "
                  f"service_time={service_time.isoformat()}, "
                  f"deadline={deadline.isoformat()}, now={now.isoformat()}")
            await self.cancel_reservation(reservation.id, cancel_source="AUTO_NO_SHOW")
            cancelled_count += 1

        return cancelled_count

    async def cancel_reservation(self, reservation_id: int, cancel_source: str = "SYSTEM", studio_id: int | None = None) -> bool:
        reservation = await db.reservation.find_unique(
            where={"id": reservation_id},
            include={"user": True, "auction": True}
        )
        if not reservation:
            return False

        if str(getattr(reservation, "status", "")).upper() == ReservationStatus.CANCELLED.value:
            return True

        auction = getattr(reservation, 'auction', None)
        if not auction:
             auction_id = getattr(reservation, 'auctionId', None)
             if auction_id:
                 auction = await db.auction.find_unique(where={"id": auction_id})
                 try:
                     reservation.auction = auction
                 except Exception:
                     pass

        self._ensure_admin_studio_access(reservation, studio_id)
        user = getattr(reservation, 'user', None)
        
        await db.reservation.update(
            where={"id": reservation_id},
            data={
                "status": ReservationStatus.CANCELLED.value,
                "cancelledAt": now_tr(),
                "cancelSource": str(cancel_source or "SYSTEM").upper(),
            }
        )

        if auction and str(getattr(auction, "status", "")).upper() != AuctionStatus.CANCELLED.value:
            await db.auction.update(
                where={"id": getattr(auction, "id")},
                data={"status": AuctionStatus.CANCELLED.value}
            )

        auction_id_for_event = getattr(auction, "id", getattr(reservation, "auctionId", None))
        if auction_id_for_event is not None:
            await socket_service.emit_reservation_cancelled(
                reservation_id=reservation_id,
                auction_id=auction_id_for_event,
            )

        user_name = getattr(user, "fullName", "Bilinmeyen Kullanıcı") if user else "Bilinmeyen Kullanıcı"
        auction_title = getattr(auction, "title", "Bilinmeyen Oturum") if auction else "Bilinmeyen Oturum"
        booking_code = getattr(reservation, "bookingCode", "-")

        source_key = str(cancel_source or "").upper()
        if source_key == "AUTO_NO_SHOW":
            await notification_service.create_admin_notifications(
                title="Otomatik Rezervasyon İptali",
                message=(f'"{auction_title}" oturumu için {user_name} (kod: {booking_code}) '
                         "hizmet saatine kadar giriş yapmadığı için rezervasyon otomatik iptal edildi."),
                notification_type="AUTO_CANCEL_NO_SHOW",
                reservation_id=reservation_id,
                auction_id=getattr(auction, "id", None),
            )
        elif source_key == "USER":
            await notification_service.create_admin_notifications(
                title="Müşteri Rezervasyonu İptal Etti",
                message=(f'{user_name}, "{auction_title}" oturumu için rezervasyonunu '
                         f'(kod: {booking_code}) kullanıcı panelinden iptal etti.'),
                notification_type="USER_CANCELLED_BY_CUSTOMER",
                reservation_id=reservation_id,
                auction_id=getattr(auction, "id", None),
            )

        return True

    async def check_in_reservation(self, reservation_id: int, studio_id: int | None = None) -> bool:
        reservation = await db.reservation.find_unique(
            where={"id": reservation_id},
            include={"auction": True},
        )
        if not reservation:
            return False

        if getattr(reservation, "auction", None) is None:
            auction_id = getattr(reservation, "auctionId", None)
            if auction_id is not None:
                auction = await db.auction.find_unique(where={"id": auction_id})
                try:
                    reservation.auction = auction
                except Exception:
                    pass

        self._ensure_admin_studio_access(reservation, studio_id)
            
        await db.reservation.update(
            where={"id": reservation_id},
            data={"status": ReservationStatus.COMPLETED.value}
        )

        auction_id_for_event = getattr(reservation, "auctionId", None)
        if auction_id_for_event is not None:
            await socket_service.emit_reservation_updated(
                reservation_id=reservation_id,
                status=ReservationStatus.COMPLETED.value,
                auction_id=auction_id_for_event,
            )

        return True

booking_lifecycle_manager = BookingLifecycleManager()