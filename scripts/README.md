# Admin Script Belgeleri

## 📜 Scripts İçeriği

1. **create_admin.py** - Admin hesabı oluşturma
2. **list_admins.py** - Admin hesaplarını listeleme
3. **delete_admin.py** - Admin hesabı silme
4. **delete_user.py** - Herhangi bir kullanıcı hesabı silme
5. **railway_debug.ps1** - Railway backend/frontend log ve SSH debug yardımcısı
6. **railway_fetch_diagnose.py** - Failed to fetch/CORS/API URL teşhis scripti
7. **clear_db.py** - Veritabanını temizleme (tümünü veya sadece oturum/rezervasyonları)
8. **reset_and_seed.py** - Veritabanını tek komutta temizleyip taxonomy + mock veri + lokal admin kurma
9. **taxonomy/create_sector.py** - Yeni sektör oluşturma
10. **taxonomy/list_sectors.py** - Sektörleri listeleme
11. **taxonomy/deactivate_sector.py** - Sektör pasifleştirme
12. **taxonomy/create_service_category.py** - Yeni hizmet kategorisi oluşturma
13. **taxonomy/list_service_categories.py** - Hizmet kategorilerini listeleme
14. **taxonomy/deactivate_service_category.py** - Hizmet kategorisi pasifleştirme
15. **taxonomy/seed_taxonomy.py** - Varsayılan sektör ve hizmet kategorisi setini yükleme
16. **taxonomy/backfill_taxonomy.py** - Mevcut işletme/fırsat kayıtlarını dry-run destekli eşleme
17. **create_studio.py** - Studio oluşturma

---

## 🔁 reset_and_seed.py

Lokal geliştirici akışı için veritabanını temizler, taxonomy verisini yükler, sektör-hizmet ilişkileri tutarlı mock fırsat verisini üretir ve istenirse test adminini yeniden oluşturur.

### Kullanım

```bash
python scripts/reset_and_seed.py
python scripts/reset_and_seed.py --skip-admin
python scripts/reset_and_seed.py --admin-studio-name "Neon Fit Academy"
```

### Varsayılanlar

- admin email: `local.admin@example.com`
- admin şifre: `TestPass123!`
- admin studio: `Neon Fit Academy`

Not: Varsayılan seed artık heuristic backfill kullanmaz. İşletmeler sektörleriyle, fırsatlar da doğrudan doğru hizmet kategorileriyle oluşturulur.

---

## 🚆 railway_debug.ps1

Railway üzerinde canlıya alınmış backend/frontend servislerine bağlanıp log ve SSH debug yapmak için kullanılır.

### Gereksinimler

- Railway CLI kurulu olmalı
- Railway hesabına login yapılmış olmalı

```bash
npm i -g @railway/cli
railway login
```

### Kullanım

```powershell
.\scripts\railway_debug.ps1 -Mode logs -BackendService <backend-service> -FrontendService <frontend-service> -Lines 300 -Follow
.\scripts\railway_debug.ps1 -Mode ssh-backend -BackendService <backend-service>
.\scripts\railway_debug.ps1 -Mode ssh-frontend -FrontendService <frontend-service>
```

### Opsiyonel Env Değişkenleri

```powershell
$env:RAILWAY_BACKEND_SERVICE="HotHour-MyRhythmNexus"
$env:RAILWAY_FRONTEND_SERVICE="HotHour-FrontEnd"
$env:RAILWAY_ENVIRONMENT="production"
.\scripts\railway_debug.ps1 -Mode logs -Follow
```

### Modlar

- `logs`: backend/frontend loglarını çeker
- `ssh-backend`: backend servise SSH açar
- `ssh-frontend`: frontend servise SSH açar
- `help`: kısa yardım ekranı

---

## 🔎 railway_fetch_diagnose.py

Frontend bundle içindeki API URL’i, backend erişilebilirliği ve CORS preflight durumunu tek komutta kontrol eder.

### Kullanım

