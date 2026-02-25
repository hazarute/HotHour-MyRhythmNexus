# Sistem Mimarisi (System Patterns)

## Mimari Genel Bakış
HotHour, backend’de API-first iş mantığına sahip olup frontend katmanında Vue 3 + Pinia + Tailwind ile çalışan bir SPA’dır. Bu yeniden plan ile mimarinin backend tarafı korunur; değişim frontend sunum mimarisinde yapılır.

## Yeni Mimari Karar: Referans Tabanlı Sunum Katmanı

### 1) Canonical Reference Pattern
- Tek görsel gerçeklik kaynağı: `Referans Görseller/`
- Mevcut canonical ekranlar:
  - `HomeView.html/.png`
  - `MyReservationsView.html/.png`
- Diğer tüm ekranlar bu iki kaynaktan türetilen design tokens + layout pattern ile üretilir.

### 2) UI Tokenization Pattern
Referanslardan çıkarılacak çekirdek token grupları:
- Renk paleti: koyu arka plan, neon primary/secondary vurgular
- Tipografi: display + mono kullanım senaryoları
- Radius/Shadow/Glow: kart, buton ve durum etiketlerinde ortak standart
- Durum renkleri: live, confirmed, completed, warning/turbo

### 3) Component-Driven Refactor
Ortak görsel öğeler reusable component’lere taşınır:
- Üst navigasyon/topbar
- Glass card ve section wrapper
- CTA buton varyantları
- Durum rozetleri
- Kod/etiket blokları (rezervasyon kodu vb.)

### 4) Screen Mapping Strategy
- **Direct Reference:** Home, My Reservations
- **Derived Reference:** Login, Auction Detail, Admin Dashboard, Admin Create, Admin Reservations

Derived ekranlar, yeni işlev eklemeden sadece referans görsel diline uyarlanır.

### 5) Functional Isolation Rule
- Store, API servisleri ve router iş mantığı korunur.
- UI refactor sırasında domain logic’e müdahale edilmez.
- Hata/empty/loading durumları görsel olarak yeniden tasarlanır fakat davranış değiştirilmez.

### 6) Real-time Visual Contract
- `price_update`, `turbo_triggered`, `auction_booked`, `booking_confirmed` eventleri mevcut şekilde kalır.
- Bu eventlerin UI karşılıkları referans diline uyarlanır (renk, glow, badge, animasyon yoğunluğu).

## Akış Diyagramı (UI Refactor)
```mermaid
flowchart LR
    R[Referans Görseller] --> T[Token Çıkarımı]
    T --> C[Ortak Bileşen Refactor]
    C --> D1[Home / My Reservations]
    C --> D2[Login / Admin / Auction Detail]
    D1 --> V[Görsel & Fonksiyon Doğrulama]
    D2 --> V
```

## Mimari Sınırlar
- Backend endpointleri, veritabanı şeması ve servis kuralları bu fazda değişmeyecek.
- Yeniden tasarım fazı, yalnızca frontend görsel katman + component kompozisyonu kapsamındadır.

## Backend Patterns (Faz R3 Update)

### Auth ve Kullanıcı Yönetimi
- **JWT (Stateless):** Access token `Authorization: Bearer` header ile taşınır.
- **Pydantic & Prisma:** 
  - Request: `UserCreate`, `UserLogin` (Strict Validation)
  - Response: `Token`, `UserResponse`
  - DB: Prisma user tablosu ile tam uyumlu mapping.
- **Email Verification:**
  - Akış: `POST /register` -> Background Task (Send Mail) -> `GET /verify-email`.
  - Token: Özel `type='verification'` claim'li JWT.
  - State: `user.isVerified` varsayılan `False`.
