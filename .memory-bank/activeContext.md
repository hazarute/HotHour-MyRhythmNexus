# Aktif Bağlam (Active Context)

## Şu Anki Durum
**Tüm fazlar tamamlandı. Proje üretime hazır.**
Son tamamlanan faz: **Admin-R** — Real-time user creation socket broadcast (2026-03-03).

---

## Son Yapılan Değişiklikler (Admin-R: Real-time Users Socket Integration)

| Dosya | Değişiklik |
|---|---|
| `app/services/socket_service.py` | `emit_user_created(user: dict)` eklendi; sanitize + ISO timestamp payload |
| `app/api/auth.py` | Register endpointinde `await emit_user_created()` çağrısı (try-catch wrapper) |
| `frontend/src/composables/admin/useAdminUsers.js` | pageSize: 10→20, socket listeners (`setupSocketListeners`, `cleanupSocketListeners`), `onUserCreated()` event handler |
| `frontend/src/views/admin/AdminUsersView.vue` | `onUnmounted()` hook ile listener cleanup entegrasyonu |
| `tests/test_users_api.py` | Socket event broadcast testleri (6 test case) |
| `.memory-bank/progress.md` | Temizlendi ve yeniden yapılandırıldı (v2 format) |

**Test Sonuçları:** Backend pytest → 82 passed | Frontend vitest → 121 passed

**Özellikler:**
- ✅ Yeni kullanıcı kaydedildiğinde tüm admin panellere broadcast
- ✅ Sayfa başına maksimum 20 kayıt (pagination)
- ✅ En yeni kullanıcılar liste başında (createdAt DESC)
- ✅ Socket listener dinamik cleanup (memory leak önleme)

---

## Sıradaki Görev
`progress.md` içindeki `[ ]` işaretli ilk görev: **CI Pipeline yapılandırması**.

---

## Dikkat Edilmesi Gerekenler
- Redis `REDIS_URL` boş bırakıldığında uygulama in-memory fallback ile çalışır — bu kasıtlı bir tasarım tercihidir.
- `fetchWithAuth()` tüm kullanıcı API çağrılarında kullanılmalı; ham `fetch()` yasaktır.
- Format fonksiyonları için `utils/formatters.js`, statü haritaları için `utils/reservationStatus.js` tek kaynak.
- **YENI:** Socket listener cleanup mutlaka component `onUnmounted()` lifecycle'ında çağrılmalı; aksi takdirde listener accumulation → memory leak.
- **YENI:** Prisma Client Python dict döndürür (Pydantic model değil); `_sanitize_dict()` ile serialization yapılmalı.
- **YENI:** Frontend `fetchWithAuth()` Response object döndürür; `.json()` method mutlaka çağrılmalı veri parse etmek için.
