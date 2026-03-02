# Proje Özeti (Project Brief)

## Genel Bakış
**HotHour**, pilates stüdyoları için dinamik Hollanda açık artırması modeliyle boş seansları gelir fırsatına çeviren bir platformdur. Kullanıcılara rekabetçi bir "fiyat düşüşü" deneyimi sunarak FOMO (Fear Of Missing Out) tetikler ve hızlı rezervasyon imkanı tanır.

Sistem çekirdeği (backend fiyat algoritmaları, socket tabanlı realtime altyapı, rezervasyon ve yetkilendirme modelleri) ile referans tasarımlara (Referans Görseller/) dayalı Frontend görsel arayüzü başarıyla tamamlanmış ve entegre edilmiştir. 

Mevcut aşamadaki ana hedef; teknik borçları temizlemek, modülerliği artırmak ve **Faz R5** kapsamında **Admin Paneli Yapısal Refactoring** sürecini tamamlayarak projeyi üretime (production) hazır, tam sürdürülebilir bir yapıya kavuşturmaktır.

## Temel Hedefler
1. **Mimari Sürdürülebilirlik:** Özellikle Admin paneli gibi yoğun iş kuralı ve API isteği barındıran View sayfalarındaki monolitik kodları Composable, Component ve Utility modüllerine ayırmak.
2. **Kod Tekrarını Engellemek:** Aynı statü renkleri, formatlama fonksiyonları ve API client yapılarını (fetch kalıplarını) merkezi ve tekil dosyalardan çekmek.
3. **Fonksiyonel Bütünlük:** Refactoring yapılırken uygulamanın kusursuz çalışan mevcut yeteneklerini (Realtime yayınlar, rezervasyon yarış kuralı, yetkilendirme katmanları, bildirim kontrolü vb.) kesinlikle bozmamak.
4. **Kalite Güvencesi:** Tüm ekranlarda mobil öncelikli (R2) başarımların ve test kapsamının korunmasını garanti altına almak.

## Güncel Kapsam (Faz R5 ve Stabilizasyon)

### Tamamlananlar (R1, R2, R3, R4)
- Tam kapsamlı Backend ve Frontend MVP uygulaması.
- Görsel referanslarla (Cam efekti, neon glow, modern karanlık tema) uyuşan kusursuz UI ve mobil uyum.
- Kayıt, giriş, rol tabanlı güvenlik, e-posta doğrulama akışları.
- Turbo mod senkronizasyonları, eşzamanlı rezervasyon race condition engellemeleri, admin rezervasyon yasakları.
- Otomatik iptal/no-show bildirimlerini kapsayan "Admin Notifications" altyapısı ve bildirim z-index/dış tıklama düzeltmeleri.
 - Refresh-token revocation için Redis destekli blacklist eklendi; fallback olarak process-local in-memory kullanım devam ediyor. (`app/core/redis_client.py`, `app/core/token_revocation.py`)
 - Backend & frontend testleri güncellendi ve çalıştırıldı (backend pytest: 76 passed; frontend vitest: 121 passed).

### Öncelikli Hedef: Neler Yapılacak? (R5 - Admin Refactor)
- **Ortak Domain Metadata:** `utils/admin/` altında statü etiketleri ve renklerinin merkezileştirilmesi.
- **Composable Katmanı:** `composables/admin/` altında veri çekme (fetch) ve local state yönetiminin logic'ten ayrıştırılması.
- **API Client:** View'lardaki uzun `fetch` bloklarının `auth token + baseUrl` destekli tekil bir utils fonksiyonuna taşınması.
- **View Parçalama:** AdminDashboard gibi devleşen view'ların alt bileşenlere (FilterToolbar, NotificationDropdown, ActionButtons vs.) bölünmesi.

### Dahil Olmayanlar
- Bu oturumda sisteme yeni bir core "feature" EKLENMEYECEKTİR.
- Sadece yapısal temizlik, teknik refactor ve clean-architecture adaptasyonu amaçlanmaktadır.

## Başarı Kriterleri
- Refactor sonrası tüm Admin sayfalarının görsel ve işlevsel olarak %100 aynı kalması ancak View dosya kod satır sayılarının dramatik şekilde düşmesi.
- Yeni eklenen `composables` / `utils` yapısının hatasız import edilebilmesi.
- Backend entegrasyon testlerinin ve frontend build aşamalarının başarıyla geçmesi.
