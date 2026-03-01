<script setup>
/**
 * PageBackground — Tekrar eden neon arka plan dekorasyonu bileşeni.
 *
 * 6 farklı view'da kopyalanan:
 *   - Sol üst neon blur blobu
 *   - Sağ alt neon blur blobu
 *   - Base64 SVG dot-grid overlay
 * ...bu bileşende merkezi olarak tutulur.
 *
 * Kullanım:
 *   <PageBackground />
 *   <PageBackground color1="neon-blue" color2="#f20d80" />
 *   <PageBackground color1="rgba(255,42,42,0.2)" color2="rgba(255,123,0,0.15)" :animate="true" />
 *
 * Props:
 *   color1   — sol üst blob rengi (Tailwind sınıf parçası ya da CSS renk değeri)
 *   color2   — sağ alt blob rengi
 *   animate  — blob'lara animate-pulse ekler (varsayılan false)
 */
defineProps({
  color1: {
    type: String,
    default: 'rgba(0,191,255,0.15)'
  },
  color2: {
    type: String,
    default: 'rgba(242,13,128,0.12)'
  },
  animate: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <!-- Sol üst neon blob -->
  <div
    class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full blur-[120px] pointer-events-none mix-blend-screen"
    :class="animate ? 'animate-pulse' : ''"
    :style="{ backgroundColor: color1 }"
  ></div>

  <!-- Sağ alt neon blob -->
  <div
    class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full blur-[120px] pointer-events-none mix-blend-screen"
    :class="animate ? 'animate-pulse' : ''"
    :style="{ backgroundColor: color2, animationDelay: animate ? '1s' : undefined }"
  ></div>

  <!-- Dot-grid overlay -->
  <div
    class="absolute inset-0 opacity-50 z-0 pointer-events-none"
    style="background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')"
  ></div>
</template>
