# Kodlama Standartları (Coding Standards)

## Backend
- async-first yaklaşım korunur
- hatalar loglanır ve uygun `HTTPException` ile yüzeye çıkarılır
- type hint kullanılır
- raw SQL son çaredir; Prisma tercih edilir
- tenant izolasyonu (`studioId`) kritik güvenlik kuralıdır

## v1.5 Domain Kuralları
- taxonomy string serbest metin olarak tutulmaz
- `slug` kararlı ve benzersiz olmalıdır
- relation include'ları kontrollü kullanılmalıdır
- işletme seviyesi veri ile fırsat seviyesi veri karıştırılmamalıdır
- master data panelden değil script ile yönetilir

## Frontend
- `script setup` ve composable deseni korunur
- yetkili isteklerde `fetchWithAuth` kullanılır
- response işlenmeden state'e yazılmaz
- filtre state'i mümkün olduğunca query param ile senkron kalır

## UI Terminolojisi
- kullanıcı metinleri: `işletme`, `fırsat`, `hizmet`
- teknik legacy isimler kod içinde korunabilir

## Script Kuralları
- CLI scriptleri açık kullanım mesajı vermeli
- seed scriptleri deterministik olmalı
- rastgele taxonomy eşleme yapılmamalı

## Çalışma İlkesi
Şu aşamada öncelik hızlı feature büyütmek değil, yapılan köklü değişiklikleri stabil ve izlenebilir tutmaktır.
