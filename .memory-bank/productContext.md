# Ürün Bağlamı (Product Context)

## Çözdüğümüz Problem
HotHour, boş kalan stüdyo seanslarını oyunlaştırılmış ve dinamik (zamanla düşen) fiyatlama ile satarak bir kazan-kazan modeli yaratır. Stüdyo gelir elde eder, kullanıcı kaliteli hizmeti ucuza yakalar. Sistemin mevcut durumunda bu iş akışı sorunsuz olarak işletilmekte olup kullanıcı tarafında referanslarla (HomView, MyReservationsView vb.) istenilen algı ve heyecan oluşturulmuştur.

## Mevcut Ürün Durumu (Başarılanlar)
- **FOMO + Hız:** Fiyatın düşüşünü canlı izleme ve tek tıkla rezervasyon deneyimi stabil çalışmaktadır.
- **Güven ve Okunabilirlik:** Kullanıcıya rezervasyon kodu, statü değişimleri ve hata mesajları net görsel feedbacklerle (Pulse ikonlar, glowlu kartlar vb.) sağlanmaktadır.
- **Operasyonel Temel:** Admin'in açık artırma planlama, filtreleme ve durumu düşen / iptal olan / tamamlanan seansları görmesi sağlanmıştır. Ancak admin tarafında işler büyüdükçe (UI karmaşıklaştıkça) yönetimsel arka plan kodu dağınıklaşmıştır.

## UX ve Operasyonel Hedefler (R5 Güncellemesi)

### Son Kullanıcı (Stabil)
Kullanıcı deneyimi hedef noktasına ulaşmıştır. Mevcut "Live Arena" hissi, detaylardaki karar verme hiyerarşisi ve sorunsuz responsive davranış olduğu gibi korunacaktır. Hiçbir flow değişikliği yapılmayacaktır.

### Admin (Revizyon ve Refactor Odaklı)
1. **Kodsal Sürdürülebilirlik:** Admin panelinin ön yüzündeki `AdminDashboardView.vue` başta olmak üzere, UI karmaşası yüzünden teknik müdahalelerin zorlaştığı noktalar sadeleştirilecektir.
2. **Standardizasyon:** `AdminReservationsView`, `AdminAuctionDetailView` ve diğer alanlardaki statü metinleri, tarih/saat gösterimleri, iptal onayı modalı gibi öğeler %100 özdeş hale getirilecek ve tek bir kaynaktan render edilecektir.
3. **Sorunsuz Bakım (Maintainability):** Admin'e ileride raporlama veya finans modülleri eklendiğinde aynı API call patternlerini doğrudan `composables` üzerinden çağırabileceği bir ortam yaratılacaktır.
