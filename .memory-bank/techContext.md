# Teknoloji Bağlamı (Tech Context)

## Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| ORM / DB | Prisma Client Python, PostgreSQL |
| Realtime | Socket.IO AsyncServer + socket.io-client |
| Görev Zamanlayıcı | APScheduler (interval, 60s) |
| Auth | JWT (jose), refresh token, Redis revocation (opsiyonel) |
| E-posta | fastapi-mail, SMTP (Gmail) |
| Frontend | Vue 3 (Composition API), Pinia, Vue Router |
| Stil | Tailwind CSS v4, PostCSS |
| Build | Vite |
| Test | pytest (backend), Vitest + @vue/test-utils (frontend) |

## Kritik Teknik Kurallar

### API / Fetch
- View içinde ham `fetch()` yasaktır (R5 sonrası kural).
- Tüm API çağrıları `adminFetch` (admin) veya `authStore.fetchWithAuth()` (kullanıcı) üzerinden geçer.
- 401 alındığında `fetchWithAuth()` otomatik refresh token deneme → başarısızsa `logout()`.

### State Yönetimi
- **Local state:** loading, error, pagination → composable içinde `ref()`.
- **Global state:** Auth token, user, auction socket → Pinia store.

### Vue 3 Kuralları
- `<script setup>` zorunlu; Options API / `export default { setup() }` yasaktır.
- `onMounted`'da eklenen event listener `onUnmounted`'da mutlaka kaldırılır.

### Auth / Token
- `ACCESS_TOKEN_EXPIRE_MINUTES=2880` (2 gün)
- `REFRESH_TOKEN_EXPIRE_DAYS=7`
- Revocation: Redis varsa Redis blacklist (TTL=refresh süresi), yoksa in-memory fallback.

### Redis (Opsiyonel)
- Aktif etmek için: `.env` içinde `REDIS_URL=redis://localhost:6379/0`.
- Boş bırakıldığında uygulama in-memory fallback ile çalışır (tek worker ortamı için yeterli).
- Health kontrolü: `GET /health` → `"redis": "available" | "unavailable"`.
- Gelecek aktif etme tetikleyicileri: çoklu worker, session revocation tutarsızlığı, yüksek kullanıcı sayısı.
