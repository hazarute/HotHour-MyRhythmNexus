# Proje Özeti (Project Brief)

**Proje Adı:** HotHour (MyRhythmNexus)
**Mevcut Durum:** ✅ Tamamlandı / Stabil Sürüm - Bakım Modunda (Maintenance Mode)

## Temel Konsept
Platform, dans ve spor stüdyoları gibi işletmelerin boş kontenjanlarını "Düşen Fiyatlı Açık Artırma" (Dutch Auction) mantığıyla satmasını sağlayan dinamik bir biletleme ve rezervasyon sistemidir. Fiyatlar zamanla düşer (HotHour/Turbo indirimleri) ve kullanıcılar FOMO (Fırsatı Kaçırma Korkusu) ile hızlıca satın alma yapar.

## Başlıca Modüller
- **Kullanıcı Modülü:** Kayıt, giriş, cüzdan (bakiye) yönetimi, gerçek zamanlı fiyat takibi, rezervasyon yapma.
- **Admin/Stüdyo Modülü:** Çoklu kiracı (Multi-tenant) mantığıyla çalışır. Her admin kendi stüdyosuna atanır; sadece kendi stüdyosunun açık artırmalarını, logolarını, istatistiklerini ve rezervasyonlarını yönetir.
- **Dinamik Fiyatlandırma Motoru:** APScheduler arka plan görevleriyle düzenli periyotlarda (veya Turbo tetikleyicilerle) fiyat güncellemeleri.
- **Gerçek Zamanlı Çekirdek (WebSocket):** Fiyat düşüşleri ve rezervasyon durumlarını (Satıldı/Dolu vb.) anlık olarak (Socket.io) tüm kullanıcılara iletir.

## Proje Hedefi (AI İçin Not)
Projenin özellik geliştirme (feature development) aşaması tamamlanmıştır. Bundan sonra yapılacak işlemler **yalnızca hata ayıklama (bug-fixing), sistem monitörleme ve bakım** odaklı olacaktır.
