<template>
  <div class="min-h-screen bg-background-dark text-white px-4 sm:px-6 lg:px-8 py-24">
    <div class="max-w-4xl mx-auto">
      <div class="mb-8">
        <p class="text-xs uppercase tracking-[0.2em] text-neon-blue/80">Yasal Metin</p>
        <h1 class="mt-2 text-3xl sm:text-4xl font-black tracking-tight">Kullanım Şartları</h1>
        <p class="mt-3 text-slate-400 text-sm">Son güncelleme: 28 Şubat 2026</p>
      </div>

      <div class="space-y-6">
        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">1) Hizmetin Kapsamı</h2>
          <p class="mt-2 text-sm text-slate-300 leading-7">
            HotHour, stüdyoların uygunluk verdiği seanslar için dinamik fiyat düşüş modeliyle rezervasyon imkânı sunar.
            Platform, seansın çevrim içi rezerve edilmesini sağlar; nihai hizmet stüdyo tarafından yerinde sunulur.
          </p>
        </section>

        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">2) Fiyatlandırma ve Rezervasyon</h2>
          <ul class="mt-2 text-sm text-slate-300 leading-7 list-disc pl-5 space-y-1">
            <li>Seans fiyatları, açık artırma süresi boyunca sistem tarafından düşürülebilir.</li>
            <li>“Hemen Kap” işlemi sırasında görünen fiyat, başarılı rezervasyon anında kilitlenir.</li>
            <li>Aynı seans için ilk başarılı rezervasyon geçerlidir; sonradan gelen denemeler reddedilebilir.</li>
            <li>Sistem kaynaklı gecikmelerde güncel durum, uygulamadaki son doğrulanmış kayıt üzerinden değerlendirilir.</li>
          </ul>
        </section>

        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">3) Ödeme ve Katılım</h2>
          <ul class="mt-2 text-sm text-slate-300 leading-7 list-disc pl-5 space-y-1">
            <li>HotHour modeli “Rezervasyon Yap & Yerinde Öde” prensibiyle çalışır.</li>
            <li>Platform üzerinden yapılan rezervasyon, stüdyoda ödeme yükümlülüğünü ortadan kaldırmaz.</li>
            <li>Kullanıcı, rezervasyon kodunu stüdyoya ibraz etmekle sorumludur.</li>
          </ul>
        </section>

        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">4) Kullanıcı Yükümlülükleri</h2>
          <ul class="mt-2 text-sm text-slate-300 leading-7 list-disc pl-5 space-y-1">
            <li>Hesap bilgileri doğru, güncel ve kullanıcıya ait olmalıdır.</li>
            <li>Hesap güvenliği (şifre ve erişim bilgileri) kullanıcı sorumluluğundadır.</li>
            <li>Kötüye kullanım, otomasyonla haksız avantaj sağlama veya sistemi yanıltma girişimleri yasaktır.</li>
          </ul>
        </section>

        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">5) İptal, Değişiklik ve Erişim</h2>
          <ul class="mt-2 text-sm text-slate-300 leading-7 list-disc pl-5 space-y-1">
            <li>Seans durumu stüdyo veya sistem tarafından güncellenebilir (ör. iptal, süre dolumu, satış kapanışı).</li>
            <li>Teknik bakım, güvenlik veya operasyonel nedenlerle hizmette geçici kesinti yaşanabilir.</li>
            <li>Gerekli hallerde belirli hesaplara erişim kısıtı uygulanabilir.</li>
          </ul>
        </section>

        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">6) Sorumluluk Sınırları</h2>
          <p class="mt-2 text-sm text-slate-300 leading-7">
            HotHour, platformun makul sürekliliği için gerekli teknik önlemleri alır. Ancak internet erişimi,
            üçüncü taraf servisler, cihaz uyumluluğu veya stüdyo kaynaklı sebeplerden doğan aksaklıklardan sınırsız
            sorumluluk üstlenmez. Kullanıcı, hizmeti mevcut haliyle kullandığını kabul eder.
          </p>
        </section>

        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">7) Gizlilik ve Veriler</h2>
          <p class="mt-2 text-sm text-slate-300 leading-7">
            Hesap, rezervasyon ve doğrulama süreçlerinde gerekli kişisel veriler işlenebilir. Bu işlemler,
            platformun hizmet sunumu ve güvenliği amacıyla sınırlı şekilde gerçekleştirilir.
          </p>
        </section>

        <section class="hh-glass-card rounded-2xl border border-white/10 p-5 sm:p-6">
          <h2 class="text-lg font-bold text-white">8) Şartların Güncellenmesi</h2>
          <p class="mt-2 text-sm text-slate-300 leading-7">
            Bu metin, ürün özellikleri veya yasal gereklilikler doğrultusunda güncellenebilir. Güncel sürüm,
            uygulama içindeki Kullanım Şartları sayfasında yayınlandığı anda yürürlüğe girer.
          </p>
        </section>
      </div>

      <div class="mt-8">
        <router-link
          to="/"
          class="inline-flex items-center gap-2 rounded-xl border border-neon-blue/40 text-neon-blue px-4 py-2 text-sm hover:bg-neon-blue/10 transition-colors"
        >
          <span class="material-symbols-outlined text-base">arrow_back</span>
          Ana Sayfaya Dön
        </router-link>
      </div>
    </div>
  </div>
</template>
