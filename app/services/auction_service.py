from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.core.db import db
from app.core.timezone import now_tr, to_tr_aware
from app.services import socket_service
from app.services.price_service import price_service
from app.utils.validators import ValidationError, auction_validator


class AuctionService:
    def _apply_backend_pricing_policy(self, data: dict) -> dict:
        normalized = dict(data)
        turbo_enabled = bool(normalized.get("turbo_enabled", False))

        if turbo_enabled:
            normalized["turbo_trigger_mins"] = auction_validator.TURBO_TRIGGER_MINS_FIXED
            normalized["turbo_interval_mins"] = auction_validator.TURBO_INTERVAL_MINS_FIXED
        else:
            normalized["turbo_trigger_mins"] = auction_validator.TURBO_TRIGGER_MINS_FIXED
            normalized["turbo_interval_mins"] = auction_validator.TURBO_INTERVAL_MINS_FIXED
            normalized["turbo_drop_amount"] = Decimal("0.00")

        return normalized

    async def _sync_current_price(self, auction, now: Optional[datetime] = None, emit_event: bool = False):
        if not auction:
            return None

        if getattr(auction, "status", None) != "ACTIVE":
            return auction

        mapping = await self._to_mapping(auction)
        now_value = to_tr_aware(now) if now else now_tr()
        if now_value is None:
            now_value = now_tr()

        computed_price, details = price_service.compute_current_price(mapping, now=now_value)
        current_price = mapping.get("currentPrice")
        auction_id = getattr(auction, "id", None)

        if auction_id is not None and (current_price is None or Decimal(str(current_price)) != Decimal(str(computed_price))):
            auction = await db.auction.update(
                where={"id": auction_id},
                data={"currentPrice": computed_price}
            )

            if emit_event and auction is not None:
                await socket_service.emit_price_update(
                    auction_id=getattr(auction, "id", auction_id),
                    current_price=str(computed_price),
                    details=details or {},
                )

        return auction

    async def _check_and_update_status(self, auction) -> object:
        if not auction:
            return None

        now = now_tr()
        start_time = to_tr_aware(getattr(auction, "startTime", None))
        end_time = to_tr_aware(getattr(auction, "endTime", None))

        if not start_time or not end_time:
            return auction

        updated = False
        new_status = auction.status

        if auction.status == "DRAFT" and start_time <= now < end_time:
            new_status = "ACTIVE"
            updated = True
        elif auction.status == "ACTIVE" and now >= end_time:
            new_status = "EXPIRED"
            updated = True
        elif auction.status == "DRAFT" and now >= end_time:
            new_status = "EXPIRED"
            updated = True

        if updated:
            auction = await db.auction.update(
                where={"id": auction.id},
                data={"status": new_status}
            )

        return auction

    async def create_auction(self, data: dict):
        data = self._apply_backend_pricing_policy(data)
        is_valid, error_msg = auction_validator.validate_auction_create(data)
        if not is_valid:
            raise ValidationError(error_msg)

        drop_amount = data.get("drop_amount")
        turbo_drop = data.get("turbo_drop_amount")
        if turbo_drop is None:
            turbo_drop = drop_amount if drop_amount is not None else Decimal("0.00")

        return await db.auction.create(
            data={
                "title": data.get("title"),
                "description": data.get("description"),
                "startPrice": data.get("start_price"),
                "floorPrice": data.get("floor_price"),
                "currentPrice": data.get("start_price"),
                "startTime": data.get("start_time"),
                "endTime": data.get("end_time"),
                "dropIntervalMins": data.get("drop_interval_mins", 60),
                "dropAmount": drop_amount if drop_amount is not None else Decimal("0.00"),
                "turboEnabled": data.get("turbo_enabled", False),
                "turboTriggerMins": data.get("turbo_trigger_mins", 120),
                "turboDropAmount": turbo_drop,
                "turboIntervalMins": data.get("turbo_interval_mins", 10),
            }
        )

    async def get_auction(self, auction_id: int):
        auction = await db.auction.find_unique(where={"id": auction_id})
        if auction:
            auction = await self._check_and_update_status(auction)
            auction = await self._sync_current_price(auction)
        return auction

    async def check_pending_auctions(self):
        try:
            items = await db.auction.find_many(
                where={
                    "status": {
                        "in": ["DRAFT", "ACTIVE"]
                    }
                }
            )
            for item in items:
                checked = await self._check_and_update_status(item)
                await self._sync_current_price(checked, emit_event=True)
            return len(items)
        except Exception as e:
            print(f"Error checking pending auctions: {e}")
            return 0

    async def list_auctions(self, include_computed: bool = False, now=None):
        try:
            items = await db.auction.find_many(order={"startTime": "asc"})
        except TypeError:
            items = await db.auction.find_many()

        normalized_now = to_tr_aware(now) if now else None

        updated_items = []
        for item in items:
            checked = await self._check_and_update_status(item)
            checked = await self._sync_current_price(checked)
            updated_items.append(checked)
        items = updated_items

        if not include_computed:
            return items

        out = []
        for item in items:
            mapping = await self._to_mapping(item)
            price, details = price_service.compute_current_price(mapping, now=normalized_now)
            out.append({
                "id": mapping.get("id"),
                "title": mapping.get("title"),
                "description": mapping.get("description"),
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
                "status": item.status,
                "computedPrice": str(price),
                "priceDetails": details,
                "currentPrice": mapping.get("currentPrice"),
                "created_at": getattr(item, "createdAt", None),
                "updated_at": getattr(item, "updatedAt", None),
            })
        return out

    async def update_auction(self, auction_id: int, data: dict):
        existing = await db.auction.find_unique(where={"id": auction_id})
        if not existing:
            return None

        merged_for_validation = {
            "title": getattr(existing, "title", None),
            "description": getattr(existing, "description", None),
            "start_price": getattr(existing, "startPrice", None),
            "floor_price": getattr(existing, "floorPrice", None),
            "start_time": getattr(existing, "startTime", None),
            "end_time": getattr(existing, "endTime", None),
            "drop_interval_mins": getattr(existing, "dropIntervalMins", None),
            "drop_amount": getattr(existing, "dropAmount", None),
            "turbo_enabled": getattr(existing, "turboEnabled", False),
            "turbo_trigger_mins": getattr(existing, "turboTriggerMins", auction_validator.TURBO_TRIGGER_MINS_FIXED),
            "turbo_drop_amount": getattr(existing, "turboDropAmount", None),
            "turbo_interval_mins": getattr(existing, "turboIntervalMins", auction_validator.TURBO_INTERVAL_MINS_FIXED),
        }
        for key, value in data.items():
            if value is not None:
                merged_for_validation[key] = value

        merged_for_validation = self._apply_backend_pricing_policy(merged_for_validation)
        is_valid, error_msg = auction_validator.validate_auction_create(merged_for_validation)
        if not is_valid:
            raise ValidationError(error_msg)

        mapping = {
            "title": "title",
            "description": "description",
            "start_time": "startTime",
            "end_time": "endTime",
            "start_price": "startPrice",
            "floor_price": "floorPrice",
            "drop_interval_mins": "dropIntervalMins",
            "drop_amount": "dropAmount",
            "turbo_enabled": "turboEnabled",
            "turbo_trigger_mins": "turboTriggerMins",
            "turbo_interval_mins": "turboIntervalMins",
            "turbo_drop_amount": "turboDropAmount",
        }

        update_data = {}
        for key, value in data.items():
            if key in mapping and value is not None:
                update_data[mapping[key]] = value

        # Enforce backend fixed turbo policy in persisted data as well
        turbo_enabled = merged_for_validation.get("turbo_enabled", False)
        update_data["turboTriggerMins"] = auction_validator.TURBO_TRIGGER_MINS_FIXED
        update_data["turboIntervalMins"] = auction_validator.TURBO_INTERVAL_MINS_FIXED
        if not turbo_enabled:
            update_data["turboDropAmount"] = Decimal("0.00")

        if not update_data:
            return None

        return await db.auction.update(
            where={"id": auction_id},
            data=update_data
        )

    async def _to_mapping(self, auction_obj) -> dict:
        def g(attr):
            return getattr(auction_obj, attr, None)

        return {
            "id": g("id"),
            "title": g("title"),
            "description": g("description"),
            "startPrice": g("startPrice") or g("start_price"),
            "floorPrice": g("floorPrice") or g("floor_price"),
            "currentPrice": g("currentPrice") or g("current_price"),
            "startTime": g("startTime") or g("start_time"),
            "endTime": g("endTime") or g("end_time"),
            "dropIntervalMins": g("dropIntervalMins") or g("drop_interval_mins"),
            "dropAmount": g("dropAmount") or g("drop_amount"),
            "turboEnabled": g("turboEnabled") or g("turbo_enabled"),
            "turboTriggerMins": g("turboTriggerMins") or g("turbo_trigger_mins"),
            "turboDropAmount": g("turboDropAmount") or g("turbo_drop_amount"),
            "turboIntervalMins": g("turboIntervalMins") or g("turbo_interval_mins"),
        }

    async def get_current_price(self, auction_id: int, now=None):
        auction = await db.auction.find_unique(where={"id": auction_id})
        if not auction:
            return None
        mapping = await self._to_mapping(auction)
        normalized_now = to_tr_aware(now) if now else None
        price, details = price_service.compute_current_price(mapping, now=normalized_now)
        return {"price": str(price), "details": details}

    async def check_and_trigger_turbo(self, auction_id: int, now: Optional[datetime] = None):
        now_value = to_tr_aware(now) if now else now_tr()
        if now_value is None:
            now_value = now_tr()

        auction = await db.auction.find_unique(where={"id": auction_id})
        if not auction:
            return {"triggered": False, "reason": "auction_not_found", "turbo_started_at": None}

        turbo_enabled = getattr(auction, "turboEnabled", False) or getattr(auction, "turbo_enabled", False)
        if not turbo_enabled:
            return {"triggered": False, "reason": "turbo_not_enabled", "turbo_started_at": None}

        turbo_started_at = getattr(auction, "turboStartedAt", None)
        if turbo_started_at is not None:
            return {
                "triggered": False,
                "reason": "turbo_already_triggered",
                "turbo_started_at": turbo_started_at,
            }

        end_time = getattr(auction, "endTime", None) or getattr(auction, "end_time", None)
        end_time = to_tr_aware(end_time)
        if end_time is None:
            return {"triggered": False, "reason": "invalid_end_time", "turbo_started_at": None}

        remaining_min = (end_time - now_value).total_seconds() / 60
        turbo_trigger_mins = getattr(auction, "turboTriggerMins", None) or getattr(auction, "turbo_trigger_mins", 120)

        if remaining_min <= turbo_trigger_mins:
            await db.auction.update(
                where={"id": auction_id},
                data={"turboStartedAt": now_value}
            )
            await socket_service.emit_turbo_triggered(
                auction_id=auction_id,
                turbo_started_at=now_value,
                remaining_minutes=round(remaining_min, 2),
            )
            return {
                "triggered": True,
                "reason": "turbo_condition_met",
                "turbo_started_at": now_value,
                "remaining_minutes": round(remaining_min, 2),
            }

        return {
            "triggered": False,
            "reason": "turbo_condition_not_met",
            "turbo_started_at": None,
            "remaining_minutes": round(remaining_min, 2),
        }


auction_service = AuctionService()
