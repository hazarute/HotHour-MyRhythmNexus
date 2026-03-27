# Geliştirici Bellek Bankası İnşa Kılavuzu (Memory Blueprint)

**⚠️ DİKKAT (COPILOT İÇİN SİSTEM TALİMATI):**
Bu dosya yalnızca `BAŞLAT` komutu verildiğinde, projenin `.memory-bank/` klasörünü ve içindeki çekirdek dosyaları sıfırdan oluşturmak için okunmalıdır. Bu rehberi kullanarak 4 ana dosyayı aşağıda belirtilen şablonlara ve `README.md` içeriğine uygun şekilde oluştur. Dosyaları oluşturduktan sonra kullanıcıdan onay bekle.

---

## DOSYA 1: `foundation.md` (Mimari ve Vizyon)
**Amacı:** Projenin "Ne" olduğunu ve "Nasıl" inşa edileceğini tanımlar. 
**Nasıl Doldurulacak:** `README.md` dosyasını analiz et ve aşağıdaki yapıyı oluştur.

* **Proje Özeti:** Tek paragraflık ürün vizyonu ve temel amacı.
* **Teknoloji Yığını (Tech Stack):** Frontend, Backend, Veritabanı, Araçlar vb. (Sürüm bilgileriyle birlikte, örn: Python 3+, React 18, Node 20).
* **Sistem Mimarisi:** İstemci-sunucu iletişimi, veri akışı, yetkilendirme modeli.
* **Klasör Yapısı:** Projenin temel dizin ağacı ve hangi klasörün ne işe yaradığı.

## DOSYA 2: `codingStandards.md` (Kodlama Standartları)
**Amacı:** Proje boyunca kodun tutarlı ve temiz kalmasını sağlamak.
**Nasıl Doldurulacak:** Kullanılan teknoloji yığınına en uygun best-practice'leri belirle ve aşağıdaki başlıkları doldur.

* **İsimlendirme Kuralları:** Değişkenler (camelCase), Fonksiyonlar, Dosyalar (kebab-case vb.), Sınıflar (PascalCase).
* **Mimari Kurallar:** Bileşen (component) yapısı, state yönetimi standartları, API çağrı katmanları.
* **Hata Yönetimi (Error Handling):** Try/catch bloklarının nasıl kullanılacağı, global hata yakalama stratejisi.
* **Tip Güvenliği (varsa):** TypeScript arayüz (interface) ve tip (type) tanımlama kuralları.

## DOSYA 3: `state.md` (Aktif Durum ve İlerleme)
**Amacı:** O anki zihinsel odağı, hangi aşamada olunduğunu ve sıradaki adımları takip etmek. Sürekli güncellenir.
**Nasıl Doldurulacak:** Proje başlangıcında ilk fazları ve temel görevleri belirleyerek oluştur.

* **Mevcut Odak:** Tek cümlelik "Şu an tam olarak ne yapıyoruz?" açıklaması. (Örn: "Kullanıcı giriş ekranının UI tasarımı yapılıyor.")
* **Aktif Faz:** Projenin hangi aşamasında olunduğu (Örn: Faz 1 - Altyapı Kurulumu).
* **Görev Listesi:** Markdown checkbox formatında Fazlar'a ayrılmış çok detaylı ve açıklayıcı adımlar.
    * `[x]` Tamamlanan görev.
    * `[ ]` Sıradaki görev (Mevcut odak her zaman en üstteki ilk boş kutucuktur).

## DOSYA 4: `decisions.md` (Kararlar ve İş Kuralları)
**Amacı:** Geliştirme sürecinde alınan kritik kararları, iş mantığını ve aşılan engelleri kayıt altında tutmak.
**Nasıl Doldurulacak:** Başlangıçta boş veya `README.md`'den çıkarılan temel kurallarla oluşturulur. Zamanla `DEĞİŞİKLİKLERİ İŞLE` komutuyla genişler.

* **İş Kuralları (Business Logic):** Projeye özel değişmez kurallar (Örn: "Şifreler en az 8 karakter olmalı", "Silinen kullanıcılar veritabanından uçurulmaz, soft-delete uygulanır").
* **Mimari Kararlar (ADR):** "Neden X kütüphanesi yerine Y kullanıldı?" gibi soruların cevapları.
* **Geçici Çözümler (Workarounds):** Karşılaşılan kronik hatalar ve projenin o hataların etrafından nasıl dolandığı.

---
**BAŞLAT PROTOKOLÜ SON ADIMI:**
Yukarıdaki 4 dosyayı oluştur, öncelikle bu dosyalar taslaktır ve kullanıcının (Yönetici) incelemesi için dön ve "Bellek Bankası altyapısının taslağını oluşturdum. İnceleme ardından revize isteklerin varsa belirtmeni, eğer yoksa taslağın nihai bellek bankası dosyaları olmasını Onaylıyor musunuz?" diye sor.