```powershell
python .\scripts\railway_fetch_diagnose.py \
   --frontend-url https://hothour-frontend.up.railway.app \
   --backend-url https://hothour-myrhythmnexus-production.up.railway.app \
   --origin https://hothour-frontend.up.railway.app \
   --origin https://kayraspace.com \
   --origin https://www.kayraspace.com \
   --origin https://tugbadanspor.kayraspace.com \
   --railway-service-backend "HotHour-MyRhythmNexus" \
   --railway-service-frontend "HotHour - FrontEnd" \
   --railway-environment production \
   --railway-lines 120
```

### Ne kontrol eder?

- Frontend index + main bundle bulunuyor mu?
- Bundle içinde doğru backend URL gömülü mü?
- Bundle’da `localhost` izi var mı?
- Backend `/health` ve `/api/v1/auctions` yanıt veriyor mu?
- Verdiğin origin listesi için CORS preflight başarılı mı?
- Opsiyonel olarak Railway backend/frontend son log örneklerini gösterir.

---

## 📝 create_admin.py

Admin hesabı oluşturmak için kullanılır.

### Kullanım

```bash
python scripts/create_admin.py <email> <password> <full_name> [phone] [gender]
```

### Parametreler

| Parametre   | Gerekli | Açıklama | Örnek |
|-------------|---------|----------|--------|
| email       | ✅      | Yöneticinin email adresi (unique) | admin@example.com |
| password    | ✅      | Yöneticinin şifresi (min 6 karakter) | mySecurePass123 |
| full_name   | ✅      | Yöneticinin adı soyadı | Ahmet Yönetici |
| phone       | ❌      | Telefon numarası. Belirtilmezse otomatik oluşturulur | +905551234567 |
| gender      | ❌      | Cinsiyet: `MALE` veya `FEMALE` | MALE |

### Örnekler

#### Minimal
```bash
python scripts/create_admin.py admin@hotour.com pass123456 "Admin Kullanıcı"
```

#### Tam detaylı
```bash
python scripts/create_admin.py admin@hotour.com SecurePass123 "Ahmet Yönetici" "+905551234567" MALE
```

#### Windows (PowerShell)
```powershell
python scripts/create_admin.py "admin@hotour.com" "pass123456" "Admin Kullanıcı" "+905551234567" "MALE"
```

### Çıktı

Başarılı oluşturulma durumunda:
```
✅ Admin hesabı başarıyla oluşturuldu !
   ID: 1
   Email: admin@hotour.com
   Ad Soyad: Admin Kullanıcı
   Telefon: +905551234567
   Role: ADMIN
   Doğrulandı: True
```

### Özellikler

- ✅ Email ve phone uniqueness kontrolü
- ✅ Şifre otomatik hash yapılır (pbkdf2_sha256)
- ✅ Admin rolü atanır
- ✅ Hesap otomatik doğrulanmış (isVerified: true)
- ✅ Phone boşsa otomatik oluşturulur
- ✅ Basit input validasyonu

### Gereksinimler

- Proje environment'i kurulu ve `.env` dosyası yapılandırılmış
- `DATABASE_URL` .env dosyasında tanımlanmış
- Tüm dependencies kurulu (`requirements.txt`)

### Sorun Giderme

| Sorun | Çözüm |
|--------|---------|
| "Hata: EMAIL zaten kayıtlı" | Farklı bir email kullanın |
| "Hata: TELEFON zaten kayıtlı" | Farklı bir telefon numarası kullanın veya telefon parametresini boş bırakın |
| "Hata: DATABASE_URL env'de yok" | `.env` dosyasını kontrol edin |
| "ModuleNotFoundError" | `pip install -r requirements.txt` çalıştırın |

---

## 🏬 create_studio.py

Studio (işletme) kaydı oluşturmak için kullanılan yardımcı script.

### Kullanım

```bash
python scripts/create_studio.py "Studio Adı" ["Adres"] ["Logo URL"] ["Google Maps URL"] --sector <id|slug> --sector <id|slug>
```

### Açıklama

- `name` (zorunlu): İşletme adı.
- `address` (opsiyonel): Adres bilgisi.
- `logo_url` (opsiyonel): Logo dosyası/URL'si.
- `google_maps_url` (opsiyonel): Google Maps bağlantısı.
- `--sector` (opsiyonel, tekrar edilebilir): Sektör ID veya slug. Birden fazla `--sector` ile birden fazla sektör bağlanabilir.

