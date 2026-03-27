# Foundation

## Proje Ozeti
HotHour (MyRhythmNexus), bos kalan hizmet kapasitesini dinamik Hollanda acik artirmasi mantigiyla degerlendiren cok kiracili bir rezervasyon platformudur. Platform, gercek zamanli fiyat dususu, ilk alan kazanir rezervasyon akisi ve admin tenant izolasyonu uzerine kuruludur. Sistem `v1.0`dan beri Railway uzerinde canli olarak calismakta, `v1.5`e gecis ise hizmet kesintisi olmadan surdurulmustur. Teknik legacy isimler olan `Studio`, `Auction` ve `studioId` korunur; urun dilinde ise `isletme`, `firsat` ve `hizmet` terimleri tercih edilir.

## Teknoloji Yigini
- Backend: Python 3.11+, FastAPI, Uvicorn, Gunicorn
- ORM ve Veri Erisimi: Prisma Client Python, Prisma CLI
- Veritabani: PostgreSQL 14+
- Realtime: python-socketio / Socket.IO
- Zamanlama: APScheduler
- Kimlik Dogrulama: JWT tabanli access token + refresh token + revoke akisi
- Cache ve Revocation: Redis, Redis yoksa in-memory fallback
- Frontend: Vue 3, Pinia, Vue Router, Vite
- Stil: Tailwind CSS v4, PostCSS
- Test: pytest, Vitest
- Konteyner ve Ortam: Docker, Docker Compose

## Sistem Mimarisi
- Frontend SPA, FastAPI backend ile HTTP uzerinden haberlesir ve canli fiyat/veri guncellemeleri icin Socket.IO kullanir.
- Backend, Prisma Client Python uzerinden PostgreSQL ile konusur.
- Auth modeli access token, refresh token ve token revoke mekanizmasi ile calisir.
- Redis varsa merkezi token revoke ve cache altyapisi olarak kullanilir; yoksa sistem in-memory fallback ile calismaya devam eder.
- Rezervasyon akisi race-condition korumali olacak sekilde fiyat kilitleme (`locked_price`) mantigina dayanir.
- Tenant cekirdegi `Studio` modelidir; adminler yalnizca kendi `studioId` kapsamindaki veri ve rezervasyonlari yonetebilir.
- `v1.5` ile isletme seviyesi siniflandirma `Sector` ve `StudioSector`, firsat seviyesi siniflandirma ise `ServiceCategory` ve `Auction.serviceCategoryId` uzerinden kurulur.
- Taxonomy master datasi serbest panel girdisiyle degil, owner kontrollu script akislariyla yonetilir.
- Gelistirme modeli tek gelistirici + manuel dogrulama + canli kullanimdan gelen geri bildirimlerle surekli kucuk revizyonlar seklindedir.

## Klasor Yapisi
- `app/`: Backend uygulama kodu
- `app/api/`: FastAPI endpoint katmani ve route tanimlari
- `app/services/`: Is kurallari, rezervasyon, auction ve diger servis mantiklari
- `app/models/`: Pydantic modelleri ve domain semalari
- `app/core/`: Konfigurasyon, guvenlik, DB, scheduler, email, Redis ve socket altyapisi
- `frontend/`: Vue 3 tabanli istemci uygulamasi
- `frontend/src/`: View, store, composable ve UI kaynaklari
- `prisma/`: Prisma schema ve migration dosyalari
- `scripts/`: Operasyonel, seed ve owner yonetimli CLI scriptleri
- `tests/`: Backend entegrasyon, birim ve davranis testleri
- `uploads/`: Yuklenen dosyalarin depolama alani
- `docker/`: Container baslatma yardimci scriptleri
- `.memory-bank/`: Proje bellek bankasi; yalnizca guncel 4 cekirdek dosya esas alinir

## Urun ve Mimari Odaqlar
- Ana deger onerisi bos kapasiteyi fiyat dususu ve FOMO etkisiyle gelire cevirmektir.
- `v1.5` gercekligi, cok sektorlu tenant yapisi ve hizmet kategorisi siniflandirmasi etrafinda tanimlidir.
- Mevcut muhendislik onceligi yeni buyuk ozelliklerden cok canlida calisan `v1.5` urununu kucuk, hedefli ve guvenli revizyonlarla gelistirmektir.