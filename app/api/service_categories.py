from fastapi import APIRouter, HTTPException, Query, status

from app.models.service_category import ServiceCategoryResponse
from app.services.service_category_service import service_category_service


router = APIRouter()


@router.get("", response_model=list[ServiceCategoryResponse])
async def list_service_categories(
    active_only: bool = Query(True, description="Sadece aktif hizmet kategorilerini getir"),
    sector_slug: str | None = Query(None, description="Belirli bir sektöre ait hizmet kategorilerini filtrele"),
):
    try:
        return await service_category_service.list_service_categories(
            active_only=active_only,
            sector_slug=sector_slug,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hizmet kategorileri getirilirken hata oluştu: {str(e)}"
        )