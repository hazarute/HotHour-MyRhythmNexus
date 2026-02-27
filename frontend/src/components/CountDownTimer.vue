<script setup>
import { computed } from 'vue' 
import { useNow } from '@vueuse/core'

const props = defineProps({
  targetTime: {
    type: String, // ISO string
    default: null
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  small: {
    type: Boolean,
    default: false
  }
})

const now = useNow()

const timeLeft = computed(() => {
  if (!props.targetTime) return '00:00:00'
  
  const end = new Date(props.targetTime).getTime()
  const current = now.value.getTime()
  const diff = end - current

  if (diff <= 0) return '00:00:00'

  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)

  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})
</script>

<template>
  <div class="countdown-timer font-mono text-hot-orange font-bold" :class="small ? 'text-sm' : ''">
    <span v-if="showLabel" class="mr-2 text-gray-400 text-sm uppercase tracking-widest">Next Drop</span>
    <span :class="small ? '' : 'text-xl'">{{ timeLeft }}</span>
  </div>
</template>
