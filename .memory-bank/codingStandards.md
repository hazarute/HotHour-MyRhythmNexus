# Kodlama Standartları (Coding Standards)

## 1. Genel Mimari Standartlar
* **Temiz Kod (Clean Code):** Fonksiyonlar tek boyutlu olmalı. Bir Vue dosyası `template`, `script` ve `style` içerse de `script` bölümü 100-150 satırı aştığında ilgili logic bir Composable veya dış fonksiyon olarak çıkartılmalıdır.
* **Tasarım Kalıpları:** Frontend de dahi modüller birbiri ile gevşek (loosely coupled) şekilde bağlanmalıdır.
* **Bozmama Garantisi (Regression-Free):** Mevcut iş kuralına (business logic) göre yazılmış tüm senaryolar (race condition alert, error status, z-index dış tıklama, iptal onayı vb.) refactoring yapıldıktan sonra aynı kalmalıdır.

## 2. İsimlendirme Kuralları (Adlandırma)

### Frontend (Vue 3, JS) Yeni Refactor Kuralları
* **Composables:** Mutlaka `use` kelimesiyle başlar ve CamelCase adlandırılır. Örn: `useAdminNotifications.js`, `useAdminReservations.js`.
* **Utils/Helpers:** Görevi anlatan basit `camelCase` dosyalar. Örn: `formatting.js`, `adminApi.js`.
* **View (Page) İçin Alt Bileşenler:** Parent'ın adını referans alan PascalCase. Örn: `AdminDashboardView.vue`'nun parçası `AdminDashboardFilterBar.vue` veya genel ise `components/admin/AdminNotificationDropdown.vue`.

## 3. Vue 3 (Composition API) Standartları
* Kodun başı `script setup` ile hazırlanmalı. Klasik `export default { setup() }` veya Options API **kesinlikle KULLANILMAYACAKTIR**.
* Sadece gerektiği kadar data Reaktif (`ref`, `reactive`) olmalıdır. Sabit metadata'lar (örn. statü renk listesi) düz obje (Object) olmalı dışarıdan export edilmelidir.
* Geri çağırma temizliği (Cleanup): `onMounted`'da event listener eklendiyse (ör: dışarı tıklama), **mutlaka** `onUnmounted`'da o listener kaldırılmalıdır.

## 4. API / Fetch Standartları
* Ham API call'larının View'da bulunması R5 sonrası yasaktır.
* API call hataları (`!response.ok`), uygun şekilde catch edilip frontend hata mesajı/state değişkenleri güncellenmelidir. `console.error` ile bırakılmamalıdır.
* Component, backend yanıt formatını deşifre etmek zorunda olmamalı; veri, Composable/Client seviyesinde parse edilip component'e saf bir şekilde sunulmalıdır.

## 5. Metadata/Formatlama Standartları
Tüm tarih formatlama, statü badge (etiket rengi belirleme) ve para birimi sembolleri `utils/` veya `constants/` altındaki `status_metadata.js`, `format_helpers.js` gibi dosyalardan import edilmelidir. Ayrı yerlerde kopyala/yapıştır (copy-paste) formatlama kod bloku **KESİNLİKLE OLMAMALIDIR**.
