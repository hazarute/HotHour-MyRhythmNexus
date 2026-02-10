# Sistem Mimarisi (System Patterns)

## Mimari Genel Bakış
Sistem, modern bir **Micro-SaaS** mimarisi izlemektedir. Backend öncelikli olarak Python/FastAPI üzerine kuruludur ve veri tutarlılığı için güçlü bir SQL veritabanı (PostgreSQL) kullanır.

### Diyagram
```mermaid
graph TD
    User((Kullanıcı))
    Admin((Stüdyo Yöneticisi))

    subgraph "HotHour Core"
        API[Backend API<br/>(FastAPI)]
        WS[WebSocket Engine<br/>(Socket.io)]
        Prisma[Prisma Client Py]
        DB[(PostgreSQL)]
    end

    User -- "HTTP (Rezervasyon)" --> API
    User -- "WS (Canlı Fiyat)" --> WS
    Admin -- "HTTP (Seans Girişi)" --> API
    API -- "ORM Queries" --> Prisma
    Prisma -- "SQL" --> DB
    WS -- "Fiyat Broadcast" --> FE(Frontend)
    API -- "Turbo Mod Tetikleyici" --> WS
```

## Temel Tasarım Desenleri

### 1. API First Design
*   Tüm iş mantığı FastAPI endpoint'leri üzerinden sunulur.
*   Frontend (Vue.js) tamamen API tüketicisidir.

### 2. Gerçek Zamanlı Fiyatlandırma Motoru
*   Fiyat hesaplaması veritabanında saklanan konfigürasyona (`startPrice`, `dropInterval`, `startTime` vb.) göre dinamik olarak yapılır veya bir background job (Celery/APScheduler - *belirlenecek*) tarafından periyodik olarak güncellenir.
*   *Not: Mevcut yapıda Prisma modelinde `currentPrice` alanı var, bu alanın senkronizasyonu kritik.*

### 3. Yarış Durumu (Race Condition) Yönetimi
*   `Reservation` tablosundaki `auctionId` alanı `@unique` olarak tanımlanmıştır.
*   Aynı anda iki kişi aynı seansa "Kap" dediğinde, veritabanı seviyesinde işlem bütünlüğü (transaction) sağlanmalı ve sadece ilk gelen işlem başarılı olmalıdır.

### 4. Code-First ORM
*   Veritabanı şeması `prisma/schema.prisma` dosyasında tanımlanır.
*   `app/core/db.py` içinde global bir Singleton `Prisma` instance'ı oluşturulur.
*   FastAPI `lifespan` eventleri ile uygulama başlangıcında `connect`, kapanışında `disconnect` yapılır.

### 5. Güvenlik Mimarisi
*   **JWT (JSON Web Token):** Stateless authentication için kullanılır.
*   **Password Hashing:** `bcrypt` algoritması ile şifreler veritabanında hashli tutulur.
*   **Servis Katmanı:**
    *   `UserService`: Veritabanı ve CRUD işlemleri.
    *   `AuthService` (Planlanan): Token üretimi ve iş mantığı.

## Klasör Yapısı (Gerçekleşen)
```
.
├── app/
│   ├── main.py            # Uygulama ve Router tanımları
│   ├── api/               # Endpoint'ler (Örn: auth.py)
│   ├── core/              # Config, Security, DB
│   ├── services/          # İş mantığı (UserService)
│   ├── models/            # Pydantic modelleri (UserCreate, Token)
│   └── utils/             # Yardımcı araçlar
├── prisma/
│   └── schema.prisma      # DB Şeması (ASCII Only)
├── .env                   # Çevresel değişkenler
└── docker-compose.yml     # PostgreSQL servisi
```
