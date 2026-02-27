# HotHour ⏳🔥

[![CI Status](https://img.shields.io/github/actions/workflow/status/hothour/core/main?style=flat-square&logo=github)](https://github.com/hothour/core/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![ORM](https://img.shields.io/badge/Prisma-Client-blueviolet?style=flat-square&logo=prisma)](https://prisma.io)
[![License](https://img.shields.io/badge/License-Noncommercial-orange.svg?style=flat-square)](./LICENSE)

> **"Boş Seans Yok, Maksimum Verim."**
> Pilates stüdyoları ve randevu bazlı işletmeler için "Dinamik Hollanda Açık Artırması" (Dutch Auction) ve "Fırsat Yönetimi" (Yield Management) platformu.

---

## 🏗 Mimari Özeti ve Sistem Akışı

HotHour, atıl kapasiteyi gelire dönüştürmek için oyunlaştırılmış (gamified) bir fiyatlandırma motoru kullanır. Sistem, "Hemen Kap" (Booking) mantığı üzerine kuruludur ve online ödeme bariyerini kaldırarak **"Rezervasyon Yap & Yerinde Ödeme"** modelini benimser.

Aşağıdaki **Teknik Mimari**, sistemin veri akışını özetlemektedir:

```mermaid
graph TD
    User((Kullanıcı))
    Admin((Stüdyo Yöneticisi))

    subgraph "HotHour Core"
        FE[Frontend SPA<br/>(Vue.js + Tailwind)]
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
    WS -- "Fiyat Broadcast" --> FE
    API -- "Turbo Mod Tetikleyici" --> WS

```

## 🎯 Proje Özeti (Project Overview)

**Problem:** Pilates stüdyoları, özellikle hafta içi 10:00 - 17:00 saatleri arasında boş kalan seansları (Dead Inventory) satmakta zorlanmaktadır.

**Çözüm:** HotHour, bu seansları belirlenen bir tavan fiyattan başlatıp, taban fiyata doğru **gerçek zamanlı** olarak düşürür. Kullanıcıda yaratılan "Fırsatı Kaçırma Korkusu" (FOMO), dönüşüm oranlarını artırır.

## ✨ Temel Özellikler (Key Features)

* **📉 Dinamik Hollanda Açık Artırması:** Fiyatlar admin tarafından belirlenen aralıklarla (örn: her 30 dakikada bir) otomatik olarak düşer.
* **🔥 Turbo Mode (Sıcak Saat):** Seansın başlamasına (örn: 2 saat) az kaldığında devreye giren agresif algoritma. Fiyat düşüş hızı artar (örn: her dakika 3₺) ve arayüzde görsel uyarıcılar devreye girer.
* **⚡ Hemen Kap (Instant Booking):** "Yarış Durumu" (Race Condition) korumalı rezervasyon sistemi. Butona ilk basan fiyatı kilitler (`lockedPrice`) ve seansı kapatır.
* **🤝 Yerinde Ödeme (Pay-at-Venue):** Kredi kartı zorunluluğu yoktur. Sistem benzersiz bir **Rezervasyon Kodu** (örn: `HOT-8X2A`) üretir; ödeme stüdyoda fiziksel olarak yapılır.
* **📊 Prisma ORM Entegrasyonu:** Karmaşık SQL sorguları yerine, tip güvenli (type-safe) ve modern veritabanı yönetimi.

## 🛠 Teknoloji Yığını (Tech Stack)

Proje, modern ve ölçeklenebilir bir Micro-SaaS mimarisine uygun olarak tasarlanmıştır.

| Kategori | Teknoloji | Açıklama |
| --- | --- | --- |
| **Backend** | Python, FastAPI | Asenkron, yüksek performanslı API. |
| **Database** | PostgreSQL | Ana veri saklama alanı. |
| **ORM** | **Prisma Client Python** | Veritabanı şeması ve migration yönetimi. |
| **Real-time** | Socket.io | Fiyat senkronizasyonu ve Turbo Mod bildirimleri. |
| **Frontend** | Vue.js / Tailwind CSS | Reaktif, mobil uyumlu ve neon temalı arayüz. |
| **Infrastructure** | Docker | Konteynerizasyon. |

## 🚀 Başlangıç Rehberi (Getting Started)

Geliştirme ortamını kurmak için aşağıdaki adımları izleyin.

### Gereksinimler (Prerequisites)

* Python 3.10+
* PostgreSQL 14+
* Node.js (Prisma CLI için gereklidir)

### Kurulum (Installation)

1. **Repoyu Klonlayın:**
```bash
git clone [https://github.com/hazarute/HotHour-MyRhythmNexus.git](https://github.com/hazarute/HotHour-MyRhythmNexus.git)
cd hothour

```


2. **Sanal Ortam ve Bağımlılıklar:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

```


3. **Çevresel Değişkenler (.env):**
```bash
cp .env.example .env
# .env dosyasındaki DATABASE_URL bilgisini düzenleyin

```


4. **Veritabanı Şeması (Prisma):**
Prisma şemasını veritabanına uygulayın ve Python client'ı oluşturun.
```bash
prisma db push
prisma generate

```


5. **Uygulamayı Başlatın:**
```bash
uvicorn main:app --reload

```


*Swagger UI:* `http://localhost:8000/docs`

## 📡 API Endpoints (Örnek)

| Metot | Endpoint | Açıklama |
| --- | --- | --- |
| `GET` | `/api/v1/auctions/live` | Şu an aktif olan ve fiyatı düşen seansları getirir. |
| `POST` | `/api/v1/reservations` | Seansı o anki fiyattan kilitler ve rezervasyon kodu üretir. |
| `POST` | `/api/v1/admin/turbo-trigger` | Manuel olarak Turbo Modu tetikler. |

## ⚖️ Lisans (License)

Bu proje, varsayılan olarak **yalnızca ticari olmayan kullanım** için lisanslanmıştır.

- ✅ Bireysel öğrenme, inceleme, deneme ve açık kaynak katkı amaçlı kullanım
- ✅ Ticari olmayan projelerde uyarlama
- ❌ Ticari kullanım, gelir elde etme amacıyla kullanım, SaaS/ürün içinde kullanım

Ticari kullanım için özel lisans gereklidir. Bu durumda lütfen benimle iletişime geçin:

- 👤 Ad Soyad: `Hazar Üte`
- 📩 E-mail: `kayraspaceinc@gmail.com`
- 📄 Detay: `COMMERCIAL-LICENSE.md`

Yasal metin için `LICENSE` dosyasına bakınız.

---

**Copyright © 2026 KayraSpace Inc.**
