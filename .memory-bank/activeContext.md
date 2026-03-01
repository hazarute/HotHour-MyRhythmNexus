# Aktif Bağlam (Active Context)

## Mevcut Durum / Şu Anki Zihinsel Odak
**Faz R6 — Public Views Yapısal Refactoring BAŞARIYLA TAMAMLANDI.**

2026-03-01: `frontend/src/views/` altındaki 8 public view dosyası (admin klasörü hariç) refactor edildi.
- `npm run build` → ✅ 108 modules, 0 hata, 2.43s
- `npm run test:unit` → ✅ 6/6 test geçti

### Tamamlanan Değişiklikler (R6)

**Yeni dosyalar oluşturuldu:**
- `frontend/src/utils/formatters.js` — `formatPrice`, `formatCurrency`, `formatDate`, `formatDateLong`, `formatTime`, `formatDateFull`
- `frontend/src/utils/reservationStatus.js` — `getStatusConfig`, `isCompletedStatus`, `isCopyAllowedStatus`
- `frontend/src/composables/useAuctionSocket.js` — socket bağlantısı, 6 event handler ve lifecycle yönetimi
- `frontend/src/composables/useReservations.js` — rezervasyon fetch/cancel/copy mantığı ve state yönetimi
- `frontend/src/composables/usePasswordStrength.js` — şifre gücü hesaplama
- `frontend/src/components/PageBackground.vue` — tekrar eden neon arka plan blob bileşeni

**View refactorları:**
- `HomeView.vue` — useAuctionSocket ile ~65 satır azaldı
- `AllAuctionsView.vue` — useAuctionSocket ile ~70 satır azaldı
- `AuctionDetailView.vue` — formatters import edildi, çift `auction_booked` off bug'ı giderildi
- `MyReservationsView.vue` — useReservations + formatters + reservationStatus ile ~165 satır azaldı
- `ProfileView.vue` — usePasswordStrength + formatDateFull ile ~25 satır azaldı
- `SignUpView.vue` — usePasswordStrength ile ~20 satır azaldı
- `LoginView.vue` — PageBackground bileşeni uygulandı
- `VerifyEmailView.vue` — PageBackground bileşeni uygulandı

## Son Tamamlanan (R6 Test Coverage)

**2026-03-01:** R6 refactor edilen tüm modüller için kapsamlı test dosyaları oluşturuldu:

| Test Dosyası | Testler | Durum |
|---|---|---|
| `tests/formatters.test.js` | 24 | ✅ |
| `tests/reservationStatus.test.js` | 21 | ✅ |
| `tests/usePasswordStrength.test.js` | 21 | ✅ |
| `tests/useAuctionSocket.test.js` | 20 | ✅ (`vi.hoisted()` singleton mock pattern) |
| `tests/useReservations.test.js` | 26 | ✅ |
| Önceki admintest'ler (3 dosya) | 6 | ✅ |
| **TOPLAM** | **118/118** | ✅ |

`npm run test:unit -- --run` → **8 test dosyası, 118 test, 0 hata**

## Sıradaki Görev (AI Seansı İçin)
R6 + R6 test coverage tamamlandı. Proje "Üretime Hazır" durumunda.

Sıradaki olası adımlar:
1. **CI Entegrasyonu** — Vitest + pytest pipeline'a ekleme
2. **E2E Test** — Playwright/Cypress user-flow
3. **Deployment** — staging/prod

## Dikkat Edilmesi Gerekenler
* Yeni view eklenirken socket aboneliği `useAuctionSocket` composable'ından kullanılmalı.
* Format fonksiyonları için `utils/formatters.js` tek kaynak — inline tanımlama yapılmamalı.
* `utils/reservationStatus.js` — rezervasyon durumu eşlemesi için tek kaynak.
* Admin view'larına dokunulmadı — R5 ile zaten clean mimaride.
