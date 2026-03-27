# Coding Standards

## Isimlendirme Kurallari
- Python degisken, fonksiyon ve modullerinde `snake_case` kullan.
- Python siniflari, Pydantic modelleri ve enum tiplerinde `PascalCase` kullan.
- Frontend composable ve component isimlerinde mevcut Vue ekosistemi geleneklerini koru; component dosyalari icin `PascalCase`, genel yardimci dosyalar icin proje mevcut stilini takip et.
- API, model ve servis katmanlarinda teknik legacy isimler (`Studio`, `Auction`, `studioId`) korunabilir.
- Kullaniciya gorunen metinlerde `isletme`, `firsat` ve `hizmet` terminolojisini kullan.

## Mimari Kurallar
- Backend tarafinda async-first yaklasim korunur.
- Endpoint katmani (`app/api`) yalnizca request validation, auth ve response sekillendirme sorumlulugunu tasir; is mantigi servis katmaninda tutulur.
- Raw SQL son caredir; veri erisimi icin oncelik Prisma uzerinden ilerlemektir.
- Tenant izolasyonu temel guvenlik kuralidir; `studioId` kapsami her ilgili endpoint ve serviste korunmalidir.
- Isletme seviyesi veri ile firsat seviyesi veri birbirine karistirilmaz.
- Taxonomy verileri serbest metin veya panel uzerinden uretilmez; owner kontrollu script akisi esas alinir.
- Relation include kullanimi endpoint ihtiyacina gore minimum gerekli alanlarla sinirli tutulur.
- Frontend tarafinda yetkili istekler `fetchWithAuth` uzerinden yurur.
- Frontend state'e veri yazmadan once response dogrulanir; API cevabi oldugu gibi state'e akitilmaz.
- Filtre state'i mumkun oldugunca query param ile senkron kalir.

## Hata Yonetimi
- Backend hatalari uygun sekilde loglanir ve kullaniciya anlamli `HTTPException` ya da kontrollu response ile donulur.
- Hata durumlarinda sessiz basarisizlik uretme; hata nedeni olabildigince belirgin kalmali.
- Frontend tarafinda ag istegi basarisizliklari `response.ok` ve beklenen payload yapisi kontrol edilerek ele alinmali.
- Yeni degisiklikler mevcut akislarda regresyon uretme riski tasiyorsa hedefli test veya manuel dogrulama notu birakilmali.
- Bu projede manuel test ana dogrulama yontemidir; otomatik test eklendiginde belirli riskli davranisi korumaya odakli ve bakimi kolay kalmalidir.

## Tip Guvenligi
- Python tarafinda type hint kullanimi varsayilan standarttir.
- Pydantic response ve request modelleri relation include davranislariyla uyumlu kalmalidir.
- Frontend tarafinda mevcut tip yapisi neyse onunla tutarli ilerle; yeni veri sekilleri acik ve izlenebilir olmali.

## Frontend Kurallari
- Vue tarafinda `script setup` ve composable deseni korunur.
- Listeleme ve filtreleme akislarinda backend ile frontend mantigi ayrismamalidir.
- Bos durumlar, kenar senaryolari ve filtre reset akislari ozellikle stabilizasyon fazinda dikkatle ele alinmalidir.

## Script ve Operasyon Kurallari
- CLI scriptleri acik kullanim mesaji ve tahmin edilebilir parametre davranisi sunmali.
- Seed scriptleri deterministik olmali; rastgele taxonomy eslemesi yapilmamali.
- Her firsatin `serviceCategoryId` degeri, bagli oldugu isletmenin sektorlerinden biriyle uyumlu olmali.
- Master veri degisiklikleri panel yerine `scripts/` altindaki owner kontrollu araclarla yonetilmelidir.

## Calisma Ilkesi
- Bu projede gelistirme akisi tek gelistirici tarafindan yurutulur; kod degisiklikleri canlida calisan urunu bozmayacak kucuk, hedefli ve geri bildirime dayali revizyonlar olarak ele alinir.
- Oncelik hizli feature buyutmekten cok `v1.5` sonrasi canli urunu stabil, izlenebilir ve tenant-guvenli sekilde surdurmektir.