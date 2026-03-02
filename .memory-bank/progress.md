# İlerleme Durumu (Progress)

## Proje Faz Özeti

| Faz | Açıklama | Durum |
|---|---|---|
| MVP | Backend + Frontend temel mimari, DB, auth, socket | ✅ |
| R1 | Görsel tokenization (cam efekti, neon, dark tema) | ✅ |
| R2 | Mobil uyum (responsive, mobile-first) | ✅ |
| R3 | İş kuralları (race condition, fiyat düşüşü, e-posta) | ✅ |
| R4 | Güvenilirlik (DB reconnect, notifications, no-show) | ✅ |
| R5 | Admin Panel Refactoring (Composable + Utility mimarisi) | ✅ |
| R6 | Public View Refactoring (formatters, composables, PageBackground) | ✅ |
| Auth-R | Refresh token + Redis revocation (opsiyonel) | ✅ |

---

## Aktif Faz: Üretime Hazırlık

### Sıradaki Görevler

- [ ] **CI Pipeline** — Vitest + pytest pipeline yapılandırması
- [ ] **Deployment** — Staging → production sunucu kurulumu
- [ ] **Redis Aktivasyonu** — `.env` içinde `REDIS_URL` ayarı (ihtiyaç dahilinde)
- [ ] **E2E Testi** — Playwright / Cypress kullanıcı akışı (opsiyonel)
- [ ] **Ödeme Entegrasyonu** — `PAYMENTS_ENABLED=false` → ileriki faz

---

## Son Tamamlananlar (2026-03-02)

### Auth-R: Refresh Token + Revocation
- `ACCESS_TOKEN_EXPIRE_MINUTES` → 2 gün (2880dk)
- `REFRESH_TOKEN_EXPIRE_DAYS` → 7 gün
- `POST /api/v1/auth/refresh` ve `POST /api/v1/auth/revoke` endpointleri eklendi
- `app/core/token_revocation.py` — Redis destekli revocation (fallback: in-memory)
- `app/core/redis_client.py` — lazy Redis client + `ping_redis()`
- `/health` endpoint'ine Redis durumu eklendi
- `frontend/src/stores/auth.js` — `refreshToken`, `fetchWithAuth()`, `refreshTokens()` eklendi
- `requirements.txt` — `redis>=4.6.0` eklendi
- Backend pytest: **76 passed** | Frontend vitest: **121 passed**
