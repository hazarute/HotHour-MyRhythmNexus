# Sistem Mimarisi (System Patterns)

## Genel Mimari
HotHour; backend'de API-first FastAPI, frontend'de Vue 3 + Pinia SPA mimarisine sahiptir. İletişim REST API ve Socket.IO (gerçek zamanlı fiyat/statü akışı) üzerinden yürütülür.

## Temel Pattern'lar

### 1. Centralized Domain Metadata
Durum (status) etiketleri, renkler ve formatlama tek bir dosyadan import edilir. View içinde inline tanım yasaktır.
- `src/utils/formatters.js` → Tarih/saat/para formatlama
- `src/utils/reservationStatus.js` → Rezervasyon statü haritası
- `src/utils/admin/status_metadata.js` → Admin açık artırma/rezervasyon statü haritası

### 2. Composable Split Pattern
iş mantığı (fetch, state, validasyon) view'dan ayrılarak composable'lara taşınmıştır:
- `composables/useAuctionSocket.js` — socket abonelik yaşam döngüsü
- `composables/useReservations.js` — rezervasyon fetch/cancel/copy
- `composables/usePasswordStrength.js` — şifre gücü hesaplama
- `composables/admin/useAdminAuctions.js`, `useAdminReservations.js`, `useAdminNotifications.js`

### 3. Admin API Fetch Abstraction
Admin API çağrıları `utils/admin/api_client.js` içindeki `adminFetch()` üzerinden geçer; auth token ve baseUrl otomatik eklenir.

### 4. Centralized Auth Flow (fetchWithAuth)
Kullanıcı API çağrıları `authStore.fetchWithAuth()` kullanır:
- Authorization header otomatik eklenir.
- 401 alındığında `/auth/refresh` denenir; başarısızsa `logout()`.

### 5. Redis-Opsiyonel Revocation Pattern
Refresh-token revocation için lazy Redis client kullanılır (`app/core/redis_client.py`):
- `REDIS_URL` tanımlıysa → Redis blacklist (TTL = refresh token süresi).
- `REDIS_URL` boşsa → in-memory set (tek process için yeterli).
- `/health` endpoint'i Redis ping durumunu raporlar.

### 6. Health Check Pattern
`GET /health` endpoint'i load balancer / orkestratör için temel sağlık bilgisi döner:
```json
{ "status": "active", "version": "...", "project": "...", "redis": "available|unavailable" }
```

### 7. Vue Component Decomposition
Büyük view'lar parçalanırken parent-child iletişimi `defineProps` / `defineEmits` ile yapılır. 2 seviyeden derin veri taşıma gerekirse Composable veya `provide/inject` kullanılır.
