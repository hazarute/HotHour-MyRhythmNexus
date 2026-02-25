<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const expandedStep = ref(null)

const steps = [
  {
    id: 1,
    title: 'Oturum Seç',
    icon: 'calendar_month',
    description: 'Canlı Oturumlar sayfasından ilgin çeken Pilates oturumunu seç.',
    details: 'Tüm etkinlikler, güne, saate ve zorluk seviyesine göre filtrelenmiştir. İstediğin stüdyoyu ve antrenörü bulman kolay.'
  },
  {
    id: 2,
    title: 'Fiyat Düştüğünde Kap',
    icon: 'trending_down',
    description: 'Dinamik fiyatlandırma ile saat ilerledikçe fiyat düşer.',
    details: 'Oturum başlanana 24 saat kala sabit bir fiyatla başlar. Sonra her saatin başında %10 indirim uygulanır. En düşük fiyat ile hemen kap!'
  },
  {
    id: 3,
    title: 'Rezervasyon Yap',
    icon: 'check_circle',
    description: 'Seçilen fiyattan hemen kap ve yer rezerv et.',
    details: 'Ödeme güvenli ve anlık işlenir. Rezervasyonun tamamlandığında SMS ve e-posta onay alırsın. İstediğin zaman iptal edebilirsin.'
  },
  {
    id: 4,
    title: 'Oturumda Hazır Ol',
    icon: 'fitness_center',
    description: 'Belirlenen saatte stüdyoya git ve antrenörlüğünü yap.',
    details: 'Giriş yaparken QR kodunu göster. Oturum bittiğinde Pilates maceraya devam et ya da sonrakini planla!'
  }
]

const faqs = [
  {
    question: 'Fiyat ne kadar düşebilir?',
    answer: 'Oturumun başlanana 24 saat kala seçilen fiyatla başlar. Her saatin başında %10 indirim uygulanır. Örneğin; 100₺ olan bir oturum 24 saat sonra 67,66₺ olur.'
  },
  {
    question: 'Rezervasyonu iptal edebilir miyim?',
    answer: 'Oturum başlayana 4 saat kadar kalana kadar rezervasyonunu iptal edebilirsin. İptal ederken başka birine yardımcı olursun ve o da indirimli fiyattan yararlanabilir.'
  },
  {
    question: 'Ödeme güvenli mi?',
    answer: 'Evet! Tüm ödemeler PCI-DSS sertifikalı güvenli ağ geçidi üzerinden yapılır. Kredi kartı bilgilerin hiçbir zaman sunucularımızda depolanmaz.'
  },
  {
    question: 'Başka bir kişinin yerine rezervasyon yapabilir miyim?',
    answer: 'Evet! Rezervasyon yaptıktan sonra başka bir kişiyi katılımcı olarak ekleyebilirsin. O kişi oturum gün geldiğinde QR koduyla giriş yapacak.'
  },
  {
    question: 'Stüdyo hangisi? Kaç kişilik oturum?',
    answer: 'Her oturum detay sayfasında stüdyonun adı, konumu, mesafeniz ve maksimum katılımcı sayısı gösterilir. Oturum başlamaya 2 saat kalana katılımcı sayısı sabitlenir.'
  }
]

const toggleStep = (stepId) => {
  expandedStep.value = expandedStep.value === stepId ? null : stepId
}

const toggleFaq = (index) => {
  expandedStep.value = expandedStep.value === `faq-${index}` ? null : `faq-${index}`
}
</script>

