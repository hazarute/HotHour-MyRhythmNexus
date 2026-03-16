# Proje Özeti (Project Brief)

**Proje Adı:** HotHour (MyRhythmNexus)
**Güncel Faz:** `v1.5 aktif` 
**Çalışma Modu:** köklü değişiklikler sonrası lokal manuel test + stabilizasyon + revize döngüsü. Canlıya almak için erken.

## Temel Konsept
HotHour, boş kalan hizmet kapasitesini Dutch Auction modeliyle değerlendiren çok kiracılı rezervasyon platformudur.

İlk ürün odağı spor/dans/pilates idi. `v1.5` ile ürün çok sektörlü hizmet pazarına genişliyor.

## v1.5 Ana Hedef
`Studio` tenant modeli korunarak iki seviyeli sınıflandırma getirildi:
- işletme seviyesi sektörler: `Sector` + `StudioSector`
- fırsat seviyesi hizmet kimliği: `ServiceCategory` + `Auction.serviceCategoryId`

## Temel Kurallar
- `Studio` tablo ve teknik isim olarak korunur.
- Ürün dilinde `studio` -> `işletme`, `auction` -> `fırsat`.
- Master veri yönetimi panelden değil, SSH/CLI scriptleriyle yapılır.
- Normal admin sektör veya hizmet kategorisi oluşturamaz.
- Admin yalnızca kendi tenant verisini yönetir.

## Şu Anki Öncelik
- `v1.5` mimarisini stabil hale getirmek
- manuel lokal testlerden gelen geri bildirimlerle revize etmek
- mevcut akışlarda regresyon bırakmamak

## İkincil Gündemler
- SEO backlog'ta tutulur
- canlıya alma kararı stabilizasyon tamamlanmadan verilmez
