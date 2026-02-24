# Aktif Bağlam (Active Context)

## Şu Anki Odak
**YENİDEN PLANLA: Referans Görsel Tabanlı Tam UI Yeniden Tasarım (Faz R1)**

- Hedef: `Referans Görseller/` klasörünü görsel gerçeklik kaynağı kabul ederek frontend arayüzünü tutarlı bir tasarım diliyle yeniden inşa etmek.
- Kapsam: Home, Login, Auction Detail, Admin Dashboard, Admin Reservations, Admin Create Auction, My Reservations ve global layout/navigation.
- Öncelik: Mevcut backend iş mantığını değiştirmeden yalnızca UI/UX katmanını referans tasarıma hizalamak.

## Son Değişiklikler
- Referans tasarım token seti çıkarıldı ve merkezi hale getirildi:
	- `frontend/src/style.css` içinde CSS değişkenleri (renk/font/radius/shadow/glow)
	- Ortak utility sınıfları: `hh-glass-card`, `hh-text-glow`, `hh-code-text`
- Tailwind tema genişletmesi referanslarla hizalandı:
	- `frontend/tailwind.config.js` içinde `primary`, neon renkler, font aileleri, shadow ve radius değerleri güncellendi
- Frontend build doğrulaması tamamlandı: `npm run build` başarılı
- Ortak component varyant kuralları kodlandı ve gerçek kullanımda aktive edildi:
	- Yeni sınıflar: `hh-btn*`, `hh-badge*`, `hh-card*`, `hh-section`, `hh-topbar`
	- Uygulanan ekranlar: `App.vue`, `HomeView.vue`, `MyReservationsView.vue`
- Tailwind `@apply` uyumluluk sorunu, varyantların saf CSS'e çevrilmesiyle kalıcı şekilde giderildi
- Global app shell ve navigasyon referans diline taşındı:
	- `App.vue` üst bar yapısı `HomeView` referansına hizalandı (logo, nav, auth CTA hiyerarşisi)
	- Admin rotaları için üst bar gizlenerek admin layout tam genişlikte korundu
	- `style.css` içinde `hh-nav-link` ve `hh-nav-link-active` eklendi
- Frontend build doğrulaması tekrar başarılı: `npm run build`
- Direct reference ekran dönüşümü tamamlandı:
	- `HomeView.vue`: referansa uygun hero, sticky filtre şeridi, live auctions bölümü
	- `AuctionCard.vue`: glass kart estetiği, canlı durum rozeti, fiyat hiyerarşisi, "Hemen Kap" CTA
	- `MyReservationsView.vue`: referans düzenine yakın 3 kolonlu kart yapısı ve access code odağı
- Bu değişikliklerden sonra frontend build tekrar başarılı: `npm run build`
- Derived ekran dönüşümü başlatıldı:
	- `LoginView.vue` referans tasarım dilinden türetilerek yeniden tasarlandı (hero + glass login panel + neon CTA hiyerarşisi)
	- Bu değişiklik sonrası frontend build tekrar başarılı: `npm run build`
- Derived ekran dönüşümü devam etti:
	- `AuctionDetailView.vue` referans dilinden türetildi (glass fiyat paneli, turbo şeridi, CTA vurgusu, detay kartları, başarı modalı iyileştirmesi)
	- Bu değişiklik sonrası frontend build tekrar başarılı: `npm run build`
- Derived ekran dönüşümü devam etti:
	- `AdminDashboardView.vue` referans dilinden türetildi (üst metrik kartları, iyileştirilmiş tablo görünümü, form alanı hiyerarşisi)
	- Bu değişiklik sonrası frontend build tekrar başarılı: `npm run build`
- Derived ekran dönüşümü devam etti:
	- `AuctionCreateForm.vue` referans dilinden türetildi (çok bölümlü form yapısı, glass kart bölümleri, turbo konfigürasyon hiyerarşisi)
	- Bu değişiklik sonrası frontend build tekrar başarılı: `npm run build`
- Derived ekran dönüşümü tamamlandı:
	- `AdminReservationsView.vue` referans dilinden türetildi (arama alanı + rezervasyon tablo hiyerarşisi + durum rozetleri)
	- Admin rezervasyon veri çekimi dayanıklılığı artırıldı (`VITE_API_URL` kullanımı, payload shape fallback, `reserved_at` önceliği)
	- Bu değişiklik sonrası frontend build tekrar başarılı: `npm run build`
- UYGULAMAYI TEST ET çalıştırıldı:
	- `pytest tests/test_e2e_flow.py -q` → 1 passed
	- `pytest tests/test_booking_integration.py -q` → 2 passed
	- `pytest tests/test_realtime_sync.py -q` → 1 passed
	- `npm run build` → başarılı
	- Not: Pydantic v2 deprecation uyarıları mevcut, ancak test başarısını etkilemedi

## Son Kararlar
- Referans klasöründe şu an iki ana ekran mevcut: `HomeView` ve `MyReservationsView` (HTML + PNG).
- Bu iki ekran, tüm uygulamanın görsel dili için “canonical reference” olarak kullanılacak.
- Referansı olmayan ekranlar (Login/Admin/Auction Detail vb.) mevcut iki referansın renk, tipografi, spacing, kart, buton ve durum rozetleri diline sadık türetilecek.
- “Feature ekleme” yerine “görsel yeniden tasarım” yaklaşımı uygulanacak (işlevsel kapsam genişletilmeyecek).

## Sıradaki Adımlar
1. Görsel tutarlılık ve fonksiyon regresyon doğrulaması
2. Kritik kullanıcı yolculukları manuel doğrulama (full cycle simulation)

## Riskler / Notlar
- Referans klasöründe Admin/Login/Auction Detail için ayrı görsel bulunmadığından, bu ekranlar türetilmiş tasarım kararıyla üretilecektir.
- Frontend’de yeni UI yapılırken mevcut API sözleşmeleri ve store mantığı korunmalıdır.
- Tüm host/cors standardı (`127.0.0.1`) korunacak; yeniden tasarım backend davranışını etkilemeyecek.