# Proje Özeti (Project Brief)

**Proje Adı:** HotHour (MyRhythmNexus)
**Güncel Faz:** `v1.5 aktif` 
**Çalışma Modu:** proje `v1.0`dan beri Railway üzerinde canlı; `v1.5` geçişi kesintisiz tamamlandı. Tek geliştirici tarafından manuel test, canlı kullanım gözlemi ve geri bildirimlerle sürekli küçük revizyonlar yapılıyor.

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
- canlida calisan `v1.5` akislarini guvenli sekilde surdurmek
- manuel test ve canli kullanim geri bildirimleriyle davranissal zayifliklari kapatmak
- mevcut akislarda regresyon birakmayan kucuk ama etkili guncellemeler yapmak

## İkincil Gündemler
- SEO backlog'ta tutulur
- yayindaki urune zarar vermeden kademeli revizyon disiplini korunur
