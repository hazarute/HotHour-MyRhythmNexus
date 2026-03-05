# Aktif Bağlam (Active Context)

## Şu Anki Durum
**Prisma DB şeması modifiye edildi ve `Studio` yapısı Frontend & Backend ile baştan uca entegre edildi. Modeller üzerinde karşılaşılan `500 Server Error` eksiklikleri çözüldü, Seed / Script mimarisi genişletildi.**
Son tamamlanan görev: **Uygulama Çapında Kapsamlı Studio Veri Modeli Genişlemesi ve Hata Çözümleri** (2026-03-06).

---

## Son Yapılan Değişiklikler (Studio Modeli API, UI ve Veritabanı Fixleri)

| Dosya / Bileşen | Değişiklik |
|---|---|
| Scriptler | `scripts/assign_studio_to_auctions.py` ve `scripts/assign_studio_to_admins.py` olarak iki spesifik onarıcı araç eklendi. Ayrıca `seed_auctions.py` Business-Rule uyumlandırması yapılarak (mock Male/Female Users, Mock Studios) daha kararlı hale getirildi. |
| API / Model Katmanı | FastAPI & Pydantic 500 Serialization Hatası giderildi. Pydantic `AuctionResponse`, Prisma dönüşüm tipine (`StudioResponse`) zorlandı. Ayrıca `booking_service.py` ve İlişkisel get modeli (`include`) güncellerken düzeltildi. |
| CLI Araçları | `requirements.txt` içeriksel encode uyumsuzluğu PS Terminal bazlı düzeltilerek; eksik `aiohttp` ve `pytest-asyncio` paketleri yüklendi. |
| Frontend UI & Visual | `MyReservationsView.vue`, `AuctionDetailView.vue`, ve `AuctionCard.vue` sayfalarının arayüzüne (Google Maps, LogoUrl, Studio Name vb.) yansımalar ve harita link yönlendirmeleri eklendi. `useRouter` eksiği fixlendi. |
| Kapsamlı Testler | Pytest backend senaryoları koşularak Pydantic model uyuşmazlığının sorun çıkartmadığı ve yeni service eklemelerinin tüm ekosistemle barışık olduğu kanıtlandı. |

**Test Sonuçları (Güncel):**
- Backend pytest → 87/87 passed ✅
- Frontend vitest → 136/136 passed ✅
- Testler içerisinde script / fake DB işlemleri validasyondan geçti ✅

**Özellikler:**
- ✅ Yönetici ve oturumlara yönelik dev/prod bakım Scriptleri ve Komutları hazırlandı.
- ✅ Ön yüz tasarımları `Studio` yapısına ait alt bilgileri kapsayacak hale geldi (Map yönlendirmeleri, logolar).
- ✅ İş modellerindeki hatalar, eksik objeler ve router bazlı redirect problemleri onarıldı.
- ✅ Seed (Fake DB veri doldurucusu) artık tamamen Business-Rule, Studio-Rule, ve Gender-Rule limitasyonlarına uyum sağlayabiliyor.

---

## Sıradaki Görev
`progress.md` içindeki `[ ]` işaretli ilk görev: **CI Pipeline yapılandırması**.

---

## Dikkat Edilmesi Gerekenler
- Geliştirme/Yönlendirme sırasında Prisma'nın dict yerine kendi instance dönüşümlerinde `.model_dump()` veya doğru Pydantic Type Hinting (örn. `StudioResponse` ) yapılması kritik! (Serialization hataları yaşatır.)
- `fetchWithAuth()` tüm kullanıcı API çağrılarında kullanılmalı; ham `fetch()` yasaktır.
- Format fonksiyonları için `utils/formatters.js`, statü haritaları için `utils/reservationStatus.js` tek kaynak.
- Pydantic testlerinde yaşanabilecek `pytest_asyncio` kayıpları `requirements.txt` üzerinden tam kurulmalıdır.
