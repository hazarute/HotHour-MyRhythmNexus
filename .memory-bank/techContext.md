# Teknoloji Bağlamı (Tech Context)

## Teknoloji Yığını

| Bileşen | Teknoloji | Versiyon / Notlar |
| --- | --- | --- |
| **Dil** | Python | 3.10+ |
| **Framework** | FastAPI | `fastapi>=0.109.0`, Asenkron |
| **Server** | Uvicorn | `uvicorn[standard]` |
| **Veritabanı** | PostgreSQL | 15 (Docker Image: `postgres:15-alpine`) |
| **ORM** | Prisma Client Python | `v0.15.0`, `enable_experimental_decimal=true` |
| **Security** | Python-Jose, Bcrypt | JWT, Password Hashing |
| **Config** | Pydantic Settings | `.env` yönetimi |
| **Real-time** | Socket.io | (AsyncServer) - Henüz entegre edilmedi |
| **Container** | Docker Compose | Veritabanı hizmeti (Port: 5433) |

## Geliştirme Ortamı Kurulumu

1.  **Python Virtual Env:**
    ```bash
    python -m venv venv
    # Windows: .\venv\Scripts\Activate
    ```

2.  **Bağımlılıklar:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Veritabanı:**
    ```bash
    docker-compose up -d
    # Port: 5433 (Default 5432 çakışmasını önlemek için)
    ```

4.  **Prisma Kurulumu:**
    ```bash
    # Şemayı DB'ye bas
    prisma db push
    
    # Client oluştur (Terminal UTF-8 modunda olmalı)
    $env:PYTHONUTF8="1"
    prisma generate
    ```

## Konfigürasyon Kuralları
*   **Decimal Tipi:** Prisma Python Client'ta `enable_experimental_decimal` özelliği aktif edilmelidir.
*   **Encoding:** Windows ortamında `schema.prisma` dosyasında ASCII dışı karakterlerden (emojiler, Türkçe karakterler) kaçınılmalı veya encoding doğru ayarlanmalıdır.
*   **Authentication:** `SECRET_KEY` mutlaka `.env` dosyasından okunmalı, hardcode edilmemelidir.

## Veri Modeli Notları (Prisma)
*   User tablosu `email` ve `phone` alanlarını unique tutar.
*   `Auction` tablosu fiyatlandırma motorunun kalbidir.
    *   Decimal tipler para birimi hassasiyeti için kullanılır (`@db.Decimal(10, 2)`).
    *   Enumlar (`AuctionStatus`, `PaymentStatus`) durum yönetimini sıkı tutar.
*   `Reservation` tablosu `auctionId` ile `User` arasında köprüdür ve 1-1 ilişki ile tekilliği garanti eder.
