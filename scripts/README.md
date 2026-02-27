# Admin Script Belgeleri

## 📜 Scripts İçeriği

1. **create_admin.py** - Admin hesabı oluşturma
2. **list_admins.py** - Admin hesaplarını listeleme
3. **delete_admin.py** - Admin hesabı silme
4. **delete_user.py** - Herhangi bir kullanıcı hesabı silme

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