Script, verilen sektörleri `scripts.taxonomy._common.resolve_sector` ile çözer; bulunamayan veya `isActive=false` olan sektörler hata verir.
Başarılı oluşturma durumunda yeni kaydın `ID`, `İsim`, `Adres` ve bağlı sektörler konsola yazdırılır.

### Örnekler

Minimal:
```bash
python scripts/create_studio.py "Neon Fit Academy"
```

Logo ve adres ile:
```bash
python scripts/create_studio.py "Neon Fit Academy" "Ataşehir, İstanbul" "https://cdn.example.com/logo.png" "https://maps.google.com/?q=..."
```

Birden fazla sektör bağlama:
```bash
python scripts/create_studio.py "Neon Fit Academy" --sector wellness --sector 3
```

PowerShell (Windows):
```powershell
python .\scripts\create_studio.py "Neon Fit Academy" "Adres" "https://cdn.example.com/logo.png" "https://maps.google.com/?q=..."
```

### Gereksinimler

- Proje environment kurulmuş ve `.env` içinde `DATABASE_URL` tanımlı.
- `requirements.txt` içindeki bağımlılıklar yüklü.
- Taxonomy (sektör) verisi önceden oluşturulmuş olmalı.

### Hata Durumları

- `Sektör bulunamadı`: Verilen sektör ID/slug bulunamadı.
- `Pasif sektör kullanılamaz`: Sektör `isActive=false` olduğu için kullanılamaz.
- Veritabanı bağlantı hatalarında script exception fırlatır ve hata mesajı gösterilir.


---

## 🧭 Taxonomy Master Data Scriptleri

Bu scriptler yalnızca proje sahibi / SSH erişimi olan operatör için tasarlanmıştır. Admin panelinden sektör veya hizmet kategorisi oluşturma yoktur; master veri yönetimi burada yapılır.

### taxonomy/create_sector.py

```bash
python scripts/taxonomy/create_sector.py "Wellness"
python scripts/taxonomy/create_sector.py "Pilates ve Yoga" --slug pilates-yoga --description "Mat ve reformer odakli hizmetler"
```

### taxonomy/list_sectors.py

```bash
python scripts/taxonomy/list_sectors.py
python scripts/taxonomy/list_sectors.py --all
```

### taxonomy/deactivate_sector.py

```bash
python scripts/taxonomy/deactivate_sector.py 3
python scripts/taxonomy/deactivate_sector.py wellness
```

### taxonomy/create_service_category.py

```bash
python scripts/taxonomy/create_service_category.py "Aletli Pilates" --sector wellness
python scripts/taxonomy/create_service_category.py "Acik Grup Dersi" --sector 2 --slug acik-grup
```

### taxonomy/list_service_categories.py

```bash
python scripts/taxonomy/list_service_categories.py
python scripts/taxonomy/list_service_categories.py --all
python scripts/taxonomy/list_service_categories.py --sector wellness
```

### taxonomy/deactivate_service_category.py

```bash
python scripts/taxonomy/deactivate_service_category.py 5
python scripts/taxonomy/deactivate_service_category.py aletli-pilates
```

### Notlar

- `--sector` parametresi hem ID hem slug kabul eder.
- Scriptler kayıt silmez; `isActive = false` ile pasifleştirir.
- Slug verilmezse isimden otomatik üretilir.

### taxonomy/seed_taxonomy.py

```bash
python scripts/taxonomy/seed_taxonomy.py
python scripts/taxonomy/seed_taxonomy.py --update-existing
```

Varsayılan çok sektörlü taxonomy setini idempotent şekilde kurar. Mevcut slug'lar korunur; `--update-existing` verilirse açıklama/ad gibi metadata da güncellenir.

### taxonomy/backfill_taxonomy.py

```bash
python scripts/taxonomy/backfill_taxonomy.py
python scripts/taxonomy/backfill_taxonomy.py --apply
python scripts/taxonomy/backfill_taxonomy.py --apply --force-categories
```

Mevcut işletme isimleri ve fırsat başlık/açıklamalarındaki anahtar kelimelere göre öneri üretir. Varsayılan mod dry-run'dır; önce planı görür, sonra `--apply` ile uygularsınız.

---

## 📋 list_admins.py

