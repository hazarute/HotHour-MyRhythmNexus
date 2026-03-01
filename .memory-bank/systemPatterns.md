# Sistem Mimarisi (System Patterns)

## Mimari Genel Bakış
HotHour, backend'de **API-first**, frontend'de **Vue 3 + Pinia + Tailwind** ile çalışan bir SPA mimarisine sahiptir. İletişim REST API ve Socket.IO (Gerçek zamanlı fiyat/statü akışı) üzerinden yürütülür. Sistem bu haliyle üretime hazır seviyeye gelmiştir.

## Yeni Mimari Odak: Clean Architecture in Vue (Faz R5)
Projede UI component tokenization (Faz R1) süreci başarıyla tamamlanmıştır. Mevcut hedef, Vue'nun gücünden tam yararlanmak için **"Composable Pattern"** ve **"Service Layer"** mimarilerini Vue projelerine yansıtmaktır.

### 1) Centralized Domain Metadata Pattern (Tek Gerçeklik Kaynağı)
Uygulama içinde dağılmış olan durum (status) ifli yapıları, tek bir utility olarak soyutlanacaktır.
- **Problem:** -if="status === 'ACTIVE'" ve elle yazılan class/renk tanımları tüm view'lara dağılmış durumda.
- **Çözüm (Hedef):** utils/admin/status_metadata.js gibi yapılar kurularak component'in sadece const { label, class } = getAuctionStatusMeta(status) demesi sağlanacaktır. (Bu pattern hem Reservation hem de Auction statusleri için uygulanmıştır).

### 2) Admin API Fetch Abstraction (Custom Async Wrapper)
API istekleri her sayfada token kontrolü, baseUrl okuma, .env yapılandırması gerektirmektedir.
- **Hedef:** pi_client.js veya helper fonksiyon aracılığıyla tüm admin isteklerinin (GET, POST, vb.) interceptor mantığına benzer basit bir wrapper üzerinden geçirilmesi. const data = await adminFetch('/api/v1/...').

### 3) Composable Split Pattern (Mantıksal Ayrıştırma)
Vue 3 script setup içindeki devasa mantık (logic) yığınları ilgi alanlarına (concerns) göre bölünerek composables/admin/ dizinine alınacaktır.
- **Örnekler:**
  - useAdminNotifications.js -> Bildirimleri çekme, okundu işaretleme, silme, loading ve badge hesaplama (Reactive State + Actions).
  - useAdminAuctions.js -> Dashboard listelerini çekme, filtreleme state'i ve sayfalama logic'i.
  - useAdminReservations.js -> Check-in, Cancel aksiyonları.

### 4) Component Decomposition Pattern
Yalnızca View'lara ait olan, ancak DOM'u aşırı dolduran yapılar <template> içinden çıkartılarak components/admin/ altına alınmıştır.
- **Notification Dropdown:** Bağımsız bir <AdminNotificationDropdown /> bileşeni.
- **Aksiyon Butonları:** Tekrar eden cancel/check-in/detail buton kombinasyonları alt bileşenlere çıkarılabilir.

### 5) Functional Isolation Rule (Devam Eden Kural)
Refactoring yapılırken;
- Pinia Store'lar (ör: global auth/auction socket) **bozulmayacaktır**.
- Backend Endpoint ve Prisma şemasına **kesinlikle** dokunulmayacaktır (mevcut backend mükemmel çalışmaktadır).
- Refactor sonrası tüm view'lar mevcut HTML iskeleti ile ayni id/class yapılarına derlenmeli, tasarımda piksel kayması yaşanmamalıdır.
