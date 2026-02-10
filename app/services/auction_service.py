from app.core.db import db


class AuctionService:
    async def create_auction(self, data: dict):
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


auction_service = AuctionService()
