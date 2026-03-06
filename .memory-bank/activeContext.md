# Aktif Bağlam (Active Context)

## Mevcut Durum
Proje **v1.0 stabil** durumdadır. Yeni odak: **SEO Uyum Fazı** başlamıştır.

## Yakın Zamanda Tamamlananlar
- `uploads/` klasörü `.gitignore`'a eklendi ve GitHub'dan temizlendi.
- `Studio` nesnesinin sisteme tam entegrasyonu tamamlandı (v1.0).
- Tüm çekirdek modüller (Auth, Auction, Rezervasyon, WebSocket, Multi-tenant Admin) stabil.

## Mevcut Zihinsel Odak (Yapay Zeka İçin Direktif)
**Faz 6: SEO Uyumu** aktif olarak devam etmektedir.
Proje **Vue 3 SPA** mimarisindedir. Temel SEO sorunu: tüm içerik JavaScript ile render edildiği için arama motorları sayfaları doğru indeksleyemez.

### Mevcut SEO Sorunları (Tespit Edildi - 6 Mart 2026)
- `index.html`'de `lang="en"` → Türkçe içerik için `lang="tr"` olmalı
- Tüm sayfalar için tek bir `<title>` ve meta description yok
- Open Graph / Twitter Card meta etiketleri hiç yok
- `public/robots.txt` yok
- `public/sitemap.xml` yok
- `favicon.ico` yok (sadece `vite.svg` var)
- Sayfa bazlı dinamik meta yönetimi yok (`@unhead/vue` kurulmamış)
- Yapısal veri (JSON-LD) hiç yok
- `canonical` URL etiketleri yok
- SSR/SSG desteği yok (büyük mimari değişiklik – uzun vadeli)
