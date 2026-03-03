<script setup>
import { ref } from 'vue'
import BrandLogo from '@/components/BrandLogo.vue'

const openIndex = ref(0)

const faqs = [
  {
    question: "Hot Hour Nedir ve Nasıl Çalışır?",
    answer: "Hot Hour, stüdyomuzdaki boş kalan pilates seanslarını dinamik fiyatlandırma (Hollanda Açık Artırması) ile sunduğumuz bir platformdur. Seansın başlamasına saatler kala fiyat en üst seviyeden başlar ve zaman geçtikçe düşer. Fiyat sizin için uygun olduğunda 'Hemen Kap' butonuna basarak seansı o anki indirimli fiyattan rezerve edersiniz."
  },
  {
    question: "Fiyatlar ne kadar düşebilir?",
    answer: "Her seansın bir taban (minimum) fiyatı vardır. Fiyat, seans saatine yaklaşıldıkça bu taban fiyata kadar kademeli olarak düşer. Son dakikalara girildiğinde 'Turbo Mod' devreye girer ve düşüş hızlanır."
  },
  {
    question: "Rezerve ettiğim seansın ödemesini nasıl yapacağım?",
    answer: "Şu an için sistemimizde 'Rezerve Et, Stüdyoda Öde' modeli geçerlidir. Platform üzerinden yakaladığınız indirimli fiyat adınıza kilitlenir. Ödemeyi stüdyoya geldiğinizde resepsiyonda yapabilirsiniz."
  },
  {
    question: "Aldığım bir seansı iptal edebilir miyim?",
    answer: "Evet, ancak fırsat seansları son dakika sunulduğu için iptallerin seans başlangıcından en geç 2 saat önce yapılması gerekmektedir. İptal işlemlerini 'Biletlerim' sayfası üzerinden gerçekleştirebilirsiniz."
  },
  {
    question: "Hot Hour seanslarına sadece üyeler mi katılabilir?",
    answer: "Hayır! Hot Hour platformuna kayıt olan herkes bu fırsatlardan yararlanabilir. İster aktif bir MyRhythmNexus üyesi olun, ister stüdyomuzu ilk defa denemek isteyen biri; indirimleri yakalamak herkesin hakkıdır."
  }
]

const toggleFaq = (index) => {
  openIndex.value = openIndex.value === index ? null : index
}
</script>

<template>
  <div class="w-full min-h-screen bg-[#050505] pt-24 px-4 pb-16 font-sans text-slate-200">
    <div class="max-w-3xl mx-auto relative z-10">
      
      <div class="flex flex-col items-center text-center mb-12">
        <div class="w-16 h-16 mb-4 bg-black/40 border border-white/10 rounded-2xl flex items-center justify-center backdrop-blur-xl shadow-[0_0_30px_rgba(0,191,255,0.2)]">
          <span class="material-symbols-outlined text-neon-blue text-3xl">help_center</span>
        </div>
        <h1 class="text-3xl md:text-5xl font-black text-white tracking-tight mb-2">Sıkça Sorulan Sorular</h1>
        <p class="text-neon-blue text-xs uppercase tracking-widest font-bold">Aklınıza Takılan Her Şey</p>
      </div>

      <div class="space-y-4">
        <div 
          v-for="(faq, index) in faqs" 
          :key="index"
          class="bg-[#0a0f1a]/80 backdrop-blur-xl border rounded-2xl overflow-hidden transition-all duration-300"
          :class="openIndex === index ? 'border-neon-blue shadow-[0_0_20px_rgba(0,191,255,0.15)]' : 'border-white/5 hover:border-white/10'"
        >
          <button 
            @click="toggleFaq(index)"
            class="w-full flex items-center justify-between p-6 text-left focus:outline-none"
          >
            <span class="font-bold text-white pr-4" :class="openIndex === index ? 'text-neon-blue' : ''">
              {{ faq.question }}
            </span>
            <span 
              class="material-symbols-outlined text-slate-400 transition-transform duration-300"
              :class="openIndex === index ? 'rotate-180 text-neon-blue' : ''"
            >
              expand_more
            </span>
          </button>
          
          <div 
            class="px-6 overflow-hidden transition-all duration-300 ease-in-out"
            :class="openIndex === index ? 'max-h-96 pb-6 opacity-100' : 'max-h-0 opacity-0'"
          >
            <p class="text-slate-400 text-sm leading-relaxed border-t border-white/5 pt-4">
              {{ faq.answer }}
            </p>
          </div>
        </div>
      </div>

      <div class="mt-12 p-6 bg-neon-magenta/5 border border-neon-magenta/20 rounded-2xl text-center">
        <p class="text-sm text-slate-300 mb-2">Aradığınız cevabı bulamadınız mı?</p>
        <a href="mailto:kayraspaceinc@gmail.com" class="inline-flex items-center gap-2 text-neon-magenta font-bold hover:text-white transition-colors">
          <span class="material-symbols-outlined text-[18px]">mail</span>
          Bize Ulaşın
        </a>
      </div>

    </div>
  </div>
</template>