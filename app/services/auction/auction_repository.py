from typing import Optional, List, Dict, Any

from app.core.db import db, connect_db
from app.services.studio_service import studio_service

# Müzayedeleri çekerken varsayılan olarak Prisma'dan istenecek ilişkiler (joins)
DEFAULT_INCLUDES = {
    "studio": {
        "include": {
            "sectors": {
                "include": {"sector": True}
            }
        }
    },
    "serviceCategory": {
        "include": {"sector": True}
    },
    "reservation": True,
}


class AuctionRepository:
    """
    Müzayede (Auction) tablosu için doğrudan Prisma veritabanı işlemlerini,
    ilişki (relation) yamalarını ve sorgu filtrelerini yöneten Repository katmanı.
    Tamamen iş mantığından (business logic) arındırılmış saf Data Access Layer'dır.
    """

    @staticmethod
    async def service_category_exists(service_category_id: int) -> bool:
        """Verilen ID'ye sahip aktif bir hizmet kategorisi olup olmadığını kontrol eder."""
        categories = await db.servicecategory.find_many(
            where={"id": service_category_id, "isActive": True},
            take=1,
        )
        return len(categories) > 0

    @staticmethod
    async def attach_missing_relations(auction: Any) -> Any:
        """
        FakePrisma (Unit testler) veya eksik veritabanı join'lerinde ilişkileri 
        manuel bağlayarak uygulamanın "NoneType" hataları almasını önler.
        """
        if not auction:
            return auction

        studio_id = getattr(auction, "studioId", None)
        if getattr(auction, "studio", None) is None and studio_id is not None:
            try:
                studio = await studio_service.get_studio_with_sectors(studio_id)
                auction.studio = studio
            except Exception:
                pass

        cat_id = getattr(auction, "serviceCategoryId", None)
        if getattr(auction, "serviceCategory", None) is None and cat_id is not None:
            try:
                cat = await db.servicecategory.find_unique(where={"id": cat_id})
                if cat:
                    if getattr(cat, "sector", None) is None and getattr(cat, "sectorId", None) is not None:
                        sec = await db.sector.find_unique(where={"id": getattr(cat, "sectorId")})
                        cat.sector = sec
                auction.serviceCategory = cat
            except Exception:
                pass

        return auction

    @staticmethod
    async def find_many_auctions_with_reconnect(where: Optional[Dict] = None, order: Optional[Dict] = None) -> List[Any]:
        """
        Özel mekanizması sayesinde Prisma bağlantısı koparsa otomatik olarak `connect_db()` dener
        ve sonuçları eksik ilişkiyaması yapılarak (attach_missing_relations) döndürür.
        """
        if order is None:
            order = {"startTime": "asc"}
        try:
            auctions = await db.auction.find_many(
                where=where,
                order=order,
                include=DEFAULT_INCLUDES
            )
            return [await AuctionRepository.attach_missing_relations(a) for a in auctions]
        except Exception as exc:
            error_text = str(exc).lower()
            if "connect" not in error_text and "connection" not in error_text:
                raise
            await connect_db()
            auctions = await db.auction.find_many(
                where=where,
                order=order,
                include=DEFAULT_INCLUDES
            )
            return [await AuctionRepository.attach_missing_relations(a) for a in auctions]

    @staticmethod
    def matches_sector_filter(auction: Any, sector_slug: Optional[str]) -> bool:
        """Liste çekerken müzayedenin sektör slug'ı ile eşleşip eşleşmediğini test eder."""
        if not sector_slug:
            return True
        studio = getattr(auction, "studio", None)
        if not studio:
            return False
        for link in (getattr(studio, "sectors", []) or []):
            sector = getattr(link, "sector", None)
            if sector and getattr(sector, "slug", None) == sector_slug:
                return True
        return False

    @staticmethod
    def matches_service_category_filter(auction: Any, service_category_slug: Optional[str]) -> bool:
        """Liste çekerken müzayedenin hizmet kategorisi slug'ı ile eşleşip eşleşmediğini test eder."""
        if not service_category_slug:
            return True
        category = getattr(auction, "serviceCategory", None)
        return bool(category and getattr(category, "slug", None) == service_category_slug)

    @staticmethod
    def matches_allowed_gender_filter(auction: Any, allowed_gender: Optional[str]) -> bool:
        """Liste çekerken müzayedenin katılımcı kuralı ile eşleşip eşleşmediğini test eder."""
        if not allowed_gender:
            return True

        normalized_filter = str(allowed_gender).upper()
        auction_allowed_gender = str(getattr(auction, "allowedGender", "ANY") or "ANY").upper()
        return auction_allowed_gender == normalized_filter


auction_repository = AuctionRepository()
