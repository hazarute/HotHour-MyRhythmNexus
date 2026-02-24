<script setup>
import { computed } from 'vue'

const props = defineProps({
  price: {
    type: [Number, String],
    required: true
  },
  currency: {
    type: String,
    default: '₺'
  },
  large: {
    type: Boolean,
    default: false
  }
})

const formattedPrice = computed(() => {
  const val = Number(props.price)
  return isNaN(val) ? '0.00' : val.toFixed(2)
})
</script>

<template>
  <div 
    class="price-ticker font-mono font-bold tracking-tighter text-white"
    :class="large ? 'text-6xl md:text-8xl' : 'text-2xl'"
  >
    <span class="text-neon-blue mr-1">{{ currency }}</span>
    <span class="tabular-nums">{{ formattedPrice }}</span>
  </div>
</template>

<style scoped>
.price-ticker {
  text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
}
</style>
