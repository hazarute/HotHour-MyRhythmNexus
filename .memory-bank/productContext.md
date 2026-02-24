# Ürün Bağlamı (Product Context)

## Çözdüğümüz Problem
Stüdyoların boş kalan seansları gelir kaybı yaratır; kullanıcı tarafında ise doğru zamanda doğru fiyatı yakalamak için hızlı, güven veren ve anlaşılır bir deneyim gerekir.

## Ürün Vaatleri
- **FOMO + Hız:** Fiyatın düşüşünü canlı izleme ve tek tıkla rezervasyon
- **Güven:** Yerinde ödeme modeli + net rezervasyon kodu
- **Operasyonel Netlik:** Admin’in hızlı seans/rezervasyon yönetimi

## Yeni UX Stratejisi (Yeniden Plan)
Bu fazda odak, mevcut çalışan deneyimi görsel olarak yeniden inşa etmektir:

1. **Referans-Öncelikli Tasarım:**
   - Birincil referans kaynak: `Referans Görseller/HomeView.*` ve `Referans Görseller/MyReservationsView.*`
   - Tüm ekranlar bu iki referansın görsel DNA’sına göre hizalanır.

2. **Tasarım Dili Bütünlüğü:**
   - Koyu zemin + neon vurgu
   - Cam (glass) kart estetiği
   - Güçlü CTA (özellikle “Hemen Kap”)
   - Kod/rezervasyon alanlarında yüksek okunabilirlik

3. **Referans Dışı Ekran Türetilmesi:**
   - Login, Admin Dashboard, Admin Reservations, Admin Create Auction, Auction Detail ekranları için ayrı mock yoksa referanslardan türetilmiş görsel sistem uygulanır.
   - İşlev eklenmez; yalnızca sunum katmanı yeniden şekillenir.

## UX Hedefleri

### Son Kullanıcı
- Home’da canlı arena hissi
- Auction detayında karar verme hızını artıran net hiyerarşi
- My Reservations ekranında kod ve seans bilgisine anında erişim

### Admin
- Login sonrası düşük bilişsel yük
- Dashboard/Reservations ekranlarında veri-öncelikli, hızlı taranabilir yapı
- Operasyon adımlarında görsel tutarlılık

## Başarı Ölçümü
- Ekranlar arası görsel birlik
- Kritik akışlarda regressionsız çalışma
- Kullanıcının birincil aksiyonlara (book/view/manage) daha kısa sürede ulaşması# Ürün Bağlamı (Product Context)

## Çözdüğümüz Problem
HotHour, boş kalan seansları dinamik fiyatlama ile satarken kullanıcıda oyunlaştırılmış bir “kaçırma” hissi oluşturur. Teknik akışlar çalışıyor olsa da ekranlar arasında görsel dil tam standardize değildir.

## Yeni Strateji: Referans Tabanlı UX Birliği
`Referans Görseller/` klasöründeki ekranlar ürünün görsel rehberi kabul edilir.

- `HomeView` → Public arena’nın ana görsel dili
- `MyReservationsView` → Kart yoğun veri ekranlarının görsel dili

Bu iki referanstan türetilen tasarım sistemi, tüm diğer ekranlara uygulanacaktır.

## UX Hedefleri (Revize)

### Son Kullanıcı
1. **Anında Anlaşılabilirlik:** Fiyat, kalan süre ve “Hemen Kap” CTA’sı ilk bakışta net olmalı.
2. **Tutarlı Estetik:** Home → Detail → Reservations geçişlerinde aynı marka hissi korunmalı.
3. **Güven ve Netlik:** Rezervasyon kodu ve durum etiketleri (Confirmed/Completed vb.) görsel olarak güçlü vurgulanmalı.

### Admin
1. **Operasyonel Hız:** Dashboard, rezervasyon doğrulama ve oluşturma ekranlarında bilgi hiyerarşisi sade ve hızlı okunabilir olmalı.
2. **Görsel Tutarlılık:** Admin paneli, public taraftan kopmadan daha fonksiyonel bir yoğunlukta tasarlanmalı.

## Tasarım İlkeleri
- Karanlık tema ağırlıklı, yüksek kontrastlı metin
- Neon vurgu renkleri ile canlı durum/CTA vurgusu
- Cam efekti (glass), yumuşak glow ve net kart sınırları
- Mobil öncelikli düzen, masaüstünde genişleyen grid yapısı
- Gereksiz yeni etkileşim eklemeden mevcut akışları güçlendirme