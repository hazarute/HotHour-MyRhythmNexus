# Aktif Bağlam (Active Context)

## Mevcut Durum / Şu Anki Zihinsel Odak
Proje vizyonu, tasarımı, backend mantığı ve tüm çekirdek bileşenleri hatasız olarak **çalışmaktadır**. Mobil öncelikli (R2) revizyonlarına, test (R3/R4) koşullarına kadar uygulama prod'a çıkacak yeterliliktedir.
**Faz R5 — Admin Paneli Yapısal Refactoring BAŞARIYLA TAMAMLANDI.**

2026-03-01 güncellemesi: Admin Dashboard üzerindeki **aktif + turbo** oturumların "İptal Et" aksiyonunda alınan `400 turbo mode requires at least 180 minutes auction duration` hatası giderildi. Kök neden, `update_auction` içinde sadece `status` güncellemesinde bile tam zaman/fiyat/turbo validasyonunun tetiklenmesiydi.

Tüm Yönetim Paneli (AdminDashboardView, AdminReservationsView, AdminAuctionDetailView, AdminReservationDetailView) sayfalarındaki karmaşık state'ler ve fetch operasyonları ayrıştırıldı, UI metadata'ları merkezileştirildi. Sistem modüler ve temiz bir mimariye (Composable ve Utils yapısına) taşındı. 
`npm run build` ile ön yüzün prod derlemesi başarıyla oluşturuldu; bileşenler derlendi ve önemli varlıklar (`dist/`) yazıldı. UI düzeninde kritik bir bozulma gözlenmedi.

## Sıradaki Görev Planı (AI Seansı İçin)
Refactoring kapsamının R5 adımları tüm View dosyaları özelinde başarıyla uygulandığı için projede "Bütünüyle Üretime Hazır (Production Ready)" duruma gelinmiştir.

Sıradaki adım:
Kullanıcının projeyi baştan sona E2E ile doğrulaması veya deployment/CI adımlarını tetiklemesidir. Ayrıca test altyapısının CI'ya entegrasyonu önerilir.

## Dikkat Edilmesi Gerekenler
* Yapısal temizlik (Clean Architecture) projede başarıyla uygulanmıştır, yeni eklenecek admin view'ları için composables/admin veya utils/admin yönergeleri standart kabul edilmelidir.
* Local build başarılıdır. Unit testler (Vitest) oluşturuldu ve yerel çalıştırmada geçti. Realtime entegrasyonlar composable seviyesinde socket abonelikleri ile sağlandı; görünümler (AdminDashboard, AdminReservations, NotificationDropdown) bu veri akışlarını kullanacak şekilde güncellendi.
