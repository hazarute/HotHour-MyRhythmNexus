# Teknoloji Bağlamı (Tech Context)

## Başarıyla Oturtulmuş Teknoloji Yığını (KORUNACAK)

| Katman | Teknoloji | Not |
| --- | --- | --- |
| Backend | Python 3.10+, FastAPI, Uvicorn, fastapi-mail | Çalışır durumda, stabil. |
| ORM/DB | Prisma Client Python, PostgreSQL | Migration'lar güncel, lock mekanizmaları çalışıyor. |
| Realtime | Socket.IO AsyncServer + socket.io-client | Çoklu client desteği, performansı yüksek. |
| Frontend | Vue 3 (Composition API), Pinia, Vue Router | State aktarımı, Route guard'ları işlevsel. |
| Styling | Tailwind CSS (Vite/PostCSS) | Referans tasarımlara uyumlu tam set tokenlar. |
| Test | pytest | E2E, Realtime, DB entegrasyon testleri (%90+). |

## Admin Refactor Sürecindeki Teknik Kurallar (R5)

### 1) Kapsüllü JavaScript / ES6 Modülleri
- Refactoring araçları olan `composables` (.js) ve `utils` (.js) dosyalarında standart Javascript fonksiyonları tanımlanacak (Vue'nun `ref`, `computed` importlarıyla reaktivite sağlanacak).
- Uygulamaya Axios vb. yeni bir bağımlılık eklemeden, mevcut native `fetch` API ile wrapper yazılacaktır.

### 2) Local State vs Global State Disiplini
- UI bazlı loading (ör: butona  tıklandığında dönen spinner), error mesajları ve pagination **Local State**'tir. Bu state'ler doğrudan composable modüllerinde `ref()` olarak tutulup export edilecek, store'a şişirilmeyecektir.
- Oturum (Auth token) ve Global veriler **Pinia'da** (Global State) kalmaya devam edecektir. Composable'lar gerektiğinde store'u (*useAuthStore*) kendi içlerinde çağırabilir.

### 3) Komponent İletişimi (Props / Emits)
- Büyük view'lar parçalanırken, parent (View) ile child (örn: ActionToolbar) arasındaki iletişim Vue 3'ün `defineProps` ve `defineEmits` fonksiyonlarıyla tip güvenli bir şekilde yapılacaktır.
- Gereksiz Prop Drilling önlenecek, 2 seviyeden derine veri taşınması gerektiğinde Composable veya Provide/Inject düşünülmelidir.

### 4) Bağlantı ve Hata Toleransı
- Backend connection'larında (Socket kesilmesi, Prisma reconnect vb.) sağlanan yüksek dayanıklılık aynen sürdürülecektir.
- API wrapper yazılırken mutlaka HTTP çağrılarındaki "auth" hatası veya "server error" durumları global/local error state'ine yönlendirilmeli (mevcut toast veya error-alert bileşenleri kullanılmalı).
