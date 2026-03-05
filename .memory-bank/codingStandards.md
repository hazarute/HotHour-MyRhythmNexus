# Kodlama Standartları (Coding Standards)

## Python / Backend
- **Asynchronous First:** Veritabanı işlemleri, redis okumaları ve API uçları %100 async / await olmalıdır.
- **Hata Yönetimi (Error Handling):** Try-Except bloklarında hatalar loglanıp mutlaka `HTTPException` (FastAPI) fırlatılarak önyüze JSON standart detay verilmelidir (`detail="Mesaj"`).
- **Typing:** Type Hinting kuraldır (`str, int, Optional[Dict], List[Any]`).
- **Prisma Kullanımı:** Raw SQL yazılmaktan kaçınılacak. Veriler çekilirken bağlı tablolar `include={"studio": True}` sözdizimi ile eklenecektir.

## Vue / Frontend
- `<script setup>` desenine kesin olarak uyulmalıdır. Reactivity için `ref` veya `computed` kullanılmalı, mutation içeren değişkenler asla template'de manipüle edilmemeli (sadece fonksiyon içinde).
- **Composable Pattern:** Sayfa büyüdükçe (Örn: Admin Panel), içerisindeki state ve fonksiyon karmaşasını çözmek için mantık `usePageName.js` içine (componsables klasörü) taşınmalı.
- **Styling:** Tailwind CSS tabanlı stiller ile ilerlenecek. Karanlık mod (dark) standart olarak uygulanmalıdır.
- **Fetch Sınıfı:** Servis çağrılarında (backend'den veri çekerken) yetkili istekler `useAuthStore().fetchWithAuth` metoduyla atılır. Gelen response `await response.json()` yapmadan objeye (State'e) eşitlenmemelidir.

## Versiyon Kontrol & Git
- `feat:`, `fix:`, `chore:`, `refactor:` standart repo mesaj formatları kullanılır.
- Kodlar "Working / Running" durumundan ödün verilmeden Git'e atılır. Sadece stabil kod deploy/kabul edilir.
