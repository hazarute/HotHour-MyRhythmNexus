# Aktif Bağlam (Active Context)

## Şu Anki Odak
**Faz R4: Canlıya Geçiş Hazırlığı ve Manuel Testler** 🚀

Tüm teknik geliştirme fazları tamamlandı. Email doğrulama sistemi başarıyla entegre edildi ve birim testleri (pytest) geçti. Şimdi sistemin bir bütün olarak beklenen davranışı sergilediğini doğrulamak için **manuel testler** yapacağız.

## 🔍 Test ve Revizyon Planı

Uygulamayı çalıştırıp aşağıdaki senaryoları tarayıcı üzerinden doğrulayacağız:

### Öncelikli Modüller
1.  **Kimlik Doğrulama (Auth):**
    - [ ] Kayıt ol (Email gönderiliyor mu?)
    - [ ] Email linkine tıkla (VerifyEmailView çalışıyor mu?)
    - [ ] Giriş yap (Doğrulanmış kullanıcı)
    - [ ] Token saklama ve çıkış yapma.

2.  **Açık Artırmalar (Auctions):**
    - [ ] Ana sayfa listesi (Socket güncellemeleri)
    - [ ] Detay sayfası (Sayaç, Teklif verme)
    - [ ] Açık artırma süresi dolunca ne oluyor?

3.  **Rezervasyonlar (Reservations):**
    - [ ] Hemen Al (Buy Now) butonu çalışıyor mu?
    - [ ] "My Reservations" ekranında rezervasyon görünüyor mu?
    - [ ] Erişim kodu doğru üretildi mi?

4.  **Admin Paneli:**
    - [ ] Yeni açık artırma oluşturma.
    - [ ] Rezervasyon listesi kontrolü.

## ✅ Tamamlanan Son İşler (Faz R4.1)
- **Email Doğrulama Sistemi:**
    - Backend: `POST /api/v1/auth/register` (Email gönderimi entegre)
    - Backend: `GET /api/v1/auth/verify-email` (Token doğrulama)
    - Frontend: `VerifyEmailView.vue` (Durum bildilendirme ekranı)
    - Test: `tests/test_email_verification.py` (Kapsamlı testler BAŞARILI)
    - Fix: Prisma `camelCase` vs Pydantic `snake_case` uyumsuzlukları giderildi.

## 📝 Sıradaki Adımlar
1.  Backend sunucusunu başlat: `uvicorn app.main:app --reload`
2.  Frontend sunucusunu başlat: `npm run dev`
3.  Tarayıcıda `http://localhost:5173` adresine git.
4.  Kayıt ol akışını test et.