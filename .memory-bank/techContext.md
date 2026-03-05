# Teknoloji Bağlamı (Tech Context)

## Temel Teknolojiler
- **Backend:** Python 3.11+, FastAPI, Prisma ORM (python-prisma), python-socketio, APScheduler, Redis (asyncio destekli).
- **Frontend:** Vue 3, Vite, Tailwind CSS, Pinia, socket.io-client.
- **Veritabanı:** PostgreSQL, Redis.

## Ortam ve Çalıştırma
- Proje kökünde `.env` dosyası okunur (Python `dotenv`).
- Geliştirme: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`

## Veritabanı Modeli / İlişkiler
- `User`: Admin veya Customer rollerini barındırır. Adminler `studioId` ile bir stüdyoya bağlanabilir.
- `Studio`: Ad, logo, adres barındırır. `User` ve `Auction` tablolarına bire-çok bağlıdır.
- `Auction`: "Oturumlar"dır. Başlangıç/Bitiş zamanı, Taban/Tavan fiyatı, dahil olduğu `studioId` bilgilerini tutar.
- `Reservation`: Satın alımları tutar. `userId` ve `auctionId` birleştirici kaydıdır (Pivot).

## Geliştirici Standartları & Bakım Kuralları
- FastAPI router'ında Pydantic ValidationError ('500 Internal Server') uyarısı gelirse, `include={}` (Prisma Relation) verilerinin Pydantic modelinde olup olmadığını kontrol edin.
- Frontend'deki tüm fetch isteklerinde `.catch()` ve `.ok` kontrolleri yapılarak, UI'a hata veya yükleme (loading=false) bitişi yansıtılmalıdır.
