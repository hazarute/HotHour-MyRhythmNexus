# Aktif Bağlam (Active Context)

## Şu Anki Durum
**Tüm fazlar tamamlandı. Proje üretime hazır.**
Son tamamlanan faz: **Auth-R** — Refresh token akışı + Redis destekli revocation (2026-03-02).

---

## Son Yapılan Değişiklikler (Auth-R)

| Dosya | Değişiklik |
|---|---|
| `app/core/config.py` | `ACCESS_TOKEN_EXPIRE_MINUTES=2880`, `REFRESH_TOKEN_EXPIRE_DAYS=7`, `REDIS_URL`, `REDIS_REVOKED_KEY_PREFIX` eklendi |
| `app/core/security.py` | `create_refresh_token()` eklendi |
| `app/api/auth.py` | `login`/`register` artık `refresh_token` döndürüyor; `/refresh`, `/revoke` endpointleri eklendi |
| `app/core/token_revocation.py` | Redis destekli revocation (fallback: in-memory) |
| `app/core/redis_client.py` | Lazy Redis client + `ping_redis()` (yeni dosya) |
| `app/main.py` | `/health` endpoint'ine Redis ping durumu eklendi |
| `app/models/user.py` | `Token` modeline `refresh_token` alanı eklendi |
| `frontend/src/stores/auth.js` | `refreshToken` state, `fetchWithAuth()`, `refreshTokens()`, `logout()` revoke eklendi |
| `requirements.txt` | `redis>=4.6.0` eklendi |
| `.env` | `REDIS_URL`, `REDIS_REVOKED_KEY_PREFIX` eklendi |
| `tests/test_auth_refresh.py` | Refresh/revoke akışı için yeni test (yeni dosya) |
| `frontend/tests/useAuthStore.test.js` | Auth store unit testleri (yeni dosya) |

**Test Sonuçları:** Backend pytest → 76 passed | Frontend vitest → 121 passed

---

## Sıradaki Görev
`progress.md` içindeki `[ ]` işaretli ilk görev: **CI Pipeline yapılandırması**.

---

## Dikkat Edilmesi Gerekenler
- Redis `REDIS_URL` boş bırakıldığında uygulama in-memory fallback ile çalışır — bu kasıtlı bir tasarım tercihidir.
- `fetchWithAuth()` tüm kullanıcı API çağrılarında kullanılmalı; ham `fetch()` yasaktır.
- Format fonksiyonları için `utils/formatters.js`, statü haritaları için `utils/reservationStatus.js` tek kaynak.
- Yeni view eklenirken socket aboneliği `useAuctionSocket` composable'ından yapılmalı.
