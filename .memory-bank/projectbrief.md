# Proje Özeti (Project Brief)

## Genel Bakış
**HotHour** — pilates stüdyoları için dinamik Hollanda açık artırması modeliyle boş seansları gelir fırsatına çeviren bir platformdur. Zamana karşı yarışan fiyat düşüşü mekanizması (FOMO), canlı socket senkronizasyonu ve rol tabanlı admin paneli ile tam kapsamlı bir SaaS çözümüdür.

## Temel Hedefler
1. **Sürdürülebilir Mimari:** Vue 3 Composable/Utility katmanı ile temiz, ölçeklenebilir frontend.
2. **Güvenli Auth:** JWT access token (2 gün) + refresh token (7 gün) + Redis destekli revocation (opsiyonel).
3. **Üretim Kalitesi:** Backend ve frontend test kapsamı, canlı socket bağlantısı, e-posta doğrulaması ile tam çalışır durumda.
4. **Ölçeklenebilirlik:** Redis, çok-worker/çok-sunucu ortamında kolayca aktif edilebilir (`REDIS_URL` ayarı).

## Mevcut Kapsam ve Durum
Tüm MVP ve refactor fazları tamamlandı. Proje üretime hazır:
- Backend: FastAPI, Prisma/PostgreSQL, Socket.IO, JWT auth, refresh token, revocation, e-posta.
- Frontend: Vue 3, Pinia, Tailwind, Composable/Utility mimarisi, reactive auth store.
- Test: Backend pytest (76 passed) + frontend vitest (121 passed) yeşil.

## Dahil Olmayanlar (Şimdilik)
- Redis zorunlu bağımlılık değil; `REDIS_URL` boş bırakıldığında in-memory fallback ile çalışır.
- Ödeme entegrasyonu (`PAYMENTS_ENABLED=false`).
- CI/CD pipeline (henüz yapılandırılmadı).
