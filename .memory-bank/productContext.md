# Ürün Bağlamı (Product Context)

## Çözdüğümüz Problem
Pilates stüdyoları ve benzeri işletmeler sabit maliyetlere sahiptir. Bir eğitmen o saatte oradadır, ışıklar açıktır. Ancak saat 10:00 - 17:00 arası veya son dakika iptalleri nedeniyle oluşan boşluklar "satılamayan envanter" olarak çöpe gider. Sabit fiyat indirimi yapmak marka değerini düşürebilir ve müşteriyi "hep indirim beklemeye" alıştırabilir.

## Çözümümüz: HotHour
Sıradan bir indirim yerine, **Dinamik Hollanda Açık Artırması** sunuyoruz.
*   **Oyunlaştırma:** Fiyatın göz önünde düşmesi heyecan yaratır.
*   **Adil Pazar Değeri:** Seans, o an birinin ödemeyi kabul ettiği en yüksek fiyattan satılır.
*   **Aciliyet:** "Turbo Mod" ile son dakikada fiyat düşüşü hızlanır, karar verme süresi daralır.

## Kullanıcı Deneyimi (UX) Hedefleri

### Son Kullanıcılar (Müşteriler) için:
1.  **Heyecan:** Fiyatın düşüşünü izlemek bir oyun gibi hissettirmeli.
2.  **Hız:** "Hemen Kap" butonu ile saniyeler içinde rezervasyon yapabilmeli.
3.  **Güven:** Ödeme stüdyoda yapılacağı için kart bilgisini girmekle uğraşmamalı. Rezervasyon kodu yeterli olmalı.

### Stüdyo Yöneticileri (Admin) için:
1.  **Otomasyon:** "Set and Forget". Bir kez kurallar (başlangıç fiyatı, taban fiyat, düşüş hızı) girildiğinde sistem kendi kendine çalışmalı.
2.  **Maksimum Verim:** Boş kalacak seansın 500 TL'ye bile satılması, 0 TL'den iyidir.

## İş Modeli Kavramları
*   **Dutch Auction (Hollanda Usulü):** Yüksekten başlayıp aşağı inen fiyat.
*   **Locked Price (Kilitli Fiyat):** Kullanıcının rezervasyon butonuna bastığı andaki fiyat. İşlem sırasında fiyat düşmeye devam etse bile, kullanıcı o anki fiyattan sorumlu olur.
*   **Booking Code:** Ödeme doğrulaması için üretilen, karmaşık olmayan ama benzersiz kod (örn: `HOT-8X2A`).
