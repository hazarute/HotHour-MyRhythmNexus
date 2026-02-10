from fastapi import APIRouter, Depends, status
from app.models.auction import AuctionCreate, AuctionResponse
from app.services.auction_service import auction_service
from app.core.deps import get_current_admin_user

router = APIRouter()


@router.post("/", response_model=AuctionResponse, status_code=status.HTTP_201_CREATED)
async def create_auction(auction_in: AuctionCreate, admin=Depends(get_current_admin_user)):
    auction = await auction_service.create_auction(auction_in.model_dump())
    return {
        "id": auction.id,
        "title": auction.title,
        "description": auction.description,
        "start_price": auction.startPrice,
        "floor_price": auction.floorPrice,
        "start_time": auction.startTime,
        "end_time": auction.endTime,
        "drop_interval_mins": auction.dropIntervalMins,
        "drop_amount": auction.dropAmount,
        "status": auction.status,
    }


@router.get("/", response_model=list[AuctionResponse])
async def list_auctions():
    items = await auction_service.list_auctions() if hasattr(auction_service, "list_auctions") else []
    mapped = []
    for a in items:
        mapped.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "start_price": a.startPrice,
            "floor_price": a.floorPrice,
            "start_time": a.startTime,
            "end_time": a.endTime,
            "drop_interval_mins": a.dropIntervalMins,
            "drop_amount": a.dropAmount,
            "status": a.status,
        })
    return mapped
