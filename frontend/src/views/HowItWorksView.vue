<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'

useHead({
  title: 'Nasıl Çalışır? — HotHour',
  meta: [
    { name: 'description', content: 'HotHour\'da nasıl indirimli seans yakalarsın? Hollanda Açık Artırması mantığını öğren, adım adım rehberimizi keşfet.' },
    { property: 'og:title', content: 'Nasıl Çalışır? — HotHour' },
    { property: 'og:description', content: 'Hollanda Açık Artırması ile indirimli seans yakala. Adım adım rehber.' },
    { property: 'og:url', content: 'https://hothour.kayraspace.com/how-it-works' },
  ],
  link: [{ rel: 'canonical', href: 'https://hothour.kayraspace.com/how-it-works' }],
})

const router = useRouter()
const expandedStep = ref(null)

const steps = [
  {
    id: 1,
    title: 'Boş Seansları Keşfet',
    icon: 'search',
    description: 'Stüdyoların hafta içi premium seanslarındaki boşlukları yakala.',
    details: 'Reformer, Cadillac veya kişiye özel Pilates antrenmanları... Filtrele, sana en uygun stüdyoyu ve saati seç. Unutma, bu seanslar normalde çok daha yüksek fiyatlı!'
  },
  {
    id: 2,
    title: 'Fiyatın Düşüşünü İzle',
    icon: 'trending_down',
    description: 'Hollanda Açık Artırması mantığıyla zaman geçtikçe fiyat düşer.',
    details: 'Seans saati yaklaştıkça fiyat tavan fiyattan taban fiyata doğru erimeye başlar. Seansa 2 saat kala 🔥 Turbo Mod devreye girer ve fiyatlar çılgın gibi düşer! Beklemek risklidir, başkası senden önce kapabilir.'
  },
  {
    id: 3,
    title: 'Hemen Kap (Kilitle)',
    icon: 'touch_app',
    description: 'Fiyat bütçene uygun olduğunda "Hemen Kap" butonuna bas.',
    details: 'Sistem saniyenin binde biri hızında çalışır. Butona ilk basan kişi o anki güncel fiyatı dondurur (kilitler) ve seansı kapatır. Tebrikler, piyasa değerinin çok altında bir seans yakaladın!'
  },
  {
    id: 4,
    title: 'Stüdyoda Öde',
    icon: 'storefront',
    description: 'Kredi kartı girmek yok! Sana verilen kod ile stüdyoya git.',
    details: 'Rezervasyon onaylandığında ekranda eşsiz bir kod (Örn: HOT-8X2A) göreceksin. Sadece stüdyoya git, resepsiyona kodunu söyle ve o an kilitlediğin indirimli fiyat üzerinden ödemeni nakit veya kartla yerinde yap.'
  }
]

const faqs = [
  {
    question: 'Fiyat ne kadar düşebilir? Sıfıra iner mi?',
    answer: 'Hayır, her seansın stüdyo tarafından belirlenmiş bir "Taban Fiyatı" (Floor Price) vardır. Fiyat bu rakamın altına asla düşmez. Taban fiyata ulaşmadan önce seansı kapmak tamamen senin hızına ve stratejine bağlı!'
  },
  {
    question: 'Ödeme için kredi kartı girmem gerekiyor mu?',
    answer: 'Kesinlikle hayır! HotHour güven üzerine kuruludur. Kredi kartı bilgini istemeyiz. Seansı uygulamadan rezerve edersin, ödemeyi ise stüdyoya gittiğinde fiziksel olarak yaparsın (Yerinde Ödeme).'
  },
  {
    question: 'Turbo Mod (🔥 Sıcak Saat) nedir?',
    answer: 'Seansın başlamasına çok az bir zaman (genellikle son 2 saat) kala devreye giren özel bir moddur. Bu modda fiyatlar normalden çok daha hızlı ve agresif bir şekilde düşmeye başlar. Ekranın kırmızıya döndüğünü gördüğünde elini çabuk tutmalısın!'
  },
  {
    question: 'Aynı seansa başka biriyle aynı anda basarsak ne olur?',
    answer: 'HotHour altyapısı "Yarış Durumu"na (Race Condition) karşı özel olarak korunmaktadır. "Hemen Kap" butonuna salise farkıyla bile olsa ilk basan kişi fiyatı kilitler ve seansı alır. Diğer kullanıcı "Seans başkası tarafından kapıldı" uyarısı görür.'
  },
  {
    question: 'Rezervasyonumu iptal edebilir miyim?',
    answer: 'Uygulama üzerinden seansa belirli bir süre kalana kadar iptal edebilirsin. Lütfen stüdyoların emeğine saygı göstererek gidemeyeceğin seansları erkenden iptal et ki o boşluktan başkası faydalanabilsin.'
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
          Fırsatı Yakala: <br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-neon-orange text-glow">HotHour Nasıl Çalışır?</span>
        </h1>
        
        <p class="text-base md:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed mb-8 md:mb-10">
          HotHour'da zaman paradır! Seçtiğin pilates seansının saati yaklaştıkça fiyatı sürekli düşer. Yeterince beklersen harika bir indirim yakalarsın, çok beklersen başkası kapar. İşte oyunun kuralları:
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
        <h2 class="text-2xl md:text-3xl font-bold text-white mb-3">4 Adımda Başlangıç</h2>
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
        <p class="text-slate-400 text-sm md:text-base">6000₺ değerindeki bir Reformer Pilates seansının fiyat yolculuğu:</p>
      </div>

      <!-- Timeline Chart -->
      <div class="hh-card p-6 md:p-8">
        <div class="space-y-4">
          <!-- Hour 24 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">Başlangıç Fiyatı</p>
            </div>
            <div class="flex-1">
              <div class="relative h-10 md:h-12 bg-gradient-to-r from-neon-orange to-orange-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 group hover:shadow-neon-orange/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">6000₺</span>
              </div>
            </div>
          </div>

          <!-- Hour 12 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">Standart Düşüş</p>
            </div>
            <div class="flex-1">
              <div class="relative w-2/3 h-10 md:h-12 bg-gradient-to-r from-neon-magenta to-pink-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 hover:shadow-neon-magenta/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">4800₺</span>
              </div>
            </div>
          </div>

          <!-- Hour 6 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">🔥 Turbo Mod Aktif</p>
            </div>
            <div class="flex-1">
              <div class="relative w-1/2 h-10 md:h-12 bg-gradient-to-r from-neon-blue to-blue-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 hover:shadow-neon-blue/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">3000₺</span>
              </div>
            </div>
          </div>

          <!-- Hour 0 -->
          <div class="flex items-center gap-4">
            <div class="w-24 md:w-32 flex-shrink-0">
              <p class="text-xs md:text-sm font-medium text-slate-400">Hemen Kapıldı!</p>
            </div>
            <div class="flex-1">
              <div class="relative w-1/3 h-10 md:h-12 bg-gradient-to-r from-neon-green to-green-600 rounded-lg flex items-center justify-end pr-4 md:pr-6 hover:shadow-neon-green/20 hover:shadow-lg transition-shadow">
                <span class="font-bold text-white text-sm md:text-base">2400₺</span>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 md:mt-8 p-4 bg-white/5 border border-white/10 rounded-lg">
          <p class="text-xs md:text-sm text-slate-300 flex items-start gap-2">
            <span class="material-symbols-outlined text-neon-blue flex-shrink-0 mt-1">info</span>
            <span>Stüdyolar fiyatın düşüş hızını ve Turbo modun ne zaman başlayacağını kendileri belirler. Gözün sayaçta olsun!</span>
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
