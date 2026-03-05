# Sistem Mimari Desenleri (System Patterns)

## Genel Mimari
- **Backend:** FastAPI (Python) - RESTful API & WebSockets.
- **Frontend:** Vue 3 (Composition API) Vite ile derlenen, Pinia mağazası ve Vue Router içeren Tek Sayfa Uygulaması (SPA).
- **Veritabanı:** PostgreSQL (Prisma ORM ile bağlanır).
- **Önbellek & Pub/Sub:** Redis (Socket.io mesajlaşması ve performans için).

## Katmanlar (Backend)
- `app/api/`: Sadece endpoint'leri barındırır, yetkilendirme (`Depends`) işlemleri yapılır.
- `app/services/`: Tüm iş mantığı (Business Logic) burada çalışır. API katmanından soyutlanmıştır. CRUD, bildirimler, Socket yollamaları buradadır.
- `app/models/`: Pydantic V2 ile Request/Response doğrulamaları. Prisma tipleri ile olan uyumsuzluklar için (örn. `from_attributes=True`) önemlidir.
- `app/core/`: Scheduler (Zamanlanmış görevler), Security, Redis entegrasyonu, DB bağlantıları.

## Katmanlar (Frontend)
- `src/views/`: Ana sayfalar (Admin, Müşteri).
- `src/composables/`: Sayfalara ait iş/UI mantığını sarmalar. (Örn: `useAdminAuctions.js`). Vue Composition API kuralları geçerlidir.
- `src/stores/`: Pinia global durum yönetimi (Auth, UI, Realtime veriler).
- `src/services/` & `src/utils/`: Socket istemci bağlantısı ve tarih/para formatlama araçları.

## Kritik Akışlar (AI İçin Not)
- **Asenkron Veri (Fetch/JSON):** Frontend'deki Pinia `authStore.fetchWithAuth` geriye saf `Response` objesi döner. Composable içinde DAİMA `await response.json()` ile işlenmelidir, aksi takdirde veriler undefined olur.
- **Fiyat Motoru:** `apscheduler` döngüsünde `update_auction_prices` çalışır. Herhangi bir "fiyat düşmüyor" şikayetinde `core/scheduler.py` ve `services/price_service.py` modülleri incelenmelidir.
- **Prisma & Pydantic Uyumsuzluğu:** Prisma'nın döneceği `Include` (ilişkili veriler - ör: Auction -> Studio) işlemlerini Pydantic response modellerinde (Örn. `StudioResponse=None`) titizlikle nullable tanımlanmalıdır.
