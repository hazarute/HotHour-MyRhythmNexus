# Teknoloji Bağlamı (Tech Context)

## Stack
- Backend: Python, FastAPI, Prisma, Socket.IO, APScheduler, Redis
- Frontend: Vue 3, Vite, Pinia, Tailwind
- Veri: PostgreSQL

## Güncel Veri Modeli
- `Studio`: tenant çekirdeği
- `Sector`: işletme seviyesi taxonomy
- `StudioSector`: `Studio <-> Sector`
- `ServiceCategory`: fırsat seviyesi hizmet taxonomy
- `Auction.serviceCategoryId`: fırsatın hizmet kimliği

## Çalıştırma
- backend: `uvicorn app.main:app --reload`
- frontend: `npm run dev`
- test/komutlar lokal `.env` ve yerel veritabanı üzerinden yürütülür

## Script Stratejisi
- taxonomy yönetimi `scripts/taxonomy/` altındadır
- seed akışı: `clear_db.py` -> `seed_taxonomy.py --update-existing` -> `seed_auctions.py` -> opsiyonel `create_admin.py`
- varsayılan reset akışı artık heuristic backfill'e dayanmaz

## Seed Kuralı
- seed deterministiktir
- rastgele işletme/kategori dağıtımı yapılmaz
- her fırsat doğru `serviceCategoryId` ile kurulur
- bir fırsatın kategorisi, bağlı işletmenin sektörlerinden biriyle uyumlu olmalıdır

## Yetki ve Operasyon
- `ADMIN` mevcut taxonomy kayıtlarını kullanır
- owner master data'yı CLI ile yönetir
- canlı rollout şu aşamada hedef değil; lokal manuel test önceliklidir

## Teknik Dikkat Noktaları
- relation include'ları Pydantic response ile uyumlu tutulmalı
- tenant izolasyonu her endpoint'te korunmalı
- frontend fetch akışlarında `response.ok` ve `response.json()` disiplini korunmalı