Tüm admin hesaplarını listeler.

### Kullanım

```bash
python scripts/list_admins.py [--verbose|-v] [--help|-h]
```

### Parametreler

| Parametre | Açıklama |
|-----------|----------|
| --verbose, -v | Tüm detayları göster (telefon, cinsiyet, vb) |
| --help, -h | Yardım mesajını göster |

### Örnekler

```bash
# Temel listeleme
python scripts/list_admins.py

# Detaylı listeleme
python scripts/list_admins.py --verbose

# Kısa format
python scripts/list_admins.py -v
```

### Çıktı Örneği

**Temel:**
```
📋 Toplam Admin Sayısı: 2

╔════╦════════════════════╦═════════════════╦═════════════╦─────────────────────╗
║ ID ║ Email              ║ Ad Soyad        ║ Doğrulandı  ║ Oluşturulma         ║
╠════╬════════════════════╬═════════════════╬═════════════╬─────────────────────╣
║ 1  ║ admin@hotour.com   ║ Admin Kullanıcı ║ ✅          ║ 25.02.2026 14:30    ║
║ 2  ║ manager@hotour.com ║ Ahmet Yönetici  ║ ✅          ║ 24.02.2026 10:15    ║
╚════╩════════════════════╩═════════════════╩═════════════╩─────────────────────╝
```

**Detaylı (--verbose):**
```
📋 Toplam Admin Sayısı: 2

╔════╦════════════════════╦═════════════════╦═════════════════╦══════════╦═══════════╦──────────────────────╗
║ ID ║ Email              ║ Ad Soyad        ║ Telefon         ║ Cinsiyet ║ Doğrulandı║ Oluşturulma          ║
╠════╬════════════════════╬═════════════════╬═════════════════╬══════════╬═══════════╬──────────────────────╣
║ 1  ║ admin@hotour.com   ║ Admin Kullanıcı ║ +905551234567   ║ MALE     ║ ✅        ║ 25.02.2026 14:30     ║
║ 2  ║ manager@hotour.com ║ Ahmet Yönetici  ║ +905559876543   ║ MALE     ║ ✅        ║ 24.02.2026 10:15     ║
╚════╩════════════════════╩═════════════════╩═════════════════╩══════════╩═══════════╩──────────────────────╝
```

### Özellikler

- ✅ Tüm admin hesaplarını tablo formatında göster
- ✅ Email, ad soyad, doğrulama durumu ve oluşturulma tarihi
- ✅ Opsiyona: Telefon ve cinsiyet bilgisi
- ✅ Doğrulama durumunu emoji ile göster (✅/❌)

---

## 🗑️ delete_admin.py

Admin hesabı silmek için kullanılır.

### Kullanım

```bash
python scripts/delete_admin.py <admin_id_veya_email> [--force]
```

### Parametreler

| Parametre | Gerekli | Açıklama |
|-----------|---------|----------|
| admin_id_veya_email | ✅ | Admin ID'si (sayı) veya Email adresi |
| --force | ❌ | Onay dialogs'u atla ve direkt sil |

### Örnekler

```bash
# ID ile silme (onay sorar)
python scripts/delete_admin.py 1

# Email ile silme (onay sorar)
python scripts/delete_admin.py admin@example.com

# Onay olmadan silme (--force)
python scripts/delete_admin.py 1 --force
python scripts/delete_admin.py admin@example.com --force
```

### Çıktı Örneği

**Onay ile:**
```
⚠️  Silmek üzere olan admin hesabı:
   ID: 1
   Email: admin@example.com
   Ad Soyad: Admin Kullanıcı
   Oluşturulma: 2026-02-25 14:30:00.123456+00:00

Bu admin hesabını silmek istediğinize emin misiniz? (evet/hayır): evet

✅ Admin hesabı başarıyla silindi !
   ID: 1
   Email: admin@example.com
   Ad Soyad: Admin Kullanıcı
```

**Hata durumunda:**
```
❌ Hata: Admin bulunamadı (ID/Email: 999)
```

### Özellikler

- ✅ ID veya Email ile arama yapabilir
- ✅ Silme öncesi onay istenir (--force ile atla)
- ✅ Silmek üzere olan hesabın detaylarını göster
- ✅ Başarılı silme mesajı

