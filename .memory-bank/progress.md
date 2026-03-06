# Proje İlerlemesi & Aşama Durumu (Progress Status)

**GÜNCEL DURUM:** `[BAKIM/MAINTENANCE MODU]` (Tüm aktif geliştirme fazları %100 tamamlandı)

## Faz 1: Çekirdek Kurulum ✅
- [x] Prisma Şemaları, DB bağlantıları
- [x] FastAPI / Vue 3 Proje İskeleti

## Faz 2: Auth & Kullanıcı Yönetimi ✅
- [x] JWT, Login / Register, Şifre Kurtarma
- [x] Kullanıcı Cüzdan / Bakiye Sistemi

## Faz 3: Açık Artırma (HotHour) & Rezervasyon ✅
- [x] CRUD Operasyonları (Oturum Yarat, Güncelle, İptal Et)
- [x] Dynamic Fiyat Motoru (AP Schedule, Turbo Trigger, Zaman/Fiyat Düşürme)
- [x] Rezervasyon DB İlişkileri, Check-in Mekanizması

## Faz 4: Socket.io & Gerçek Zamanlılık ✅
- [x] Redis Pub/Sub, Socket Emit olayları
- [x] Yeni Fiyat / Yeni Rezerve / Satıldı statülerinin Vue sayfalarında Canlı Güncellenmesi

## Faz 5: Studio (Çoklu Kiracı) Yönetimi ✅
- [x] Prisma Studio Entegrasyonu ve Veritabanı Migrasyonu
- [x] Geri dönük verilerin Script'ler ile güncellenmesi
- [x] Admin Panelinin sadece atanan stüdyoyu yönetecek statüye getirilmesi
- [x] Admin Studio Logo Upload ve Frontend JSON hata ayıklamaları

---

## Faz 6: SEO Uyumu 🔍 [AKTİF]

> **Bağlam:** Proje Vue 3 SPA. Tüm içerik JS ile render edilir. Ana sorun: arama motorları sayfaları doğru indeksleyemez. Çözüm: meta yönetimi, yapısal veri, teknik SEO ve uzun vadede SSG/SSR.

### 6.1 Temel SEO Altyapısı (Foundation) — Hızlı Kazanımlar
- [x] `index.html` → `lang="tr"` düzeltildi
- [x] `index.html` → `<meta name="description">`, Open Graph, Twitter Card, canonical meta etiketleri eklendi
- [x] `public/robots.txt` oluşturuldu (admin sayfaları engellendi)
- [x] `public/sitemap.xml` oluşturuldu (tüm statik sayfalar dahil)
- `[ ]` Uygun `favicon.ico` ve `apple-touch-icon.png` ekle (`public/` klasörüne)

### 6.2 Sayfa Bazlı Dinamik Meta Yönetimi
- [x] `@unhead/vue` kütüphanesi kuruldu (`createUnhead` API)
- [x] `frontend/src/main.js`'e `createUnhead()` ile entegre edildi
- [x] `HomeView.vue` — useHead() ile title + description + og + canonical
- [x] `AllAuctionsView.vue` — useHead() ile meta
- [x] `AuctionDetailView.vue` — auction verisine göre dinamik title/description/og/canonical
- [x] `HowItWorksView.vue` — useHead() ile meta
- [x] `FAQView.vue` — useHead() ile meta
- [x] `TermsOfUseView.vue` — useHead() ile meta (noindex)
- [x] `PrivacyPolicyView.vue` — useHead() ile meta (noindex)

### 6.3 Yapısal Veri (Structured Data / JSON-LD)
- [x] `HomeView.vue` → `WebSite` + `Organization` schema eklendi
- [x] `AuctionDetailView.vue` → `Event` schema eklendi (dinamik: stüdyo, tarih, fiyat)
- [x] `FAQView.vue` → `FAQPage` schema eklendi

### 6.4 Teknik SEO
- [x] Her sayfa için `<link rel="canonical">` desteği (useHead ile — 6.2'de tamamlandı)
- [x] `public/og-image.jpg` eklendi (1200×630, sosyal medya önizleme görseli)
- [x] `index.html` lang "tr", charset ve viewport düzeltildi (6.1'de tamamlandı)
- [x] Favicon seti eklendi: `favicon.ico`, `favicon.svg`, `favicon-96x96.png`, `apple-touch-icon.png`, `site.webmanifest`

### 6.5 İleri SEO — SSG/SSR (Büyük Mimari Değişiklik — Uzun Vadeli)
- `[ ]` `vite-plugin-ssr` veya Nuxt 3 migrasyonu değerlendir
- `[ ]` Dinamik auction sayfaları (`/auction/:id`) için prerender stratejisi belirle
- `[ ]` Statik sayfalar için SSG uygula (prerender at build time)

---
## Bakım (Maintenance) 🛠️
- `[ ]` Rutin hata bildirimlerini kontrol et, yalnızca mevcut stabil sistemde bugfix yap.

*Sistem v1.0 stabil. Faz 6 (SEO) aktif geliştirme fazıdır.*
