# Sistem Mimari Desenleri (System Patterns)

## Genel Mimari
- Backend: FastAPI + Prisma + Socket.IO + APScheduler
- Frontend: Vue 3 + Pinia + Vite
- Veri: PostgreSQL + Redis

## Temel Katmanlar
- `app/api`: endpoint ve auth sınırı
- `app/services`: iş mantığı
- `app/models`: request/response şemaları
- `app/core`: config, db, security, scheduler, realtime altyapı
- `frontend/src/views`: sayfalar
- `frontend/src/composables`: UI iş mantığı
- `frontend/src/stores`: global state

## v1.5 Çekirdek Deseni
- tenant çekirdeği: `Studio`
- işletme sınıflandırması: `Sector` + `StudioSector`
- fırsat sınıflandırması: `ServiceCategory` + `Auction.serviceCategoryId`

## Kurumsal Yönetim Deseni
- `ADMIN` tenant yöneticisidir
- taxonomy master data owner tarafından script ile yönetilir
- panelde serbest taxonomy yazımı yoktur
- işletme sektörleri panelden düzenlenmez

## Veri Sunum Deseni
- işletme seviyesi sektör ile fırsat seviyesi hizmet kategorisi ayrı tutulur
- include stratejileri endpoint ihtiyacına göre seçilir
- liste ve detay ekranlarında yalnızca gerekli nested ilişkiler döndürülür

## Filtreleme Deseni
- kalıcı kaynak backend filtreleridir
- ana eksenler: `status`, `sector`, `service_category`, metin arama
- frontend query param senkronizasyonu korunur

## Terminoloji Deseni
- teknik isimler korunur: `Studio`, `Auction`, `studioId`
- ürün metinlerinde: `işletme`, `fırsat`, `hizmet`

## Güncel Mimari Öncelik
Yeni büyük refactor eklemekten çok, yapılan köklü değişikliklerin birbirini bozmadan çalışmasını korumak.
