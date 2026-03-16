from decimal import Decimal
from typing import Dict, Any, Tuple

from app.models.enums import Gender
from app.utils.validators import ValidationError, auction_validator

class AuctionMapper:
    """
    Müzayede (Auction) servisi için veri dönüşüm ve haritalama sınıfı.
    Gelen request payload'larını veritabanı modeline veya veritabanı modelini 
    sözlüklere (dict) çevirmekle yükümlüdür. İş mantığı içermemesi hedeflenmiştir.
    """

    @staticmethod
    def apply_backend_pricing_policy(data: dict) -> dict:
        """Turbo ve fiyatlandırma ile ilgili güvenlik kurallarına uygun veriyi haritalar."""
        normalized = dict(data)
        turbo_enabled = bool(normalized.get("turbo_enabled", False))

        normalized["turbo_trigger_mins"] = auction_validator.TURBO_TRIGGER_MINS_FIXED
        normalized["turbo_interval_mins"] = auction_validator.TURBO_INTERVAL_MINS_FIXED
        if not turbo_enabled:
            normalized["turbo_drop_amount"] = Decimal("0.00")

        return normalized

    @staticmethod
    def validate_and_merge_auction_data(data: dict, existing=None, force_full_validation=False) -> Tuple[bool, dict]:
        """
        API'den gelen karmaşık veri ve mevcut veriyi birleştirir.
        Gerekirse AuctionValidator'ü çağırarak alanları test eder.
        """
        validation_sensitive_fields = {
            "start_price", "floor_price", "start_time", "end_time",
            "drop_interval_mins", "drop_amount", "turbo_enabled",
            "turbo_trigger_mins", "turbo_drop_amount", "turbo_interval_mins",
        }

        should_run_full_validation = force_full_validation or any(
            field in data and data.get(field) is not None
            for field in validation_sensitive_fields
        )

        merged = {}
        if should_run_full_validation:
            if existing:
                merged = {
                    "title": getattr(existing, "title", None),
                    "description": getattr(existing, "description", None),
                    "allowed_gender": getattr(existing, "allowedGender", Gender.ANY.value),
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
                    merged[key] = value

            merged = AuctionMapper.apply_backend_pricing_policy(merged)
            is_valid, error_msg = auction_validator.validate_auction_create(merged)
            if not is_valid:
                raise ValidationError(error_msg)

        return should_run_full_validation, merged

    @staticmethod
    def prepare_create_data(merged: dict) -> dict:
        """python_case formatlı sözlüğü camelCase Prisma Create sözlüğüne çevirir."""
        drop_amount = merged.get("drop_amount")
        turbo_drop = merged.get("turbo_drop_amount")
        if turbo_drop is None:
            turbo_drop = drop_amount if drop_amount is not None else Decimal("0.00")

        return {
            "title": merged.get("title"),
            "description": merged.get("description"),
            "allowedGender": merged.get("allowed_gender", Gender.ANY.value),
            "startPrice": merged.get("start_price"),
            "floorPrice": merged.get("floor_price"),
            "currentPrice": merged.get("start_price"),
            "startTime": merged.get("start_time"),
            "endTime": merged.get("end_time"),
            "scheduledAt": merged.get("scheduled_at") or merged.get("end_time"),
            "dropIntervalMins": merged.get("drop_interval_mins", 60),
            "dropAmount": drop_amount if drop_amount is not None else Decimal("0.00"),
            "turboEnabled": merged.get("turbo_enabled", False),
            "turboTriggerMins": merged.get("turbo_trigger_mins", 120),
            "turboDropAmount": turbo_drop,
            "turboIntervalMins": merged.get("turbo_interval_mins", 10),
        }

    @staticmethod
    def prepare_update_data(data: dict, merged_for_validation: dict, should_run_full_validation: bool) -> dict:
        """python_case formatlı sözlüğü camelCase Prisma Update sözlüğüne çevirir."""
        mapping_keys = {
            "title": "title", "description": "description", "allowed_gender": "allowedGender", "status": "status",
            "serviceCategoryId": "serviceCategoryId", "start_time": "startTime", "end_time": "endTime",
            "start_price": "startPrice", "floor_price": "floorPrice", "drop_interval_mins": "dropIntervalMins",
            "drop_amount": "dropAmount", "turbo_enabled": "turboEnabled", "turbo_trigger_mins": "turboTriggerMins",
            "turbo_interval_mins": "turboIntervalMins", "turbo_drop_amount": "turboDropAmount"
        }

        update_data = {attr_name: data[key] for key, attr_name in mapping_keys.items() if key in data and data[key] is not None}
        
        if "serviceCategoryId" in data and data.get("serviceCategoryId") is None:
            update_data["serviceCategoryId"] = None

        if should_run_full_validation:
            turbo_enabled = merged_for_validation.get("turbo_enabled", False)
            update_data["turboTriggerMins"] = auction_validator.TURBO_TRIGGER_MINS_FIXED
            update_data["turboIntervalMins"] = auction_validator.TURBO_INTERVAL_MINS_FIXED
            if not turbo_enabled:
                update_data["turboDropAmount"] = Decimal("0.00")
                
        return update_data

    @staticmethod
    def to_mapping(auction_obj: Any) -> dict:
        """Prisma nesnesini iç işleyişte (price_engine vb) kullanılacak sözlüğe çevirir."""
        def g(attr):
            return getattr(auction_obj, attr, None)
        return {
            "id": g("id"),
            "title": g("title"),
            "description": g("description"),
            "allowedGender": g("allowedGender") or g("allowed_gender") or Gender.ANY.value,
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
            "serviceCategoryId": g("serviceCategoryId") or g("service_category_id"),
        }

auction_mapper = AuctionMapper()
