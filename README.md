# HotHour ⏳🔥

[![CI](https://img.shields.io/github/actions/workflow/status/hazarute/HotHour-MyRhythmNexus/ci.yml?branch=main&style=flat-square&logo=github)](https://github.com/hazarute/HotHour-MyRhythmNexus/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Noncommercial-orange.svg?style=flat-square)](./LICENSE)

> **"Boş Kapasite Yok, Maksimum Verim."**
> İşletmelerin boş kalan hizmet fırsatlarını dinamik Hollanda açık artırması (Dutch Auction) modeliyle değerlendiren rezervasyon ve fiyatlandırma platformu.

---

## 🚀 Hızlı Başlangıç (Quickstart)

Backend ve frontend'i yerelde hızlıca ayağa kaldırmak için:

```bash
git clone https://github.com/hazarute/HotHour-MyRhythmNexus.git
cd HotHour-MyRhythmNexus

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
prisma generate
uvicorn app.main:app --reload
```

Frontend için ayrı terminal:

```bash
cd frontend
npm install
npm run dev
```

- API Docs: `http://localhost:8000/api/v1/docs`
- Frontend (Vite): `http://localhost:5173`

---

## 🧭 İçindekiler

- [Proje Özeti](#-proje-özeti)
- [Mimari ve Akış](#-mimari-ve-akış)
- [Temel Özellikler](#-temel-özellikler)
- [Teknoloji Yığını](#-teknoloji-yığını)
- [Kurulum](#-kurulum)
- [Yapılandırma](#️-yapılandırma)
- [Kullanım](#-kullanım)
- [API Örnekleri](#-api-örnekleri)
- [Test](#-test)
- [Yol Haritası](#-yol-haritası)
- [Katkı](#-katkı)
- [Lisans](#️-lisans)

---

## 🎯 Proje Özeti

**Problem:** Randevu ve kapasite bazlı çalışan işletmeler, özellikle gün içindeki boş kalan hizmet slotlarını (dead inventory) değerlendirmekte zorlanıyor.

**Çözüm:** HotHour fırsatları tavan fiyattan başlatır, taban fiyata doğru gerçek zamanlı düşürür ve kullanıcıda FOMO etkisi oluşturarak dönüşüm artırmayı hedefler.

**v1.5 Yönü:** Platform artık tek bir dikeyle sınırlı değil; güzellik, wellness, bakım, fizyoterapi ve benzeri hizmet işletmelerini de kapsayacak çok sektörlü bir yapıya evriliyor.

**Değer Teklifi:**
- Gerçek zamanlı fiyat düşüşü + Socket.IO senkronizasyonu
- Race-condition korumalı “ilk alan kazanır” rezervasyon akışı
- Online ödeme zorunluluğu olmadan “rezervasyon yap, işletmede öde” modeli
- Admin paneli ile operasyonel kontrol (turbo tetikleme, yayın, bildirimler)
- İşletme seviyesi sektör ve fırsat seviyesi hizmet sınıflandırması için genişlemeye uygun mimari temel

**Terminoloji Notu:** Kod tabanında teknik legacy isimler olarak `Studio`, `studioId` ve `Auction` korunabilir; ancak kullanıcıya görünen ürün dilinde `işletme`, `fırsat` ve `hizmet` terimleri tercih edilir.

## 🏗 Mimari ve Akış

```mermaid
graph TD
    User((Kullanıcı))
    Admin((İşletme Yöneticisi))

    subgraph "HotHour Core"
        FE[Frontend SPA<br/>(Vue 3 + Pinia + Tailwind)]
        API[Backend API<br/>(FastAPI)]
        WS[WebSocket Engine<br/>(Socket.IO)]
        ORM[Prisma Client Python]
        DB[(PostgreSQL)]
        REDIS[(Redis - Opsiyonel)]
    end

    User -- "HTTP" --> API
    User -- "WS" --> WS
    Admin -- "HTTP (Admin)" --> API
    API -- "ORM Query" --> ORM
    ORM -- "SQL" --> DB
    API -- "Revocation / Cache" --> REDIS
    WS -- "Price Broadcast" --> FE
```

## ✨ Temel Özellikler

- 📉 **Dinamik Hollanda Açık Artırması:** Fiyat, tanımlı aralıklarda otomatik düşer.
- 🔥 **Turbo Mode:** Fırsat başlangıcına yaklaşınca daha agresif düşüş kuralı devreye girer.
- ⚡ **Hemen Kap:** Rezervasyon anında fiyat kilitlenir (`locked_price`) ve yarış koşulu korunur.
- 🔐 **Auth-R Akışı:** Access token (2 gün) + refresh token (7 gün) + token revoke.
- 🧠 **Redis Opsiyonel Revocation:** Redis varsa merkezi blacklist, yoksa in-memory fallback.
- 📧 **E-posta Doğrulama:** Kayıt sonrası doğrulama linki ile aktivasyon.
- 🏷️ **Çok Sektörlü Genişleme Hazırlığı:** İşletme düzeyinde sektör, fırsat düzeyinde hizmet kategorisi modeline uyumlu yapı.
- 🧩 **Tenant İzolasyonu:** Admin kullanıcılar yalnızca kendi işletmelerine bağlı veri ve rezervasyonları yönetir.

## 🛠 Teknoloji Yığını

| Katman | Teknoloji |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn, Gunicorn |
| ORM / DB | Prisma Client Python, PostgreSQL |
| Realtime | Socket.IO (python-socketio + socket.io-client) |
| Scheduler | APScheduler |
| Auth | JWT (python-jose), refresh token, revoke mekanizması |
| Frontend | Vue 3, Pinia, Vue Router, Vite |
| Stil | Tailwind CSS v4 |
| Test | pytest (backend), Vitest (frontend) |
| Konteyner | Docker / Docker Compose |

## ⚙️ Kurulum

### Önkoşullar

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Prisma CLI (`npm i -g prisma`)

### 1) Repo ve backend bağımlılıkları

```bash
git clone https://github.com/hazarute/HotHour-MyRhythmNexus.git
cd HotHour-MyRhythmNexus

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Ortam değişkenleri

```bash
cp .env.example .env
```

`.env` içinde en az aşağıdaki değerleri düzenleyin:
- `DATABASE_URL`
- `SECRET_KEY`
- `FRONTEND_URL`
- SMTP ayarları (email doğrulama için)

### 3) Prisma

```bash
prisma generate
prisma db push
```

### 4) Uygulamayı çalıştırma

```bash
uvicorn app.main:app --reload
```

### 5) Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🧩 Yapılandırma

- `REDIS_URL`: Boşsa sistem token revocation için in-memory fallback ile çalışır.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Varsayılan `2880` (2 gün).
- `REFRESH_TOKEN_EXPIRE_DAYS`: Varsayılan `7`.
- `BACKEND_CORS_ORIGINS`: Frontend origin'lerini burada yönetin.
- `PAYMENTS_ENABLED`: Şu an `false` (ödeme entegrasyonu sonraki faz).

Docker ile PostgreSQL ayağa kaldırmak için:

```bash
docker compose up -d db
```

> Varsayılan compose map'i: host `5433` -> container `5432`.

## 💡 Kullanım

- API dokümantasyonu: `http://localhost:8000/api/v1/docs`
- Health kontrolü: `GET /health` (Redis durumu dahil)
- Frontend local: `http://localhost:5173`

Auth akışında frontend tarafında token yönetimi `fetchWithAuth()` üzerinden yapılır; 401 durumunda otomatik refresh denenir.

## 🧠 Domain Modeli

HotHour teknik olarak çok kiracılı bir yapı kullanır:

- `Studio`: Teknik legacy isimdir; platformdaki işletme/şube tenant'ını temsil eder.
- `Auction`: Teknik legacy isimdir; kullanıcıya sunulan fırsatı temsil eder.
- `Reservation`: Kullanıcının belirli bir fırsat için oluşturduğu rezervasyondur.

`v1.5` ile hedeflenen genişleme:

- İşletme seviyesinde çoklu sektör desteği
- Fırsat seviyesinde hizmet kategorisi desteği
- Public keşif ekranlarında sektör ve hizmet bazlı filtreleme
- Admin tarafında yalnızca ön tanımlı sektör/hizmet kayıtlarını seçme akışı

Master veri yönetimi yaklaşımı:

- Sektör ve hizmet kategorileri normal admin panelinden serbest metin olarak oluşturulmaz.
- Bu kayıtlar operasyonel script'ler ile merkezi olarak yönetilir.
- Normal admin yalnızca tanımlı kayıtları kendi işletmesine veya fırsatlarına bağlar.

## 📡 API Örnekleri

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/revoke`
- `GET /api/v1/auth/me`

### Auctions
- `GET /api/v1/auctions`
- `GET /api/v1/auctions/{auction_id}`
- `POST /api/v1/auctions/{auction_id}/trigger-turbo`
- `POST /api/v1/auctions/{auction_id}/broadcast-price` (admin)

### Reservations
- `POST /api/v1/reservations/book`
- `GET /api/v1/reservations/my/all`
- `DELETE /api/v1/reservations/{reservation_id}`
- `GET /api/v1/reservations/admin/all` (admin)

### v1.5 Hedef API Genişlemeleri
- `GET /api/v1/sectors`
- `GET /api/v1/service-categories`
- `PUT /api/v1/studios/me/sectors`
- `GET /api/v1/auctions?sector=...`
- `GET /api/v1/auctions?service_category=...`

## ✅ Test

Backend:

```bash
pytest -q
```

Frontend:

```bash
cd frontend
npm run test:unit -- --run
```

## 🗺 Yol Haritası

Mevcut odak alanları:
- Çok sektörlü veri modeli (`Sector`, `StudioSector`, `ServiceCategory`) tasarımı
- Backend filtreleme ve response genişletmeleri
- Admin tarafında ön tanımlı sektör/hizmet seçimi akışları
- Public keşif ekranında sektör ve hizmet filtreleri
- SSH/CLI tabanlı master veri yönetim script'leri
- Redis'in çok worker senaryolarında aktif kullanımı
- Opsiyonel E2E test katmanı
- Ödeme entegrasyonu (`PAYMENTS_ENABLED=true` gelecekte)

## 🤝 Katkı

Katkılar memnuniyetle karşılanır. Şu anda ayrı bir `CONTRIBUTING.md` bulunmuyor; lütfen issue açarak veya PR ile önerilerinizi paylaşın.

## ⚖️ Lisans

Bu proje varsayılan olarak **yalnızca ticari olmayan kullanım** için lisanslanmıştır.

- ✅ Bireysel öğrenme, inceleme, deneme ve açık kaynak katkı amaçlı kullanım
- ✅ Ticari olmayan projelerde uyarlama
- ❌ Ticari kullanım, gelir elde etme amacıyla kullanım, SaaS/ürün içinde kullanım

Ticari kullanım için özel lisans gereklidir:

- 👤 Hazar Üte
- 📩 kayraspaceinc@gmail.com
- 📄 Detay: `COMMERCIAL-LICENSE.md`

Yasal metin için `LICENSE` dosyasına bakınız.

---

**Copyright © 2026 KayraSpace Inc.**
