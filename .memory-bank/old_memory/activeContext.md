# Aktif Bağlam (Active Context)

## Mevcut Durum
`v1.5` aktif odak olmaya devam ediyor. Proje şu anda büyük çaplı değişiklikler sonrası lokal manuel test ve stabilizasyon evresinde.

## Sonuçlanmış Ana Başlıklar
- çok sektörlü taxonomy modeli kuruldu
- public filtreleme sektör ve hizmet kategorisi bazında çalışıyor
- admin tarafında hizmet kategorisi seçimi eklendi
- işletme sektör yönetimi panelden kapatıldı
- dashboard'da işletme sektörü ile fırsat kategorisi ayrıştırıldı
- seed akışı deterministik ve taxonomy uyumlu hale getirildi

## Şu Anki Ana Hedef
Yeni büyük açılımlar yerine, mevcut `v1.5` çerçevesini daha stabil hale getirmek ve manuel testlerden gelen revizeleri işlemek.

## Sabit Kurallar
- `Studio` korunur, tenant çekirdeğidir
- taxonomy owner yönetimindedir
- normal admin sektör değiştiremez
- fırsat sınıflandırması `ServiceCategory` üzerinden yürür
- ürün dilinde `işletme` ve `fırsat` kullanılır

## Dikkat Edilecek Riskler
- tenant izolasyonu
- relation response kırılmaları
- işletme sektörü ve fırsat kategorisinin karışması
- seed verisinin gerçek senaryodan kopması
- yeni revizelerin eski akışlarda regresyon üretmesi

## İkincil Gündemler
- SEO backlog'ta kalır
- canlıya alma bu fazın önceliği değildir
