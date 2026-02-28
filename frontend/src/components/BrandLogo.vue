<script setup>
/**
 * HotHour Marka Logosu
 * Kaynak: src/assets/logo.png
 */
import { defineProps } from 'vue'

// Vite'de @ alias'ı src klasörüne işaret eder.
// Görselin src/assets/logo.png konumunda olması gerekmektedir.
const props = defineProps({
  className: {
    type: String,
    default: 'w-12 h-12' // Varsayılan boyut artırıldı (48px)
  }
})
</script>

<template>
  <img 
    src="@/assets/logo.png" 
    alt="HotHour Logo" 
    :class="[className, 'object-contain max-h-full drop-shadow-[0_0_8px_rgba(0,191,255,0.4)]']"
  />
</template>