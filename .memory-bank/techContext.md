# Teknoloji Bağlamı (Tech Context)

## Güncel Teknoloji Yığını (Korunan)

| Katman | Teknoloji |
| --- | --- |
| Backend | Python 3.10+, FastAPI, Uvicorn, fastapi-mail |
| ORM/DB | Prisma Client Python, PostgreSQL |
| Realtime | Socket.IO AsyncServer + socket.io-client |
| Frontend | Vue 3 (Composition API), Pinia, Vue Router |
| Styling | Tailwind CSS (Vite/PostCSS) |
| Test | pytest (+ entegrasyon ve realtime testleri) |

## Yeniden Tasarım Fazı Teknik Kararları

### 1) “No New Core Dependency” Kuralı
- UI redesign için yeni büyük UI framework eklenmez.
- Mevcut stack (Vue + Tailwind + Pinia) korunur.

### 2) Referans Tabanlı Stil Kuralları
- Referans klasöründeki HTML/CSS örüntüsü temel alınır.
- Uygulama içinde token bazlı ortak sınıf/desen kullanımı hedeflenir.
- Inline stil çoğaltmak yerine ortak class/component yaklaşımı tercih edilir.

### 3) Host ve API Tutarlılığı
- Lokal geliştirme standardı: `127.0.0.1`
- Frontend API hedefi: `VITE_API_URL=http://127.0.0.1:8000`
- CORS yapılandırması backend `.env` ile uyumlu kalır.

### 4) Realtime Uyum
- Socket event isimleri değişmez.
- Sadece eventlerin görsel sunumu güncellenir.

### 5) Build/Test Güvencesi
- Her büyük ekran refactor adımında en az:
  - `npm run build` (frontend)
  - ilgili backend/entegrasyon testleri
  doğrulaması yapılır.

## Ekran Dönüşüm Teknik Sırası
1. Global layout + navigation token uyarlaması
2. Home + My Reservations (direct reference)
3. Login + Auction Detail (derived)
4. Admin Dashboard + Admin Create + Admin Reservations (derived)
5. Son görsel/fonksiyon regresyon turu


## Son Teknik Güncellemeler (Stabilizasyon)

### 1) Booking Güvenlik Katmanları
- Backend: `ADMIN` kullanıcılar için rezervasyon işlemi engellenir (HTTP 403).
- Frontend: Buton-level ve store-level guard birlikte uygulanır.

### 2) Realtime Durum Yayını
- `auction_booked` event’i çoklu client senaryosunda testle doğrulandı.
- `turbo_triggered` event’i Home/AllAuctions/Detail görünümlerinde canlı state güncellemesine bağlı.

### 3) Prisma Bağlantı Dayanıklılığı
- `list_auctions` endpoint akışında transient `ConnectError` durumunda reconnect + retry uygulanır.
- Amaç: kısa süreli engine/network kopmalarında kullanıcıya 500 yerine toparlanan servis davranışı sağlamak.

### 4) Test Stratejisi Güncellemesi
- Booking integration testlerinde eşzamanlı iki kullanıcı yarışı (`201 + 409`) doğrulanır.
- Admin booking yasağı için negatif entegrasyon testi eklenmiştir.
- Realtime testinde `auction_booked` ve `turbo_triggered` eventlerinin çoklu client teslimi doğrulanır.