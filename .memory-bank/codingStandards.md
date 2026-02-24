# Kodlama Standartları (Coding Standards)

## 1. Genel Prensipler
* **Tip Güvenliği (Type Safety):** * Backend'de Python Type Hints ve Pydantic aktif olarak kullanılacak. `Any` kullanımından kaçınılacak.
  * Frontend'de (eğer TypeScript kullanılmayacaksa) Vue `props` tanımlamalarında tip (type) ve zorunluluk (required) belirtilecek.
* **Asenkron Programlama:** FastAPI ve Prisma Client'ın `async/await` özellikleri kullanılacak. Bloklayan I/O işlemlerinden kaçınılacak.
* **Temiz Kod (Clean Code):** Fonksiyonlar ve Vue bileşenleri (components) tek bir işi yapmalı (Single Responsibility). Dev devasa dosyalar yerine küçük, yeniden kullanılabilir modüller tercih edilecek.
* **Dokümantasyon:** Karmaşık iş mantığı içeren fonksiyonlar (özellikle fiyat algoritması) docstring / yorum satırı ile açıklanacak.

## 2. İsimlendirme Kuralları

### Backend (Python)
* **Değişkenler ve Fonksiyonlar:** `snake_case` (örn: `calculate_current_price`)
* **Sınıflar (Class):** `PascalCase` (örn: `AuctionService`)
* **Sabitler (Constants):** `UPPER_SNAKE_CASE` (örn: `DEFAULT_DROP_INTERVAL`)
* **Dosya İsimleri:** `snake_case` (örn: `auction_router.py`)

### Frontend (Vue 3 & JS/TS)
* **Bileşenler (Components):** `PascalCase` ve çok kelimeli (örn: `PriceTicker.vue`, `BookButton.vue`).
* **Değişkenler ve Fonksiyonlar:** `camelCase` (örn: `fetchAuctions`, `currentPrice`).
* **Pinia Stores:** `use` önekiyle `camelCase` (örn: `useAuctionStore.js`).
* **Tailwind Sınıfları:** Standart Tailwind isimlendirmeleri kullanılacak, özel (custom) CSS yazılacaksa `.css` dosyasında BEM metodolojisi tercih edilecek.

## 3. Frontend (Vue 3) Geliştirme Standartları
* **Composition API:** Tüm yeni bileşenler Vue 3 `<script setup>` syntax'ı kullanılarak yazılacaktır. Seçenekler API'si (Options API) kullanılmayacaktır.
* **State Yönetimi (Pinia):** Global veriler (aktif açık artırmalar, kullanıcı oturumu) Pinia'da tutulacak. Sadece tek bir bileşeni ilgilendiren anlık veriler (modal'ın açık/kapalı olması vb.) bileşen içinde `ref` veya `reactive` ile yönetilecek.
* **WebSocket Lifecycle:** Socket bağlantıları bileşen ekrana çizildiğinde (`onMounted`) açılmalı ve bileşen ekrandan kalktığında (`onUnmounted`) bellek sızıntısını (memory leak) önlemek için mutlaka kapatılmalı/dinleme bırakılmalıdır.

## 4. API ve WebSocket Standartları
* **REST Endpoint'ler Kaynak Odaklı Olmalı:**
  * `GET /api/v1/auctions`
  * `POST /api/v1/reservations`
* **Status Kodları Doğru Kullanılmalı:**
  * `200 OK`: Başarılı okuma
  * `201 Created`: Başarılı oluşturma
  * `400 Bad Request`: Validasyon hatası
  * `404 Not Found`: Kaynak yok
  * `409 Conflict`: Çakışma (örn: zaten satılmış seans - Race Condition)
* **WebSocket Event İsimlendirmeleri:** `snake_case` kullanılacak.
  * Backend emit: `price_update`, `turbo_triggered`
  * Frontend emit: `subscribe_auction`

## 5. Validasyon Deseni (Validation Pattern)
* **Backend Utility Katmanı:** `app/utils/validators.py` içinde `Validator` sınıfları oluşturulmalı.
* **Statik Metodlar:** Validasyon metodları `@staticmethod` olarak yazılmalı (testlenmesi kolay).
* **Custom Exception:** İş mantığı hatalarında `ValidationError` istisnası fırlatılıp API katmanında 400 (`HTTPException`) cevabına dönüştürülmeli.
* **Frontend Validasyonu:** Kullanıcı deneyimini artırmak için form hataları backend'e gitmeden önce önyüzde (Vue tarafında) yakalanıp kullanıcıya gösterilmeli.

## 6. Commit Mesajları
* Türkçe veya İngilizce olabilir, ancak tutarlı olmalı.
* Format: `TÜR(KAPSAM): Açıklama`
  * `FEAT(API): Yeni rezervasyon endpointi eklendi`
  * `FEAT(UI): Hemen Kap butonu ve loading state eklendi`
  * `FIX(Core): Fiyat hesaplama hatası düzeltildi`
  * `DOCS: README güncellendi`
  * `CHORE: Bağımlılıklar güncellendi`