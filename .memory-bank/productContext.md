# Ürün Bağlamı (Product Context)

## Neden Bu Ürün?
Hizmet sektöründe (özellikle stüdyo seanslarında) boş kalan kontenjanlar zarar yazar. "HotHour" modeli ile seans saati yaklaştıkça fiyat düşerek potansiyel müşteriler satın almaya teşvik edilir. Ayrıca `Turbo` mantığı ile belirli bir süre kalan seanslarda ani fiyat düşüşleri yapılarak satış garantilenmeye çalışılır.

## UX (Kullanıcı Deneyimi) Hedefleri
1. **Oyunlaştırma (Gamification):** Sayaçlar, periyodik düşen fiyatlar ve ani (Turbo) fırsat bildirimleri ile kullanıcıyı platformda tutmak.
2. **Hızlı Reaksiyon:** Fiyat güncellemeleri anlık (real-time) geldiği için sayfayı yenilemeye gerek kalmadan "Hemen Al" dürtüsünü harekete geçirmek.
3. **Kolay Stüdyo Yönetimi:** Admin panelinde yöneticiyi sadece kendi kurumuna ait (Studio ID) veriler, grafikler ve rezervasyonlara yönlendirerek karmaşayı engellemek (Tenant-isolation).

## Bakım İpuçları (AI İçin)
- Müşterinin "gerçek zamanlılık" beklentisi yüksektir. WebSocket (Socket.io) çökmeleri anında satışları durdurur. Kritik sorunlarda ilk kontrol edilmesi gereken yer `socket_service.py` ve `frontend SocketStore/Composables` bağlantılarıdır.
- Adminlerin kendi verilerini görmesi önemlidir. Query'lerde `studioId` sızıntısı olmamasına dikkat edilmelidir.