### ⚠️ Dikkat

- Silme işlemi **geri alınamaz**
- Normal kullanıcıları silmek için bu script kullanılamaz (sadece ADMIN role'ü)

---

## 🗑️ delete_user.py

Herhangi bir kullanıcı hesabı silmek için kullanılır (Admin ve normal kullanıcılar).

### Kullanım

```bash
python scripts/delete_user.py <user_id_veya_email> [--force]
```

### Parametreler

| Parametre | Gerekli | Açıklama |
|-----------|---------|----------|
| user_id_veya_email | ✅ | Kullanıcı ID'si (sayı) veya Email adresi |
| --force | ❌ | Onay dialogs'u atla ve direkt sil |

### Örnekler

```bash
# ID ile silme (onay sorar)
python scripts/delete_user.py 1

# Email ile silme (onay sorar)
python scripts/delete_user.py user@example.com

# Onay olmadan silme (--force)
python scripts/delete_user.py 1 --force
python scripts/delete_user.py user@example.com --force
```

### Çıktı Örneği

**Onay ile:**
```
⚠️  Silmek üzere olan kullanıcı hesabı:
   ID: 5
   Email: user@example.com
   Ad Soyad: Ahmet Yücel
   Role: USER
   Email Doğrulanmış: Evet
   Oluşturulma: 2026-02-25 10:15:00.123456+00:00

Bu kullanıcı hesabını silmek istediğinize emin misiniz? (evet/hayır): evet

✅ Kullanıcı hesabı başarıyla silindi !
   ID: 5
   Email: user@example.com
   Ad Soyad: Ahmet Yücel
   Role: USER
```

**Hata durumunda:**
```
❌ Hata: Kullanıcı bulunamadı (ID/Email: 999)
```

### Özellikler

- ✅ ID veya Email ile arama yapabilir
- ✅ Silme öncesi onay istenir (--force ile atla)
- ✅ Silmek üzere olan hesabın tüm detaylarını göster (Role, Email doğrulama durumu, vb)
- ✅ Başarılı silme mesajı
- ✅ Admin ve normal kullanıcı ayrımı yapmaz, tüm kullanıcıları silebilir

### ⚠️ Dikkat

- Silme işlemi **geri alınamaz**
- Admin hesaplarını silmek için `delete_user.py` veya `delete_admin.py` kullanabilirsiniz
- Kullanıcı ile ilişkili tüm veriler (rezervasyonlar, teklifler, vb) silinecektir

---

## 🧹 clear_db.py

Veritabanını hızlıca temizlemek veya sadece oturum/veritabanı kalıntılarını silmek için kullanılır.

- **Varsayılan** davranış: tüm rezervasyonlar, bildirimler, açık artırmalar ve kullanıcılar (adminler dahil) silinir.
- `--sessions-only` seçeneği ile **rezervasyonlar** ve **oturumlar (auction kaydı)** temizlenir; diğer kayıtlar korunur.

### Kullanım

```bash
# Tüm veritabanını sil
python scripts/clear_db.py

# Sadece rezervasyonlar, oturumları (açık artırmalar)  sil
python scripts/clear_db.py --sessions-only
```

### Notlar

- İşlem başlamadan önce kullanıcıdan onay istenir.
- `--sessions-only` modu yalnızca rezervasyonlar ve açık artırma/oturum kayıtlarını siler.

---

## 🛠️ Genel Gereksinimler

Tüm scriptlerin çalışması için:

1. **Python 3.8+** kurulu olmalı
2. **Proje Environment** yapılandırılmış olmalı
3. **`.env` dosyası** aşağıdaki içerik ile hazırlanmalı:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/hothour
   SECRET_KEY=your_secret_key_here
   ```
4. **Dependencies** kurulu olmalı:
   ```bash
   pip install -r requirements.txt
   ```

### Kurulum

```bash
# Hangi scriptleri çalıştırmak istiyorsanız
python scripts/create_admin.py
python scripts/list_admins.py
python scripts/delete_admin.py
python scripts/delete_user.py
```

---

## 📞 Destek

Ek bilgi veya sorun için proje README.md dosyasını kontrol edin.
