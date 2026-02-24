from app.core.db import db
from app.services.price_service import price_service
from app.utils.validators import auction_validator, ValidationError


class AuctionService:
    async def create_auction(self, data: dict):
        # Validate auction data before creation
        is_valid, error_msg = auction_validator.validate_auction_create(data)
        if not is_valid:
            raise ValidationError(error_msg)
        
        # Map incoming keys to Prisma model fields
        drop_amount = data.get("drop_amount")
        turbo_drop = data.get("turbo_drop_amount", drop_amount if drop_amount is not None else "0.00")

        auction = await db.auction.create(
            data={
                "title": data.get("title"),
                "description": data.get("description"),
                "startPrice": data.get("start_price"),
                "floorPrice": data.get("floor_price"),
                "currentPrice": data.get("start_price"),
                "startTime": data.get("start_time"),
                "endTime": data.get("end_time"),
                "dropIntervalMins": data.get("drop_interval_mins", 60),
                "dropAmount": drop_amount if drop_amount is not None else "0.00",
                "turboEnabled": data.get("turbo_enabled", False),
                "turboTriggerMins": data.get("turbo_trigger_mins", 120),
                "turboDropAmount": turbo_drop,
                "turboIntervalMins": data.get("turbo_interval_mins", 5),
            }
        )
        return auction
    
    async def list_auctions(self):
        items = await db.auction.find_many()
        return items

    async def _to_mapping(self, auction_obj) -> dict:
        # Convert DB auction object (attribute access) to a dict expected by price_service
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
        """Fetch auction by id and compute current price using `price_service`.

        Returns dict: `{"price": str, "details": {...}}` or None if auction not found.
        """
        auction = await db.auction.find_unique(where={"id": auction_id})
        if not auction:
            return None
        mapping = await self._to_mapping(auction)
        price, details = price_service.compute_current_price(mapping, now=now)
        return {"price": str(price), "details": details}

    async def list_auctions(self, include_computed: bool = False, now=None):
        """If `include_computed` is True, returns list of dicts with `computedPrice`.
        Otherwise returns DB objects (default, preserves existing behavior).
        """
        items = await db.auction.find_many()
        if not include_computed:
            return items
        out = []
        for a in items:
            mapping = await self._to_mapping(a)
            price, details = price_service.compute_current_price(mapping, now=now)
            # build a shallow mapping for API consumers
            record = {
                "id": mapping.get("id"),
                "title": mapping.get("title"),
                "description": mapping.get("description"),
                "start_price": mapping.get("startPrice"),
                "floor_price": mapping.get("floorPrice"),
                "start_time": mapping.get("startTime"),
                "end_time": mapping.get("endTime"),
                "drop_interval_mins": mapping.get("dropIntervalMins"),
                "drop_amount": mapping.get("dropAmount"),
                "status": getattr(a, "status", None),
                "computedPrice": str(price),
                "priceDetails": details,
            }
            out.append(record)
        return out


auction_service = AuctionService()
