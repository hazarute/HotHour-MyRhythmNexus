# Kodlama Standartları (Coding Standards)

## Genel Mimari
- Bir Vue dosyasının `<script>` bölümü 100-150 satırı aşıyorsa ilgili logic bir Composable'a taşınır.
- Modüller gevşek bağlı (loosely coupled) olmalıdır.
- Refactor sonrasında mevcut iş kuralları (race condition, status, iptal akışı vb.) bozulmamalıdır.

## İsimlendirme Kuralları

### Frontend
- **Composables:** `use` ön eki + CamelCase → `useAdminNotifications.js`
- **Utils/Helpers:** camelCase → `formatters.js`, `reservationStatus.js`
- **Alt Bileşenler:** Parent adını referans alan PascalCase → `AdminNotificationDropdown.vue`

### Backend
- **Servisler:** `snake_case` → `auction_service.py`, `booking_service.py`
- **Modeller:** `snake_case` dosya, PascalCase sınıf → `class AuctionResponse`
- **Endpointler:** REST, kebab-case URL → `/api/v1/auth/refresh`

## Vue 3 Standartları
- `<script setup>` zorunlu; Options API yasaktır.
- Sadece gerçekten reaktif olan veriler `ref()` / `reactive()` kullanır; sabit metadata düz obje olarak export edilir.
- `onMounted`'da eklenen her listener `onUnmounted`'da temizlenir.

## API / Fetch Standartları
- Ham `fetch()` view içinde yasaktır (R5 kuralı).
- Admin: `adminFetch(path, options?)` kullanılır.
- Kullanıcı: `authStore.fetchWithAuth(path, options?)` kullanılır — 401 otomatik refresh içerir.
- `!response.ok` her durumda yakalanır ve uygun hata state'ine yazılır.

## Formatlama ve Metadata
- Tarih/saat/para formatlama: `src/utils/formatters.js` (tek kaynak).
- Rezervasyon statü haritası: `src/utils/reservationStatus.js` (tek kaynak).
- Inline format tanımlaması kesinlikle yapılmaz.

## Test Standartları
- Backend: `pytest` — her yeni endpoint veya servis değişikliği için test yazılır.
- Frontend: `vitest` — her yeni composable/store için unit test yazılır.
- Test komutları:
  - Backend: `$env:PYTHONPATH="..."; pytest -q`
  - Frontend: `npm --prefix frontend run test:unit`
