<script setup>
import { ref, computed } from 'vue' // Removed onMounted/onUnmounted as we just display countdown
import { useNow } from '@vueuse/core'

const props = defineProps({
  targetTime: {
    type: String, // ISO string
    default: null
  }
})

const now = useNow()

const timeLeft = computed(() => {
  if (!props.targetTime) return '00:00'
  
  const end = new Date(props.targetTime).getTime()
  const current = now.value.getTime()
  const diff = end - current

  if (diff <= 0) return '00:00'

  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)

  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})
</script>

<template>
  <div class="countdown-timer font-mono text-hot-orange font-bold">
    <span class="mr-2 text-gray-400 text-sm uppercase tracking-widest">Next Drop</span>
    <span class="text-xl">{{ timeLeft }}</span>
  </div>
</template>
