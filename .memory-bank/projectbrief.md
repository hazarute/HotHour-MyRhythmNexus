# Proje Özeti (Project Brief)

## Genel Bakış
**HotHour**, pilates stüdyoları için dinamik Hollanda açık artırması modeliyle boş seansları gelir fırsatına çeviren bir platformdur. Sistem çekirdeği (backend, fiyat motoru, rezervasyon, gerçek zamanlı event altyapısı) çalışır durumdadır.

Bu yeniden planlama ile ana hedef, mevcut çalışan fonksiyonları bozmadan tüm frontend görsel arayüzünü `Referans Görseller/` klasöründeki tasarım diliyle yeniden hizalamaktır.

## Temel Hedefler
1. **UI Tutarlılığı:** Home, rezervasyonlar, admin ekranları ve giriş ekranı arasında tek bir görsel dil oluşturmak.
2. **Referans Sadakati:** Referans görsellerdeki tipografi, kart yapısı, glow/kontrast dengesi ve CTA hiyerarşisini korumak.
3. **Fonksiyonel Güvenlik:** Yeniden tasarım sürecinde backend API sözleşmeleri ve mevcut iş akışları (login, book, realtime) değiştirilmeyecek.
4. **Hızlı Yayınlanabilirlik:** Yeniden tasarım MVP’si minimum teknik riskle devreye alınacak.

## Güncel Kapsam

### Mevcut Durum (Özet)
Backend ve Frontend geliştirme fazları (R1, R2, R3) tamamlanmıştır. Proje şu anda **Canlıya Geçiş Öncesi Doğrulama (R4)** aşamasındadır.

### Dahil Olanlar
- Kullanıcı ve admin için mevcut akışların görsel yeniden tasarımı (Tamamlandı)
- Public ekranlar: Home, Auction Detail, My Reservations (Tamamlandı)
- Admin ekranlar: Login, Dashboard, Auction Create, Reservations (Tamamlandı)
- Global layout/navigation ve ortak bileşen stili (Tamamlandı)
- Mevcut API/store/socket entegrasyonunun korunması (Tamamlandı)
- **Manuel Testler ve Bug Fix:** Canlıya alma öncesi son kontroller.

### Dahil Olmayanlar
- Yeni ürün özelliği ekleme (ödeme gateway, yeni business rule vb.)
- Backend domain model değişiklikleri (Zorunlu olmadıkça)
- Mevcut kapsam dışı analitik/raporlama modülleri

## Başarı Kriterleri
- Tüm hedef ekranlar referans diliyle görsel olarak tutarlı olur
- Mevcut kritik kullanıcı yolculukları bozulmadan çalışır:
  - Login
  - Auction görüntüleme
  - Hemen Kap / rezervasyon oluşturma
  - My Reservations görüntüleme
  - Admin’de rezervasyon doğrulama
- Frontend build ve mevcut temel testler çalışır durumda kalır

## Son Kapsam Güncellemesi (R4.7)
- Rezervasyon akışında rol bazlı güvenlik kuralı netleştirildi: **Admin kullanıcılar oturum rezerve edemez**.
- Realtime tutarlılık artırıldı: bir kullanıcı rezervasyon yaptığında diğer kullanıcılarda oturum durumu anında kapanır.
- Turbo mod görünürlüğü backend state + frontend socket senkronuyla dinamik hale getirildi.
- Üretim kararlılığı için auction listeleme akışında bağlantı kopmasına karşı otomatik toparlanma eklendi.