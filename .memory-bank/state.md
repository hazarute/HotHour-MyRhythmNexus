# State

## Mevcut Odak
Railway uzerinde aktif kullanilan `v1.5` urununde manuel test, canli kullanim geri bildirimi ve kotuye kullanim gozlemleriyle tetiklenen kucuk ama etkili revizyonlari guvenle hayata gecirmek.

## Aktif Faz
`v1.5` Canli Revizyon ve Davranissal Guclendirme

## Gorev Listesi

### Faz 1 - Temel Platform Altyapisi
- [x] Cekirdek auth, rezervasyon, fiyat motoru ve realtime altyapisini kur
- [x] Tenant odakli `Studio` cekirdek modelini ve admin izolasyonunu yerlestir

### Faz 2 - Cok Sektorlu Veri Modeli
- [x] `Sector`, `StudioSector` ve `ServiceCategory` veri modelini tasarla ve uygula
- [x] `Auction.serviceCategoryId` baglantisini sisteme dahil et
- [x] Migration akisini calistir ve veri modelini Prisma semasi ile hizala

### Faz 3 - `v1.5` Uygulama Genislemesi
- [x] Taxonomy servislerini ve read endpoint'lerini ekle
- [x] Public filtreleme akisina sektor ve hizmet kategorisi destegi ekle
- [x] Admin firsat formunda hizmet kategorisi secimini destekle
- [x] Admin panelinde isletme sektoru ile firsat kategorisi gosterimini ayristir
- [x] Isletme sektor duzenleme akislarini panelden kapat
- [x] Owner yonetimli taxonomy scriptlerini ekle
- [x] Seed akisini deterministik ve taxonomy uyumlu hale getir
- [x] Rezervasyon tarafinda tenant izolasyonunu daha siki uygula

### Aktif Revizyon: Sektor bazli 10 gun cooldown
- [x] `BookingLifecycleManager.validate_booking_eligibility` icindeki mevcut `studioId + serviceCategoryId` iptal kaynakli 10 gun engelini aynen koru.
- [x] Hedef auction icin `serviceCategoryId` uzerinden `sectorId` tespit et; gerekiyorsa kategori iliskisini DB'den tamamla.
- [x] Kullaniciya ait son 10 gunluk rezervasyon gecmisinde ayni sektore ait firsat rezervasyonlarini sorgulayacak sektorel cooldown kontrolunu tasarla.
- [x] Yeni kurali is akisinda ayri ve okunur tutmak icin `RecentSectorBookingRestrictionError` ekle ya da mevcut hata hiyerarsisini bilincli sekilde genislet.
- [x] `app/api/reservations.py` icinde yeni sektor kisitini anlamli 400 mesaji ile expose et.
- [x] `tests/test_cancel_restriction.py` icine `test_user_book_then_rebook_same_sector_is_blocked` senaryosunu ekle.
- [x] Ayni test paketinde su davranislari da koru: mevcut iptal bazli kategori engeli bozulmuyor, farkli sektor izinli kaliyor, farkli studyo davranisi yalnizca yeni kurala gore degisiyor.
- [ ] Uygulama sonrasi hedefli manuel kontrol yap: rezervasyon alma, 2. rezervasyon denemesi, farkli sektor izin akisi, mevcut iptal kisitinin korunmasi.

### Canli Urun Bakimi
- [ ] Canlidan ve manuel testlerden gelen yeni kucuk iyilestirme fikirlerini davranis/risk bazli olarak sirala.
- [ ] Kotuye kullanim veya kenar durum goruldugunde once mevcut akisa etkisini analiz et, sonra dar kapsamli revizyon planla.
- [ ] Her revizyonda tenant izolasyonu, rezervasyon yarisi ve kategori-sektor tutarliligini yeniden kontrol et.

### Backlog / Sonraki Dalga
- [ ] SEO backlog maddelerini stabilizasyon sonrasinda yeniden planla
- [ ] Redis'in cok worker senaryolarindaki rolunu daha ileri rollout planina bagla
- [ ] Odeme entegrasyonu acilacagi zaman `PAYMENTS_ENABLED` odakli teknik plan cikar

## Durum Notlari
- Proje `v1.0`dan beri Railway uzerinde canli ve aktif kullanimdadir.
- `v1.5` gecisi kesintisiz tamamlanmis, kullanim aksamadan devam etmistir.
- Gelistirme modeli tek gelistirici + manuel test + canli geri bildirim + hedefli revizyon seklindedir.
- Yeni buyuk ozellik eklemekten cok mevcut canli akislarda davranissal aciklari kapatmak ve regresyonu onlemek hedeflenir.
- Seed ve taxonomy akislarinin gercek senaryodan kopmamasi kritik kabul edilir.
- `tests/test_cancel_restriction.py` hedefli pytest kosusu gecti; manuel UI akis dogrulamasi halen bekliyor.
- Frontend tarafinda abuse senaryolari icin component testi, store testi ve Playwright tabanli tarayici testi kapsami olusturuldu.