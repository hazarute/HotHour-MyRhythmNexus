"""
Transparent Proxy for backward compatibility.
Bu dosya sistemdeki genel importların (from app.services.auction_service import auction_service)
bozulmaması amacıyla Auction Domain yapısına tünelleme yapar.
"""

from app.services.auction.auction_service import auction_service, AuctionAccessDeniedError

__all__ = ["auction_service", "AuctionAccessDeniedError"]
