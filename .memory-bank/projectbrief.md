# Proje Özeti (Project Brief)

## Genel Bakış
**HotHour**, Pilates stüdyoları ve randevu bazlı işletmeler için geliştirilmiş bir **Dinamik Hollanda Açık Artırması (Dutch Auction)** ve **Gelir Yönetimi (Yield Management)** platformudur.

Temel hedef, "dolu olması gereken ama boş kalan" (dead inventory) seansları, oyunlaştırılmış bir fiyatlandırma modeliyle kullanıcıya sunarak gelire dönüştürmektir. Kullanıcılar, zamanla fiyatı düşen bir seansı "başkası kapmadan" en uygun fiyata yakalamaya çalışır.

## Temel Hedefler
1.  **Atıl Kapasiteyi Nakde Çevirmek:** Boş kalan seansların maliyetini çıkarmak ve ek gelir sağlamak.
2.  **FOMO Yaratmak:** Fiyatın düşmesi ve "tek" olması, kullanıcıda kaçırma korkusu yaratarak satış hızını artırır.
3.  **Ödeme Bariyerini Kaldırmak:** Kredi kartsız, "Rezervasyon Yap & Yerinde Ödeme" modeli ile güven sorununu aşmak.
4.  **Operasyonel Yükü Azaltmak:** Otomatik fiyatlandırma ve rezervasyon yönetimi.

## Kapsam
Proje şu an için **HotHour Core** (Backend API, Veritabanı, İş Mantığı) üzerine odaklanmaktadır.

### Dahil Olanlar
*   Kullanıcı ve Rol Yönetimi (Stüdyo Yöneticisi, Son Kullanıcı)
*   Açık Artırma Motoru (Fiyat düşürme mantığı, Turbo mod)
*   Rezervasyon Sistemi (Yarış durumu koruması, Fiyat kilitleme)
*   Bildirim Altyapısı
*   Admin Paneli API uçları

### Dahil Olmayanlar (Şimdilik)
*   Gelişmiş analitik panoları (MVP sonrası)
*   Online Ödeme Gateway entegrasyonu (MVP'de yerinde ödeme var)
