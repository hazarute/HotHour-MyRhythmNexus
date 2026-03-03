<script setup>
// Yasal metin olduğu için statik içerik
const lastUpdated = "3 Mart 2026"
</script>

<template>
  <div class="w-full min-h-screen bg-[#050505] pt-24 px-4 pb-16 font-sans text-slate-200">
    <div class="max-w-4xl mx-auto relative z-10">
      
      <div class="mb-10 border-b border-white/10 pb-8">
        <h1 class="text-3xl md:text-5xl font-black text-white tracking-tight mb-4">Gizlilik Politikası ve KVKK</h1>
        <div class="flex items-center gap-2 text-xs text-slate-500 font-bold uppercase tracking-widest">
          <span class="material-symbols-outlined text-[16px]">update</span>
          Son Güncelleme: {{ lastUpdated }}
        </div>
      </div>

      <div class="bg-[#0a0f1a]/80 backdrop-blur-xl border border-white/5 rounded-3xl p-6 md:p-10 shadow-2xl space-y-8 text-sm text-slate-400 leading-relaxed">
        
        <section>
          <h2 class="text-xl font-bold text-white mb-3">1. Veri Sorumlusu</h2>
          <p>
            KayraSpace Inc. ("Şirket", "Biz", "HotHour") olarak, kişisel verilerinizin güvenliği hususunda azami hassasiyet göstermekteyiz. Bu bilinçle, platformumuzu kullanan tüm şahıslara ait her türlü kişisel verinin 6698 sayılı Kişisel Verilerin Korunması Kanunu ("KVKK")'na uygun olarak işlenmesine ve muhafaza edilmesine büyük önem atfediyoruz.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-white mb-3">2. Toplanan Kişisel Veriler</h2>
          <p class="mb-2">Platformumuza kayıt olurken ve kullanırken aşağıdaki verileriniz toplanmaktadır:</p>
          <ul class="list-disc list-inside space-y-1 ml-2">
            <li><strong>Kimlik Verisi:</strong> Ad, soyad.</li>
            <li><strong>İletişim Verisi:</strong> E-posta adresi, telefon numarası.</li>
            <li><strong>İşlem Güvenliği Verisi:</strong> IP adresi, şifre bilgileri (kriptolu olarak), platform üzerindeki rezervasyon geçmişiniz.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-bold text-white mb-3">3. Kişisel Verilerin İşlenme Amacı</h2>
          <p>
            Toplanan kişisel verileriniz; platform üzerinden sunulan hizmetlerden (açık artırma bazlı rezervasyon) faydalanabilmeniz, sistem hatalarının giderilmesi, kullanıcı deneyiminin iyileştirilmesi, iletişim süreçlerinin yürütülmesi ve yasal yükümlülüklerimizin yerine getirilmesi amaçlarıyla işlenmektedir.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-white mb-3">4. Çerez (Cookie) Politikası</h2>
          <p>
            HotHour platformu, oturumunuzu açık tutmak (Auth Token) ve güvenlik önlemlerini sağlamak amacıyla zorunlu teknik çerezler kullanmaktadır. Reklam veya üçüncü taraf izleme çerezleri sistemimizde yer almamaktadır.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-white mb-3">5. Kullanıcı Hakları</h2>
          <p class="mb-2">KVKK Madde 11 uyarınca, veri sahibi olarak aşağıdaki haklara sahipsiniz:</p>
          <ul class="list-disc list-inside space-y-1 ml-2">
            <li>Kişisel veri işlenip işlenmediğini öğrenme,</li>
            <li>Kişisel verileriniz işlenmişse buna ilişkin bilgi talep etme,</li>
            <li>Eksik veya yanlış işlenen verilerin düzeltilmesini isteme,</li>
            <li>Kişisel verilerinizin silinmesini veya yok edilmesini talep etme.</li>
          </ul>
        </section>

        <section class="border-t border-white/5 pt-8 mt-8">
          <h2 class="text-lg font-bold text-white mb-2 flex items-center gap-2">
            <span class="material-symbols-outlined text-neon-blue">mail</span> İletişim
          </h2>
          <p>
            Kişisel verilerinizle ilgili her türlü soru ve talebiniz için bizimle iletişime geçebilirsiniz:<br>
            <strong class="text-neon-blue">E-posta:</strong> <a href="mailto:kayraspace@gmail.com" class="hover:text-white transition-colors">kayraspace@gmail.com</a>
          </p>
        </section>

      </div>
    </div>
  </div>
</template>

<style scoped>
section h2 {
  color: #fff;
}
</style>