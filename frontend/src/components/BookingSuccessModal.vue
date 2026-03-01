<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  reservation: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const router = useRouter()
const copyFeedback = ref(false)
let autoRedirectTimer = null

const copyBookingCode = async () => {
  const code = props.reservation?.booking_code
  if (!code) return
  try {
    await navigator.clipboard.writeText(code)
  } catch {
    const el = document.createElement('textarea')
    el.value = code
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
  }
  copyFeedback.value = true
  setTimeout(() => { copyFeedback.value = false }, 2000)
}

const goToReservations = () => {
  emit('close')
  router.push('/my-reservations')
}

// Auto-redirect 5 seconds after modal becomes visible
watch(() => props.visible, (val) => {
  if (val) {
    if (autoRedirectTimer) clearTimeout(autoRedirectTimer)
    autoRedirectTimer = setTimeout(() => {
      goToReservations()
    }, 5000)
  } else {
    if (autoRedirectTimer) {
      clearTimeout(autoRedirectTimer)
      autoRedirectTimer = null
    }
  }
})

onUnmounted(() => {
  if (autoRedirectTimer) {
    clearTimeout(autoRedirectTimer)
    autoRedirectTimer = null
  }
})
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/90 backdrop-blur-md p-4">
      <div class="bg-gradient-to-b from-[#0b1220] via-[#070d18] to-[#050505] border border-neon-green/40 rounded-3xl p-8 max-w-sm w-full text-center shadow-[0_0_60px_rgba(54,211,153,0.25)] relative overflow-hidden">
        <div class="absolute -top-16 left-1/2 -translate-x-1/2 w-56 h-56 rounded-full bg-neon-green/10 blur-3xl pointer-events-none"></div>
        <div class="absolute inset-0 opacity-[0.04] pointer-events-none" style="background-image: radial-gradient(#fff 1px, transparent 1px); background-size: 14px 14px;"></div>

        <div class="relative z-10 pb-6">
          <div class="w-16 h-16 bg-neon-green/10 rounded-full flex items-center justify-center mx-auto mb-4 border border-neon-green/30 shadow-[0_0_20px_rgba(54,211,153,0.25)]">
            <span class="material-symbols-outlined text-4xl text-neon-green">emoji_events</span>
          </div>
          <h2 class="text-3xl font-black text-white uppercase tracking-wider mb-1">Seans Kilitlendi</h2>
          <p class="text-neon-green text-sm font-semibold">Harika iş! Fırsatı rakiplerinden önce kaptın.</p>
          <p class="text-slate-400 text-xs mt-2">Piyasa değerinin çok altında bir fiyata seansı garantiledin.</p>
        </div>

        <div class="relative z-10 pt-4 pb-4">
          <p class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-2">Giriş Kodunuz</p>
          <div
            @click="copyBookingCode"
            class="bg-black/60 border border-white/15 p-4 rounded-xl cursor-pointer group hover:border-neon-green/60 transition-all duration-300 relative"
            :class="copyFeedback ? 'copy-code-success border-neon-green/70 shadow-[0_0_25px_rgba(54,211,153,0.45)] scale-[1.01]' : ''"
            :title="copyFeedback ? 'Kopyalandı!' : 'Kopyalamak için tıklayın'"
          >
            <p class="text-4xl font-black font-mono text-white tracking-widest drop-shadow-[0_0_10px_rgba(255,255,255,0.5)] group-hover:text-neon-green transition-colors">
              {{ reservation?.booking_code || 'HOT-XXXX' }}
            </p>
            <span
              class="absolute top-2 right-2 bg-neon-green text-black text-[10px] font-bold px-2 py-1 rounded-md transition-all duration-200"
              :class="copyFeedback ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-1 pointer-events-none'"
            >
              Kopyalandı!
            </span>
            <span
              class="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[11px] font-bold text-neon-green whitespace-nowrap transition-all duration-200"
              :class="copyFeedback ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1 pointer-events-none'"
            >
              Kod panoya kopyalandı ✓
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-4 leading-relaxed">
            Stüdyoya gittiğinizde bu kodu resepsiyona göstererek ödemenizi tamamlayın.
          </p>
        </div>

        <div class="relative z-10 mt-2">
          <button
            @click="goToReservations"
            class="w-full py-4 rounded-xl font-black text-white bg-gradient-to-r from-amber-400 via-orange-500 to-amber-300 hover:from-amber-300 hover:via-orange-400 hover:to-yellow-300 uppercase tracking-widest transition-all shadow-[0_0_25px_rgba(251,146,60,0.4)] hover:shadow-[0_0_38px_rgba(251,146,60,0.65)]"
          >
            Biletlerime Git
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style>
.copy-code-success {
  animation: copyPulse 450ms ease-out;
}

@keyframes copyPulse {
  0% { transform: scale(1); box-shadow: 0 0 0 rgba(54, 211, 153, 0); }
  40% { transform: scale(1.02); box-shadow: 0 0 35px rgba(54, 211, 153, 0.45); }
  100% { transform: scale(1); box-shadow: 0 0 20px rgba(54, 211, 153, 0.25); }
}
</style>
