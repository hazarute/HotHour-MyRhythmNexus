# Proje İlerlemesi & Aşama Durumu (Progress Status)

**GÜNCEL DURUM:** `[v1.5 ACTIVE / STABILIZATION MODE]`

## v1.0 Özeti
- çekirdek auth, rezervasyon, fiyat motoru, realtime ve tenant altyapısı tamam
- admin tenant izolasyonu ve temel işletme yönetimi mevcut

---

## Release v1.5: Çok Sektörlü Platform Genişlemesi [AKTİF]

### Tamamlanan Ana Başlıklar
- [x] çok sektörlü veri modeli kuruldu
- [x] migration uygulandı
- [x] taxonomy servisleri ve read endpoint'leri eklendi
- [x] public filtreleme sektör ve hizmet kategorisi destekli hale geldi
- [x] admin fırsat formunda hizmet kategorisi seçimi eklendi
- [x] admin studio sektör düzenleme akışı panelden kapatıldı
- [x] admin liste ekranlarında işletme sektörü ve fırsat kategorisi ayrıştırıldı
- [x] owner yönetimli taxonomy scriptleri eklendi
- [x] seed akışı deterministik ve taxonomy uyumlu hale getirildi
- [x] tenant izolasyonu için rezervasyon tarafı sıkılaştırıldı

### Açık / İzlenen Başlıklar
- [ ] bazı detay response'larda nested relation kapsamını sade ve güvenli tutarak netleştir
- [ ] frontend filtre boş durum ve kenar senaryolarını manuel testlerle doğrula
- [ ] manuel testlerden gelen revizeleri işleyerek `v1.5` stabilitesini artır

### Son Doğrulamalar
- [x] hedefli backend regresyonları geçti
- [x] hedefli frontend unit testleri geçti
- [x] build alındı
- [x] seed script syntax ve senaryo tutarlılığı doğrulandı

### Şu Anki Çalışma Modu
- lokal manuel test devam ediyor
- canlıya çıkmak için erken
- öncelik yeni büyük özellik değil, stabilizasyon ve revize

---

## Backlog / İkincil Gündemler

### SEO Uyumu
- [ ] Eksik kalan SEO maddelerini `v1.5` stabilizasyonundan sonra yeniden ele al
- [ ] Uzun vadede SSR/SSG değerlendirmesini sürdür

### Bakım
- [ ] Rutin hata bildirimlerini izlemeye devam et

*Yeni gerçeklik kaynağı: `v1.5` çok sektörlü tenant + hizmet sınıflandırması + stabilizasyon sürecidir.*
