# Teknoloji Bağlamı (Tech Context)

## Teknoloji Yığını

Proje, API-First yaklaşımıyla tasarlanmış olup, backend ve frontend bileşenleri birbirinden bağımsız olarak çalışır ancak WebSocket ve REST API'ler üzerinden sıkı bir şekilde haberleşir.

| Kategori | Bileşen | Teknoloji | Versiyon / Notlar |
| --- | --- | --- | --- |
| **Backend** | Dil | Python | 3.10+ |
| **Backend** | Framework | FastAPI | `fastapi>=0.109.0`, Asenkron yapı |
| **Backend** | Server | Uvicorn | `uvicorn[standard]` |
| **Database** | Veritabanı | PostgreSQL | 15 (Docker Image: `postgres:15-alpine`) |
| **Database** | ORM | Prisma Client Python | `v0.15.0`, `enable_experimental_decimal=true` |
| **Security** | Auth & Şifreleme | Python-Jose, Bcrypt | JWT tabanlı kimlik doğrulama, Password Hashing |
| **Config** | Çevresel Değişkenler | Pydantic Settings | `.env` tabanlı konfigürasyon yönetimi |
| **Real-time** | WebSocket Engine | Socket.io | Backend: `AsyncServer`, Frontend: `socket.io-client` (Aktif) |
| **Testing** | Async Client Transport | aiohttp | `aiohttp>=3.10.0` (Socket.io `AsyncClient` entegrasyon testleri için gerekli) |
| **Frontend** | Core Framework | Vue.js | Vue 3 (Composition API) |
| **Frontend** | Build Tool | Vite | Hızlı modül değişimi (HMR) ve derleme |
| **Frontend** | Styling | Tailwind CSS | v4.2+ (PostCSS integration: `@tailwindcss/postcss`) |
| **Frontend** | State Management | Pinia | Global durum yönetimi (Açık artırma verileri, Auth state) |
| **Frontend** | Routing | Vue Router | SPA navigasyon yönetimi |
| **DevOps** | Container | Docker Compose | Veritabanı hizmeti (Port: 5433) |

## Geliştirme Ortamı Kurulumu

Proje iki ana dizinden (veya ayrı depolardan) oluşur: `backend` ve `frontend`.

### 1. Backend Kurulumu (Python/FastAPI)

1.  **Python Virtual Env:**
    ```bash
    python -m venv venv
    # Windows: .\venv\Scripts\Activate
    # macOS/Linux: source venv/bin/activate
    ```

2.  **Bağımlılıklar:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Veritabanı (Docker):**
    ```bash
    docker-compose up -d
    # Port: 5433 (Default 5432 çakışmasını önlemek için)
    ```

4.  **Prisma Kurulumu:**
    ```bash
    # Şemayı DB'ye bas
    prisma db push
    
    # Client oluştur (Terminal UTF-8 modunda olmalı)
    # Windows PowerShell için: $env:PYTHONUTF8="1"
    prisma generate
    ```

### 2. Frontend Kurulumu (Vue 3 / Vite)

1.  **Bağımlılıkların Yüklenmesi:**
    Node.js (v18+) yüklü olduğundan emin olun.
    ```bash
    cd frontend
    npm install
    # veya yarn install / pnpm install
    ```

2.  **Geliştirme Sunucusunu Başlatma:**
    ```bash
    npm run dev
    # Genellikle http://127.0.0.1:5173 adresinde ayağa kalkar
    ```

3. **Frontend API URL (Önerilen):**
   `frontend/.env` içinde backend adresini sabitleyin:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```

## CI ve Test Notları

- Proje için basit bir GitHub Actions workflow eklendi: `.github/workflows/ci.yml` (testleri çalıştırır).
- Lokal test çalıştırma sırasında Prisma client yüklü değilse repo içinde test-ortamı için bir "fake Prisma" shim (`app/core/db.py`) bulunur. Bu shim pytest ortamında otomatik devreye girer; prod ortamında gerçek `prisma.Prisma` kullanılmalıdır.

## Konfigürasyon Kuralları
* **Decimal Tipi:** Prisma Python Client'ta `enable_experimental_decimal` özelliği aktif edilmelidir. Frontend tarafında bu veriler string veya float olarak karşılanıp doğru şekilde (virgülden sonra 2 hane) formatlanmalıdır.
* **Encoding:** Windows ortamında `schema.prisma` dosyasında ASCII dışı karakterlerden (emojiler, Türkçe karakterler) kaçınılmalı veya encoding doğru ayarlanmalıdır.
* **Authentication:** `SECRET_KEY` mutlaka `.env` dosyasından okunmalı, hardcode edilmemelidir.
* **CORS:** Backend `.env` içinde `BACKEND_CORS_ORIGINS` geçerli JSON liste formatında verilmelidir (örn: `http://127.0.0.1:5173`).
* **Host Tutarlılığı:** Bu projede lokal geliştirmede `localhost` yerine `127.0.0.1` kullanımı tercih edilir (frontend-backend bağlantı kararlılığı için).

## Veri Modeli Notları (Prisma)
* User tablosu `email` ve `phone` alanlarını unique tutar.
* `Auction` tablosu fiyatlandırma motorunun kalbidir.
    * Decimal tipler para birimi hassasiyeti için kullanılır (`@db.Decimal(10, 2)`).
    * Enumlar (`AuctionStatus`, `PaymentStatus`) durum yönetimini sıkı tutar.
* `Reservation` tablosu `auctionId` ile `User` arasında köprüdür ve 1-1 ilişki ile tekilliği garanti eder (Race Condition koruması).