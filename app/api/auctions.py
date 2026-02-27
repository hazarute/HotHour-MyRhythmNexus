from fastapi import APIRouter, Depends, status, Query, HTTPException, Path
from app.models.auction import AuctionCreate, AuctionUpdate, AuctionResponse
from app.services.auction_service import auction_service
from app.services import socket_service
from app.core.deps import get_current_admin_user
from app.utils.validators import ValidationError

router = APIRouter()


@router.post("/", response_model=AuctionResponse, status_code=status.HTTP_201_CREATED)
async def create_auction(auction_in: AuctionCreate, admin=Depends(get_current_admin_user)):
    try:
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
            "created_at": getattr(auction, "createdAt", None),
            "updated_at": getattr(auction, "updatedAt", None)
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{auction_id}", response_model=AuctionResponse)
async def update_auction(
    auction_in: AuctionUpdate,
    auction_id: int = Path(..., gt=0),
    admin=Depends(get_current_admin_user)
):
    try:
        updated = await auction_service.update_auction(auction_id, auction_in.model_dump())
        if not updated:
            raise HTTPException(status_code=404, detail="Auction not found")
            
        return {
            "id": updated.id,
            "title": updated.title,
            "description": updated.description,
            "start_time": updated.startTime,
            "end_time": updated.endTime,
            "start_price": updated.startPrice,
            "floor_price": updated.floorPrice,
            "drop_interval_mins": updated.dropIntervalMins,
            "drop_amount": updated.dropAmount,
            "turbo_enabled": updated.turboEnabled,
            "turbo_trigger_mins": updated.turboTriggerMins,
            "turbo_drop_amount": updated.turboDropAmount,
            "turbo_interval_mins": updated.turboIntervalMins,
            "status": updated.status,
            "current_price": updated.currentPrice,
            "created_at": getattr(updated, "createdAt", None),
            "updated_at": getattr(updated, "updatedAt", None)
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[AuctionResponse])
async def list_auctions(include_computed: bool = Query(False, description="Include computedPrice and priceDetails")):
    # preserve backward-compatible default behavior
    items = await auction_service.list_auctions(include_computed=include_computed) if hasattr(auction_service, "list_auctions") else []
    mapped = []
    for a in items:
        # if service returned DB objects (not computed), keep original mapping
        if not isinstance(a, dict):
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
                "current_price": a.currentPrice if hasattr(a, 'currentPrice') else a.startPrice,
                "created_at": a.createdAt,
                "updated_at": a.updatedAt
            })
        else:
            # item already contains computed fields from service
            # If currentPrice or computedPrice is in the dict, map it to current_price
            current_p = a.get("computedPrice") or a.get("currentPrice") or a.get("start_price")
            mapped.append({
                "id": a.get("id"),
                "title": a.get("title"),
                "description": a.get("description"),
                "start_price": a.get("start_price"),
                "floor_price": a.get("floor_price"),
                "start_time": a.get("start_time"),
                "end_time": a.get("end_time"),
                "drop_interval_mins": a.get("drop_interval_mins"),
                "drop_amount": a.get("drop_amount"),
                "status": a.get("status"),
                "computedPrice": a.get("computedPrice"),
                "priceDetails": a.get("priceDetails"),
                "current_price": current_p,
                "created_at": a.get("created_at"),
                "updated_at": a.get("updated_at")
            })
    return mapped


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(auction_id: int = Path(..., gt=0)):
    auction = await auction_service.get_auction(auction_id)
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
        
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
        "turbo_enabled": auction.turboEnabled,
        "turbo_trigger_mins": auction.turboTriggerMins,
        "turbo_drop_amount": auction.turboDropAmount,
        "turbo_interval_mins": auction.turboIntervalMins,
        "status": auction.status,
        "current_price": auction.currentPrice,
        "created_at": getattr(auction, "createdAt", None),
        "updated_at": getattr(auction, "updatedAt", None)
    }


@router.post("/{auction_id}/trigger-turbo", status_code=status.HTTP_200_OK)
async def trigger_turbo_mode(auction_id: int = Path(..., gt=0)):
    """
    Check if turbo mode should be triggered for the given auction.
    If conditions are met, triggers turbo mode and returns the result.
    
    Args:
        auction_id: The ID of the auction
        
    Returns:
        dict with keys: triggered, reason, turbo_started_at, remaining_minutes
    """
    result = await auction_service.check_and_trigger_turbo(auction_id)
    if result["reason"] == "auction_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )
    return result


@router.post("/{auction_id}/broadcast-price", status_code=status.HTTP_200_OK)
async def broadcast_current_price(
    auction_id: int = Path(..., gt=0),
    admin=Depends(get_current_admin_user),
):
    """
    Admin endpoint: compute and broadcast the current price of an auction
    to all Socket.io subscribers of that auction room.

    Useful for:
    - Manual price refresh triggers
    - Scheduled background tasks calling this via internal HTTP
    - Testing real-time price updates

    Returns:
        {"auction_id": int, "current_price": str, "broadcast": true}
    """
    price_result = await auction_service.get_current_price(auction_id)
    if price_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )

    await socket_service.emit_price_update(
        auction_id=auction_id,
        current_price=price_result["price"],
        details=price_result.get("details") or {},
    )

    return {
        "auction_id": auction_id,
        "current_price": price_result["price"],
        "broadcast": True,
    }