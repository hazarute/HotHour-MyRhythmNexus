from fastapi import APIRouter, HTTPException, Query, status

from app.models.sector import SectorResponse
from app.services.sector_service import sector_service


router = APIRouter()


@router.get("", response_model=list[SectorResponse])
async def list_sectors(active_only: bool = Query(True, description="Sadece aktif sektörleri getir")):
    try:
        return await sector_service.list_sectors(active_only=active_only)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sektörler getirilirken hata oluştu: {str(e)}"
        )