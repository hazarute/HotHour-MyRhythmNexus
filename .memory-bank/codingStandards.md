# Kodlama Standartları (Coding Standards)

## Genel Prensipler
1.  **Tip Güvenliği:** Python Type Hits (Pydantic) aktif olarak kullanılacak. `Any` kullanımından kaçınılacak.
2.  **Asenkron Programlama:** FastAPI ve Prisma Client'ın `async/await` özellikleri kullanılacak. Bloklayan I/O işlemlerinden kaçınılacak.
3.  **Temiz Kod:** Fonksiyonlar tek bir işi yapmalı (Single Responsibility).
4.  **Dokümantasyon:** Karmaşık iş mantığı içeren fonksiyonlar docstring ile açıklanacak.

## İsimlendirme Kuralları
*   **Değişkenler ve Fonksiyonlar:** `snake_case` (örn: `calculate_current_price`)
*   **Sınıflar (Class):** `PascalCase` (örn: `AuctionService`)
*   **Sabitler (Constants):** `UPPER_SNAKE_CASE` (örn: `DEFAULT_DROP_INTERVAL`)
*   **Dosya İsimleri:** `snake_case` (örn: `auction_router.py`)

## API Standartları (REST)
*   Endpoint'ler kaynak odaklı olmalı:
    *   `GET /auctions`
    *   `POST /auctions`
    *   `POST /reservations`
*   Status kodları doğru kullanılmalı:
    *   `200 OK`: Başarılı okuma
    *   `201 Created`: Başarılı oluşturma
    *   `400 Bad Request`: Validasyon hatası
    *   `404 Not Found`: Kaynak yok
    *   `409 Conflict`: Çakışma (örn: zaten satılmış seans)

## Validasyon Deseni (Validation Pattern)
*   **Utility Katmanı:** `app/utils/validators.py` içinde `Validator` sınıfları oluşturulmalı.
*   **Statik Metodlar:** Validasyon metodları `@staticmethod` olarak yazılmalı (testlenmesi kolay).
*   **Custom Exception:** `ValidationError` istisnası kaldırılmalı ve 400 cevabı verilmeli.
*   **Entegrasyon:** Servis katmanı (`create_auction`) validasyon çağrısı yapıp exception'ı raise etmeli.
*   **Error Handling:** API endpoint'leri `try-except` ile `ValidationError`'ı yakalamalı ve HTTPException 400 vermelidir.
*   **Test Stratejisi:**
    - **Unit:** `tests/test_validators.py` - İş mantığını test et
    - **Integration:** `tests/test_*_integration.py` - API endpoint'lerini test et

## Commit Mesajları
*   Türkçe veya İngilizce olabilir, ancak tutarlı olmalı.
*   Format: `TÜR: Açıklama`
    *   `FEAT: Yeni rezervasyon endpointi eklendi`
    *   `FIX: Fiyat hesaplama hatası düzeltildi`
    *   `DOCS: README güncellendi`
    *   `CHORE: Bağımlılıklar güncellendi`