<template>
  <div class="w-full">
    <!-- Hero Section -->
    <section class="w-full relative px-6 md:px-12 py-12 md:py-16 overflow-hidden">
      <div class="absolute inset-0 z-0 opacity-20 bg-gradient-to-br from-neon-blue via-background-dark to-neon-magenta"></div>
      <div class="absolute inset-0 z-0 bg-gradient-to-t from-background-dark via-background-dark/90 to-transparent"></div>
      
      <div class="relative z-10 max-w-5xl mx-auto text-center">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neon-blue mb-6 md:mb-8">
          <span class="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
          Başlangıç Rehberi
        </div>
        
        <h1 class="text-4xl sm:text-5xl md:text-6xl font-black text-white leading-tight tracking-tight mb-4 md:mb-6">
          Dinamik Fiyatlandırma <br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-neon-orange text-glow">Nasıl Çalışır?</span>
        </h1>
        
        <p class="text-base md:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed mb-8 md:mb-10">
          HotHour'da her saat önemlidir. Belirli bir oturuma ne kadar geç kaldırsan, fiyat o kadar düşer. Tüm süreci anlamak için aşağıdaki adımları izle.
        </p>

        <button 
          @click="router.push({ name: 'all-auctions' })"
          class="mx-auto block bg-primary hover:bg-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-neon-blue transition-all active:scale-95 inline-flex items-center gap-2"
        >
          <span class="material-symbols-outlined">gavel</span>
          Şimdi Oturum Bul
        </button>
      </div>
    </section>

    <!-- Steps Section -->
    <section class="hh-section max-w-4xl py-8 md:py-12">
      <div class="mb-8 md:mb-12 text-center">
        <h2 class="text-2xl md:text-3xl font-bold text-white mb-3">4 Adımta Başlangıç</h2>
        <p class="text-slate-400 text-sm md:text-base">Basit, hızlı ve güvenli bir satın alma deneyimi</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <div
          v-for="step in steps"
          :key="step.id"
          @click="toggleStep(step.id)"
          class="hh-card cursor-pointer group transition-all duration-300 hover:border-primary/50"
          :class="expandedStep === step.id ? 'border-primary/80 bg-white/5' : ''"
        >
          <!-- Step Header -->
          <div class="flex items-start gap-4 md:gap-5">
            <div class="flex-shrink-0 w-12 h-12 md:w-14 md:h-14 rounded-lg bg-gradient-to-br from-neon-blue/30 to-primary/30 flex items-center justify-center border border-primary/40 group-hover:border-primary/60 transition-colors">
              <span class="material-symbols-outlined text-neon-blue text-lg md:text-2xl">{{ step.icon }}</span>
            </div>
            
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2 mb-1">
                <h3 class="text-base md:text-lg font-bold text-white">{{ step.title }}</h3>
                <span class="material-symbols-outlined text-slate-500 group-hover:text-neon-blue transition-colors transform" :class="expandedStep === step.id ? 'rotate-180' : ''">expand_more</span>
              </div>
              <p class="text-sm text-slate-400">{{ step.description }}</p>
            </div>
          </div>

          <!-- Step Details (Expandable) -->
          <div
            v-if="expandedStep === step.id"
            class="mt-5 pt-5 border-t border-white/10 animate-in fade-in duration-300"
          >
            <p class="text-sm md:text-base text-slate-300 leading-relaxed">{{ step.details }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How Pricing Works Section -->
    <section class="hh-section max-w-4xl py-8 md:py-12 border-t border-slate-800">
      <div class="mb-8 md:mb-12">
        <h2 class="text-2xl md:text-3xl font-bold text-white mb-2">Fiyatlandırma Örneği</h2>
        <p class="text-slate-400 text-sm md:text-base">100₺ tarifeli bir oturumun fiyatı saatlere göre nasıl değişir</p>
      </div>

      <!-- Timeline Chart -->
      <div class="hh-card p-6 md:p-8">
        <div class="space-y-4">
          <!-- Hour 24 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">24 saat önce</p>
            </div>
            <div class="flex-1">
              <div class="relative h-10 md:h-12 bg-gradient-to-r from-neon-orange to-orange-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 group hover:shadow-neon-orange/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">100₺</span>
              </div>
            </div>
          </div>

          <!-- Hour 12 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">12 saat kalana</p>
            </div>
            <div class="flex-1">
              <div class="relative w-2/3 h-10 md:h-12 bg-gradient-to-r from-neon-magenta to-pink-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 hover:shadow-neon-magenta/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">81,00₺</span>
              </div>
            </div>
          </div>

          <!-- Hour 6 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">6 saat kalana</p>
            </div>
            <div class="flex-1">
              <div class="relative w-1/2 h-10 md:h-12 bg-gradient-to-r from-neon-blue to-blue-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 hover:shadow-neon-blue/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">65,61₺</span>
              </div>
            </div>
          </div>

          <!-- Hour 0 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">Hemen kap!</p>
            </div>
            <div class="flex-1">
              <div class="relative w-1/3 h-10 md:h-12 bg-gradient-to-r from-neon-green to-green-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 hover:shadow-neon-green/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">53.10₺</span>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 md:mt-8 p-4 bg-white/5 border border-white/10 rounded-lg">
          <p class="text-xs md:text-sm text-slate-300 flex items-start gap-2">
            <span class="material-symbols-outlined text-neon-blue flex-shrink-0 mt-1">info</span>
            <span>Her saatin başında %10 otomatik indirim uygulanır. Oturum başlanana 4 saat kalana kadar kap yapabilirsin.</span>
          </p>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="hh-section max-w-4xl py-8 md:py-12 border-t border-slate-800">
      <div class="mb-8 md:mb-12">
        <h2 class="text-2xl md:text-3xl font-bold text-white mb-2">Sık Sorulan Sorular</h2>
        <p class="text-slate-400 text-sm md:text-base">Daha fazla bilgi edinmek için tıkla</p>
      </div>

      <div class="space-y-3 md:space-y-4">
        <div
          v-for="(faq, index) in faqs"
          :key="index"
          @click="toggleFaq(index)"
          class="hh-card cursor-pointer group transition-all duration-300 hover:border-neon-blue/50"
          :class="expandedStep === `faq-${index}` ? 'border-neon-blue/80 bg-white/5' : ''"
        >
          <div class="flex items-center justify-between gap-3 md:gap-4">
            <h3 class="text-sm md:text-base font-semibold text-white flex-1">{{ faq.question }}</h3>
            <span class="material-symbols-outlined text-slate-500 group-hover:text-neon-blue transition-colors flex-shrink-0 transform" :class="expandedStep === `faq-${index}` ? 'rotate-180' : ''">expand_more</span>
          </div>

          <p
            v-if="expandedStep === `faq-${index}`"
            class="text-sm md:text-base text-slate-300 mt-4 pt-4 border-t border-white/10 leading-relaxed animate-in fade-in duration-300"
          >
            {{ faq.answer }}
          </p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="hh-section max-w-4xl py-8 md:py-12 border-t border-slate-800">
      <div class="hh-card p-6 md:p-10 text-center bg-gradient-to-br from-neon-blue/10 to-neon-magenta/10 border-neon-blue/30">
        <h3 class="text-2xl md:text-3xl font-bold text-white mb-3">Başlamaya Hazır Mısın?</h3>
        <p class="text-slate-300 mb-6 md:mb-8 text-sm md:text-base max-w-xl mx-auto">
          Şimdi canlı oturumları keşfet ve en iyi fiyatı yakala. Az daha, yanmaya hazır ol!
        </p>
        <button
          @click="router.push({ name: 'all-auctions' })"
          class="bg-primary hover:bg-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-neon-blue transition-all active:scale-95 inline-flex items-center gap-2 text-sm md:text-base"
        >
          <span class="material-symbols-outlined">gavel</span>
          Hemen Başla
        </button>
      </div>
    </section>

    <!-- Back to Home Link -->
    <section class="hh-section max-w-4xl py-6 md:py-8 text-center border-t border-slate-800">
      <button 
        @click="router.push('/')"
        class="inline-flex items-center gap-2 text-slate-400 hover:text-neon-blue transition-colors text-xs md:text-sm"
      >
        <span class="material-symbols-outlined">arrow_back</span>
        Ana Sayfaya Dön
      </button>
    </section>
  </div>
</template>

<style scoped>
/* Additional styling can be added here if needed */
</style>
