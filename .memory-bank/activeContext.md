# Aktif Bağlam (Active Context)

## Şu Anki Odak
**Faz 2.5: Turbo Modu Trigger Mekanizması (✅ Tamamlandı)**

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
        - `app/utils/validators.py` (AuctionValidator sınıfı + timezone fix)
        - Unit test: 26 ✓ | Integration test: 4 ✓
    *   **✅ Turbo Modu Trigger Mekanizması (7 test geçiyor)**
        - `AuctionService.check_and_trigger_turbo()` methodu
        - Turbo koşulu: `remaining_min <= turbo_trigger_mins`
        - Idempotent trigger (yeniden tetiklenmiyor)
        - `POST /api/v1/auctions/{id}/trigger-turbo` endpoint'i
        - Prisma: `turboStartedAt` field ve `@default` values
        - Validator: timezone-aware datetime comparisons

*   **Bekleyen:**
    *   Reservation Sistemi (Faz 3): "Hemen Kap" & Race Condition.

## Test Durumu
*   **Turbo Trigger Tests:** 7/7 ✅ (test_turbo_trigger.py)
*   **Auction Tests:** 2/2 ✅ (test_auctions.py)
*   **Computed Price:** 1/1 ✅ (test_auctions_computed.py)
*   **Toplam:** 41 test geçiyor

## Sıradaki Görevler
1.  Reservation Sistemi (Faz 3): "Hemen Kap" (Booking) mantığı.
2.  Race Condition yönetimi (Concurrent booking).
3.  Booking Code üretimi ve geçmişi.
