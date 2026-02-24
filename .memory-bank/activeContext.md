# Aktif Bağlam (Active Context)

## Şu Anki Odak
**Faz 2: Açık Artırma (Auction) Yönetimi (Validasyon ✓)**

## Mevcut Durum
*   **Tamamlanan:**
    *   Auth ve Kullanıcı Yönetimi (Gender eklendi).
    *   Auction CRUD (Admin create, Public list).
    *   Async Test Altyapısı (Clean architecture w/ pytest-asyncio).
    *   GitHub initial push ("Initial release - Auth, Auctions CRUD, and Clean Async Test Infrastructure").
    *   Fiyat Hesaplama Motoru (`app/services/price_service.py`) ve unit testleri.
    *   `price_service` `auction_service` ile entegre edildi; `include_computed` desteği.
    *   Entegrasyon testi ve CI workflow eklendi.
    *   Test Prisma shim eklendi (env kontrollü).
    *   **✅ Auction Validasyon Kuralları (30 test geçiyor)**
        - Fiyat: startPrice > floorPrice, tüm pozitif, dropAmount limit
        - Zaman: startTime < endTime, endTime future, dropInterval uygun
        - Turbo: turbo_drop_amount, turbo_interval_mins kuralları
        - `app/utils/validators.py` (AuctionValidator sınıfı)
        - Unit test: 26 ✓ | Integration test: 4 ✓
*   **Bekleyen:**
    *   Turbo Modu trigger mekanizması.
    *   Reservation Sistemi (Faz 3).

## Test Durumu
*   **Test Suite:** `tests/test_auth.py` ve `tests/test_auctions.py`
*   **Durum:** ✅ Geçiyor (Async Client, Function scope fixture)
*   **Kapsam:** Register, Login, Admin Create Auction, Non-Admin Reject.

## Sıradaki Görevler
1.  Turbo Modu Trigger Mekanizması (açık artırma sırasında fiyat hızlanır).
2.  Reservation Sistemi (Faz 3): "Hemen Kap" ve Race Condition yönetimi.
3.  Booking Code üretimi ve geçmişi.
