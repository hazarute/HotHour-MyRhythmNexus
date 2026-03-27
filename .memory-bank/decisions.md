# Decisions

## Is Kurallari
- `Studio`, tenant cekirdegi olarak korunur; teknik isimlendirme legacy olsa da veri modeli etrafinda ana sinirdir.
- Urun dilinde `studio` yerine `isletme`, `auction` yerine `firsat`, `service category` baglaminda `hizmet` dili tercih edilir.
- Normal admin yalnizca kendi tenant verisini yonetebilir; tenant izolasyonu guvenlik siniri olarak ele alinir.
- Taxonomy kayitlari serbest metin olarak uretilmez; owner tarafindan kontrollu scriptlerle yonetilir.
- Normal admin sektor veya hizmet kategorisi yaratamaz.
- Isletme seviyesi siniflandirma ile firsat seviyesi siniflandirma birbirine karistirilmaz.
- Rezervasyon aninda fiyat kilitlenir; ilk alan kazanir mantigi korunur.
- Online odeme zorunlu degildir; rezervasyon yap, isletmede ode modeli gecerli kabul edilir.
- Platform `v1.0`dan beri Railway uzerinde canli olarak calisir; `v1.5`e gecis kesintisiz devam eden bir uretim evrimi olarak ele alinmistir.
- Gelistirme ve dogrulama akisi tek gelistirici tarafindan yurutulur; birincil kalite kaynagi manuel test, canli kullanim gozlemi ve gelen geri bildirimlerle yapilan hedefli revizyonlardir.
- Kullanici bir firsati rezerve ettigi andan itibaren, ayni sektore bagli diger firsatlar icin 10 gun boyunca yeniden rezervasyon yapamaz.
- Kullanicinin USER kaynakli iptalinden dogan mevcut `ayni studio + ayni hizmet kategorisi` 10 gun engeli korunur; sektor bazli rezervasyon engeli bu kurala ek olarak calisir.

## Mimari Kararlar (ADR)
- Prisma, veri erisimi icin varsayilan katmandir; raw SQL yalnizca zorunlu durumlarda dusunulur.
- Redis opsiyonel tutulur; varsa merkezi revoke/caching saglar, yoksa sistem in-memory fallback ile calisir.
- `v1.5` genislemesi, teknik legacy isimleri koruyup urun dilini ayristirma karariyla ilerler. Bu sayede mevcut kod tabani gereksiz buyuk refactor yemeden urun dili gelistirilebilir.
- Isletme siniflandirmasi `Sector` + `StudioSector`, firsat siniflandirmasi `ServiceCategory` + `Auction.serviceCategoryId` yapisina ayrilmistir. Bu ayrim tenant gercekligi ile kullaniciya sunulan hizmet kimligini netlestirmek icin secilmistir.
- Taxonomy master data yonetimi panel disina alinmistir. Gerekce: veri kalitesini, slug kararliligini ve sektor-hizmet hiyerarsisini merkezi kontrol altinda tutmak.
- Frontend filtre davranisi kalici kaynak olarak backend filtre semantigine baglanir; query param senkronizasyonu bu nedenle korunur.

## Gecici Cozumler ve Operasyonel Notlar
- Redis olmayan ortamlarda token revoke davranisi in-memory fallback ile surdurulur; bu, gelistirme ve dusuk operasyonel kurulumlar icin kabul edilen gecici esnekliktir.
- Proje canlida aktif olarak kullanildigi icin degisiklikler buyuk dalgalar halinde degil, dikkatli secilmis kucuk revizyonlar halinde yayina alinmalidir.
- Relation include kapsamlarinda fazla nested veri donmek response kirilmalarina yol acabileceginden, endpoint bazli minimum include stratejisi uygulanir.
- Seed akisinda heuristic veya rastgele taxonomy backfill yaklasimlarindan uzak durulur; deterministik seed tercih edilir.

## Guncel Uygulama Notu
- Yeni is gelistirmeleri, canli kullanim sirasinda fark edilen zayif noktalar, kotuye kullanim senaryolari ve urun icgorusunden dogan kucuk ama surekli iyilestirmeler seklinde ele alinir.
- `v1.5` sonrasi revizyonlarin hedefi buyuk yeniden yazimlar degil, davranissal aciklari kapatmak ve canli akislarin guvenilirligini arttirmaktir.

## Mevcut Risk Kaydi
- Tenant izolasyonunun zayiflamasi kabul edilemez bir regresyondur.
- Isletme sektoru ile firsat kategorisinin karismasi hem veri tutarliligini hem de UX guvenini bozar.
- Backend ve frontend filtre mantiklarinin ayrismasi arama ve kesif deneyimini bozar.
- Koklu degisiklikler sonrasi yapilan hizli duzeltmeler, test edilmezse eski akislarda gizli regresyon uretebilir.