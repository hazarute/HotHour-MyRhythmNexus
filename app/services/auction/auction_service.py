from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.core.timezone import now_tr, to_tr_aware
from app.core.db import db
from app.models.enums import AuctionStatus
from app.utils.validators import ValidationError
from app.services import socket_service
from app.services.price_service import price_service
from app.services.service_category_service import service_category_service

# Yeni modüler yapımız (Domain-Driven Design)
from app.utils.auction_mapper import auction_mapper
from app.services.auction.auction_repository import auction_repository, DEFAULT_INCLUDES
from app.services.auction.auction_lifecycle import auction_lifecycle_manager


class AuctionAccessDeniedError(PermissionError):
    """Raised when an admin tries to manage an auction outside their studio scope."""


class AuctionService:
    """
    ŞEF (ORCHESTRATOR): Müzayede (Auction) merkez yönetimi.
    Kendisi doğrudan veritabanı sorgusu veya formatlama yapmaz. İşleri alt departmanlara delege eder:
    - auction_mapper: Veri formatlama ve dönüştürme
    - auction_repository: Veritabanı sorguları ve ilişki (join) sorunları
    - auction_lifecycle_manager: Statü ayarlamaları, fiyat hesapları ve turbo kilitleri
    """

    async def _validate_service_category_for_studio(self, studio_id: int | None, service_category_id: int | None):
        if service_category_id is not None:
            service_category = await service_category_service.get_service_category_by_id(service_category_id)
            if not service_category:
                raise ValidationError("Geçerli ve aktif bir hizmet kategorisi seçmelisiniz")

        if not studio_id:
            return

        studio_requires_category = await service_category_service.studio_requires_service_category(studio_id)

        if studio_requires_category and service_category_id is None:
            raise ValidationError("İşletmenize bağlı sektörler için bir hizmet kategorisi seçmelisiniz")

        if service_category_id is None:
            return

        is_allowed = await service_category_service.is_service_category_allowed_for_studio(
            studio_id,
            service_category_id,
        )
        if not is_allowed:
            raise ValidationError("Seçilen hizmet kategorisi işletmenizin sektörleriyle eşleşmiyor")

    @staticmethod
    def _ensure_studio_access(record, studio_id: int | None):
        if studio_id is None or record is None:
            return

        if getattr(record, "studioId", None) != studio_id:
            raise AuctionAccessDeniedError("Bu fırsat üzerinde işlem yapma yetkiniz yok")

    async def create_auction(self, data: dict, studio_id: int | None = None):
        # 1. Validation & Mapping
        _, merged = auction_mapper.validate_and_merge_auction_data(data, force_full_validation=True)

        service_category_id = data.get("serviceCategoryId")
        effective_studio_id = studio_id if studio_id is not None else data.get("studioId")
        await self._validate_service_category_for_studio(effective_studio_id, service_category_id)

        create_data = auction_mapper.prepare_create_data(merged)

        if effective_studio_id:
            create_data["studioId"] = effective_studio_id
        if service_category_id is not None:
            create_data["serviceCategoryId"] = service_category_id

        # 2. Repository (Insert)
        created = await db.auction.create(data=create_data, include=DEFAULT_INCLUDES)
        created = await auction_repository.attach_missing_relations(created)

        # 3. Lifecycle & Socket Event
        auction_status = auction_lifecycle_manager.determine_initial_status(
            getattr(created, "startTime", None),
            getattr(created, "endTime", None)
        )

        mapping = auction_mapper.to_mapping(created)
        mapping["status"] = auction_status
        await socket_service.emit_auction_created(mapping)
        return created

    async def get_auction(self, auction_id: int):
        auction = await db.auction.find_unique(where={"id": auction_id}, include=DEFAULT_INCLUDES)
        if auction:
            auction = await auction_repository.attach_missing_relations(auction)
            auction = await auction_lifecycle_manager.sync_status_with_reservation(auction)
            auction = await auction_lifecycle_manager.check_and_update_status(auction)
            auction = await auction_lifecycle_manager.ensure_turbo_triggered(auction)
            auction = await auction_lifecycle_manager.sync_current_price(auction)
            auction = await auction_repository.attach_missing_relations(auction)
        return auction

    async def check_pending_auctions(self):
        try:
            items = await auction_repository.find_many_auctions_with_reconnect(where={
                "status": {
                    "in": [AuctionStatus.DRAFT.value, AuctionStatus.ACTIVE.value]
                }
            })
            
            for item in items:
                checked = await auction_lifecycle_manager.check_and_update_status(item)
                checked = await auction_lifecycle_manager.ensure_turbo_triggered(checked)
                await auction_lifecycle_manager.sync_current_price(checked, emit_event=True)
            return len(items)
        except Exception as e:
            print(f"Error checking pending auctions: {e}")
            return 0

    async def list_auctions(
        self,
        include_computed: bool = False,
        now=None,
        sector_slug: str | None = None,
        service_category_slug: str | None = None,
        allowed_gender: str | None = None,
    ):
        items = await auction_repository.find_many_auctions_with_reconnect()
        normalized_now = to_tr_aware(now) if now else None

        updated_items = []
        for item in items:
            checked = await auction_lifecycle_manager.sync_status_with_reservation(item)
            checked = await auction_lifecycle_manager.check_and_update_status(checked)
            checked = await auction_lifecycle_manager.ensure_turbo_triggered(checked)
            checked = await auction_lifecycle_manager.sync_current_price(checked)
            checked = await auction_repository.attach_missing_relations(checked)
            updated_items.append(checked)
        items = updated_items

        items = [
            item for item in items
            if auction_repository.matches_sector_filter(item, sector_slug)
            and auction_repository.matches_service_category_filter(item, service_category_slug)
            and auction_repository.matches_allowed_gender_filter(item, allowed_gender)
        ]

        if not include_computed:
            return items

        out = []
        for item in items:
            mapping = auction_mapper.to_mapping(item)
            price, details = price_service.compute_current_price(mapping, now=normalized_now)
            out.append({
                "id": mapping.get("id"),
                "title": mapping.get("title"),
                "description": mapping.get("description"),
                "allowed_gender": mapping.get("allowedGender"),
                "start_price": mapping.get("startPrice"),
                "floor_price": mapping.get("floorPrice"),
                "start_time": mapping.get("startTime"),
                "end_time": mapping.get("endTime"),
                "drop_interval_mins": mapping.get("dropIntervalMins"),
                "drop_amount": mapping.get("dropAmount"),
                "turbo_enabled": mapping.get("turboEnabled"),
                "turbo_trigger_mins": mapping.get("turboTriggerMins"),
                "turbo_drop_amount": mapping.get("turboDropAmount"),
                "turbo_interval_mins": mapping.get("turboIntervalMins"),
                "turbo_started_at": getattr(item, "turboStartedAt", None),
                "status": getattr(item, "status", None),
                "computedPrice": str(price),
                "priceDetails": details,
                "currentPrice": mapping.get("currentPrice"),
                "created_at": getattr(item, "createdAt", None),
                "updated_at": getattr(item, "updatedAt", None),
                "studioId": getattr(item, "studioId", None),
                "studio": getattr(item, "studio", None),
                "serviceCategoryId": getattr(item, "serviceCategoryId", None),
                "serviceCategory": getattr(item, "serviceCategory", None),
            })
        return out

    async def update_auction(self, auction_id: int, data: dict, studio_id: int | None = None):
        existing = await db.auction.find_unique(where={"id": auction_id})
        if not existing:
            return None

        self._ensure_studio_access(existing, studio_id)

        # 1. Validation & Mapping
        should_run_full, merged = auction_mapper.validate_and_merge_auction_data(data, existing)
        update_data = auction_mapper.prepare_update_data(data, merged, should_run_full)

        if "serviceCategoryId" in data:
            sc_id = update_data.get("serviceCategoryId")
            effective_studio_id = studio_id if studio_id is not None else getattr(existing, "studioId", None)
            await self._validate_service_category_for_studio(effective_studio_id, sc_id)

        if not update_data:
            return None

        # 2. Update DB
        updated = await db.auction.update(
            where={"id": auction_id},
            data=update_data,
            include=DEFAULT_INCLUDES
        )
        updated = await auction_repository.attach_missing_relations(updated)

        updated_id = getattr(updated, "id", None)
        computed_auction = await self.get_auction(updated_id) if updated_id is not None else None
        
        # 3. Emit
        if computed_auction:
            mapping = auction_mapper.to_mapping(computed_auction)
            mapping["status"] = getattr(computed_auction, "status", AuctionStatus.DRAFT.value)
            await socket_service.emit_auction_updated(mapping)

        return updated

    async def delete_auction(self, auction_id: int, studio_id: int | None = None):
        existing = await db.auction.find_unique(where={"id": auction_id})
        if not existing:
            return None

        self._ensure_studio_access(existing, studio_id)

        if getattr(existing, "status", None) != AuctionStatus.DRAFT.value:
            raise ValidationError("Only DRAFT auctions can be deleted")

        deleted = await db.auction.delete(where={"id": auction_id})
        await socket_service.emit_auction_deleted(auction_id)
        return deleted

    async def get_current_price(self, auction_id: int, now=None):
        auction = await db.auction.find_unique(where={"id": auction_id})
        if not auction:
            return None
        mapping = auction_mapper.to_mapping(auction)
        normalized_now = to_tr_aware(now) if now else None
        price, details = price_service.compute_current_price(mapping, now=normalized_now)
        return {"price": str(price), "details": details}

    async def check_and_trigger_turbo(self, auction_id: int, now: Optional[datetime] = None):
        return await auction_lifecycle_manager.check_and_trigger_turbo(auction_id, now)

auction_service = AuctionService()
