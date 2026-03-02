# Ürün Bağlamı (Product Context)

## Problem ve Çözüm
Pilates stüdyoları boş seanslardan gelir kaybeder. HotHour bu seansları dinamik (zamanla düşen) Hollanda açık artırma modeliyle satışa çıkarır; kullanıcı canlı fiyat düşüşünü izler ve uygun fiyatta tek tıkla rezervasyon yapar.

## Mevcut Ürün Durumu
Tüm kullanıcı ve admin akışları tamamlandı, üretim kalitesinde çalışıyor:

| Alan | Durum |
|---|---|
| Rezervasyon + fiyat düşüşü (FOMO) | ✅ Stabil |
| Canlı socket senkronizasyonu | ✅ Stabil |
| Admin panel (planlama, filtreleme, aksiyon) | ✅ Stabil |
| E-posta doğrulama | ✅ Stabil |
| JWT auth + refresh token akışı | ✅ Stabil |
| Mobil uyum (responsive) | ✅ Stabil |

## UX Prensipleri (Korunacak)
- **Son Kullanıcı:** "Live Arena" hissi, glowlu kartlar, pulse ikonlar, anlık fiyat güncellemeleri — hiçbir flow değiştirilmeyecek.
- **Admin:** Tek kaynaktan statü/formatlama; tüm composable/utility bağlantıları stabil.

## Sonraki Ürün Adımları
1. **Canlıya Çıkış (Deployment):** Staging → production pipeline.
2. **CI Entegrasyonu:** Vitest + pytest CI pipeline.
3. **Redis Aktivasyonu:** Kullanıcı/worker sayısı arttığında `.env` içinde `REDIS_URL` ayarlanarak tek adımda aktif edilir.
4. **Ödeme Entegrasyonu:** `PAYMENTS_ENABLED=false` → gelecek faz.
