# Aktif Bağlam (Active Context)

## Şu Anki Odak
**Faz 2: Açık Artırma (Auction) Yönetimi**

## Mevcut Durum
*   **Tamamlanan:**
    *   Auth ve Kullanıcı Yönetimi (Gender eklendi).
    *   Auction CRUD (Admin create, Public list).
    *   Async Test Altyapısı (Clean architecture w/ pytest-asyncio).
    *   GitHub initial push ("Initial release - Auth, Auctions CRUD, and Clean Async Test Infrastructure").
    *   Fiyat Hesaplama Motoru (`app/services/price_service.py`) ve unit testleri (`tests/test_price_engine.py`) eklendi ve geçiyor.
    *   `price_service` `auction_service` ile entegre edildi; API'de `include_computed` desteği eklendi.
    *   Entegrasyon testi (`tests/test_auctions_computed.py`) ve CI workflow (`.github/workflows/ci.yml`) eklendi.
    *   Testlerde kullanılmak üzere `app/core/db.py` içinde test-ortamına özel fake Prisma shim eklendi (env kontrollü).
*   **Bekleyen:**
    *   Auction validasyonları (zaman, fiyat kuralları).
    *   Turbo Modu mantığı.

## Test Durumu
*   **Test Suite:** `tests/test_auth.py` ve `tests/test_auctions.py`
*   **Durum:** ✅ Geçiyor (Async Client, Function scope fixture)
*   **Kapsam:** Register, Login, Admin Create Auction, Non-Admin Reject.

## Sıradaki Görevler
1.  Auction Validasyon Kuralları (Zaman/Fiyat mantığı).
2.  Turbo Modu Entegrasyonu (auction servis ile entegrasyon).
3.  Auction validasyon kurallarını implement edip unit/integration testlerini yazmak.
