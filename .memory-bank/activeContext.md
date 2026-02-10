# Aktif Bağlam (Active Context)

## Şu Anki Odak
**Faz 2: Açık Artırma (Auction) Yönetimi.**
Kullanıcı altyapısı (Auth) tamamlandı. Şimdi projenin ana fonksiyonu olan Açık Artırma mekanizmasına (CRUD) geçiyoruz.

**Son Yapılan İşlem:**
*   `DEĞİŞİKLİKLERİ İŞLE` protokolü uygulandı.
*   Auth sistemi (JWT, Login, Register) tamamlandı ve Swagger üzerinden test edilebilir durumda.
*   `.memory-bank` dosyaları güncel durum ile senkronize edildi.
*   `Gender` enum'u eklendi ve `User` modeline nullable `gender` alanı eklendi.
*   `app/models/user.py` Pydantic modelleri güncellendi (`Gender` enum ve `gender: Optional[Gender]`).
*   `prisma db push` ile şema veritabanına aktarıldı ve `prisma generate` ile Python client oluşturuldu (virtualenv içindeki `prisma-client-py` kullanıldı).
*   Gerekli paketler virtualenv içerisine yüklendi: `prisma-client-py`, `email-validator`, `python-jose`, `passlib[bcrypt]`, `bcrypt`.
*   `tests/test_auth.py::test_register_and_login` testi venv içinde çalıştırıldı ve geçti.
*   Auction altyapısı eklendi:
    *   `app/models/auction.py` — `AuctionCreate` ve `AuctionResponse` Pydantic modelleri.
    *   `app/services/auction_service.py` — `create_auction` ve `list_auctions` servisleri (Prisma kullanıyor).
    *   `app/api/auctions.py` — `POST /api/v1/auctions` (Sadece Admin), `GET /api/v1/auctions` (Public placeholder).
    *   `app/core/deps.py` — `get_current_user` ve `get_current_admin_user` dependency'leri (JWT doğrulama + role kontrol).
    *   `app/main.py` içinde auctions router eklendi.
*   Tüm testler venv içinde çalıştırıldı ve mevcut testler geçti.
*   **Test Altyapısı Yenilendi (Clean Approach):**
    *   Testler `pytest-asyncio` ve `AsyncClient` (httpx) kullanacak şekilde tamamen asenkron yapıya geçirildi.
    *   Test yardımcıları (`create_user_in_db` vb.) doğrudan async prisma çağrıları kullanıyor.
    *   `Fixture` scope hataları giderildi (`function` scope kullanılıyor).
    *   Test veritabanı bağlantısı `db_connect` fixture'ı ile her test için güvenli hale getirildi.

## Sıradaki Adımlar
1.  **Auction Modelleri ve İş Mantığı:**
    *   `POST /auctions` için eksik iş mantığı validasyonları (zaman aralığı, fiyat kuralları).
    *   `AuctionUpdate` ve `AuctionBase` genişletmeleri.
2.  **Auction Servisi (`app/services/auction_service.py`):**
    *   Açık artırma detay (GET /{id}), güncelleme ve silme.
    *   Turbo drop mantığının planlanması.
3.  **API Endpointleri (`app/api/auctions.py`):**
    *   `POST /auctions` (Sadece Admin - *Role kontrolü eklenecek*)
    *   `GET /auctions` (Public)

## Yeni Öncelikler
- `POST /auctions` artık admin-only olarak eklendi; bir sonraki adım admin-only testleri eklemek.
- Auction iş mantığı validasyonları (zaman aralığı, fiyat kuralları, turbo modu) uygulanmalı.

## Riskler ve Notlar
*   Admin yetkilendirmesi henüz kodlanmadı. İlk etapta herkes açık artırma oluşturabilir durumda olacak, sonrasında `Role.ADMIN` kontrolü eklenemeli.

