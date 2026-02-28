<script setup>
import { computed, onBeforeUnmount, watch, ref } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  price: {
    type: Number,
    default: 0
  },
  discountPercent: {
    type: Number,
    default: 0
  },
  targetTime: {
    type: [String, Number, Date],
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const nowMs = ref(Date.now())
let timerId = null

const startTicking = () => {
  if (timerId) return
  timerId = setInterval(() => {
    nowMs.value = Date.now()
  }, 1000)
}

const stopTicking = () => {
  if (!timerId) return
  clearInterval(timerId)
  timerId = null
}

watch(() => props.visible, (isVisible) => {
  if (isVisible) {
    nowMs.value = Date.now()
    startTicking()
  } else {
    stopTicking()
  }
})

onBeforeUnmount(() => {
  stopTicking()
})

const countdown = computed(() => {
  if (!props.targetTime) return { hours: '00', mins: '00', secs: '00', totalMins: 0 }

  const end = new Date(props.targetTime).getTime()
  if (Number.isNaN(end)) return { hours: '00', mins: '00', secs: '00', totalMins: 0 }

  const diff = Math.max(0, end - nowMs.value)
  const totalSeconds = Math.floor(diff / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const mins = Math.floor((totalSeconds % 3600) / 60)
  const secs = totalSeconds % 60

  return {
    hours: String(hours).padStart(2, '0'),
    mins: String(mins).padStart(2, '0'),
    secs: String(secs).padStart(2, '0'),
    totalMins: Math.floor(diff / 60000)
  }
})

const shouldShowUrgencyMessage = computed(() => countdown.value.totalMins <= 30)

const formatPrice = (val) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 0
  }).format(Number(val || 0))
}
</script>

<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
    <div class="w-full max-w-md rounded-2xl border border-white/15 bg-[#111827] shadow-2xl overflow-hidden">
      <div class="px-6 pt-6 pb-5 bg-gradient-to-r from-primary/20 to-neon-blue/10 border-b border-white/10">
        <p class="text-xs uppercase tracking-[0.18em] text-neon-blue/90 font-bold">Son Adım</p>
        <h3 class="text-2xl font-black text-white mt-1">Bu Fırsatı Yakalamaya Hazır mısın?</h3>
        <p class="text-slate-300 text-sm mt-2">Seçtiğin oturum bu fiyatla sadece başarılı rezervasyon anında kilitlenir.</p>
      </div>

      <div class="p-6 space-y-4">
        <div class="rounded-xl border border-white/10 bg-white/5 p-4">
          <p class="text-slate-400 text-xs uppercase tracking-wider">Kilitlenecek Tutar</p>
          <p class="text-3xl font-black text-white mt-1">{{ formatPrice(price) }}</p>
          <p class="text-xs text-green-400 mt-2">Başlangıç fiyata göre %{{ discountPercent }} avantajdasın.</p>
        </div>

        <div class="rounded-xl border border-white/10 bg-white/5 p-3 flex items-center justify-between">
          <span class="text-slate-300 text-sm">Kalan Süre</span>
          <span class="text-neon-blue font-mono font-bold">{{ countdown.hours }}:{{ countdown.mins }}:{{ countdown.secs }}</span>
        </div>

        <p v-if="shouldShowUrgencyMessage" class="text-amber-300 text-xs font-medium">
          Bu oturum kapanmaya çok yakın. Hızlı davranmanız önerilir.
        </p>

        <div class="flex items-center gap-3 pt-2">
          <button
            :disabled="loading"
            @click="emit('cancel')"
            class="flex-1 py-3 rounded-xl border border-white/20 text-slate-300 font-semibold hover:bg-white/5 transition-colors disabled:opacity-50"
          >
            Vazgeç
          </button>
          <button
            :disabled="loading"
            @click="emit('confirm')"
            class="flex-1 py-3 rounded-xl font-bold text-white bg-gradient-to-r from-primary via-blue-600 to-neon-blue hover:shadow-neon-blue transition-all disabled:opacity-50"
          >
            Hemen Kapat
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
