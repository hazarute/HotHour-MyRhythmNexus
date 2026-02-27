<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'card' // card | detail
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  isActive: {
    type: Boolean,
    default: true
  },
  animateIcon: {
    type: Boolean,
    default: false
  },
  gradientClass: {
    type: String,
    default: 'from-primary via-blue-600 to-neon-blue'
  },
  shadowClass: {
    type: String,
    default: ''
  },
  cardLabel: {
    type: String,
    default: 'Hemen Kap'
  },
  showTrailingIcon: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const onClick = (event) => {
  if (props.disabled || props.loading) return
  emit('click', event)
}
</script>

<template>
  <button
    v-if="variant === 'card'"
    class="w-full py-3 rounded-lg bg-primary hover:bg-neon-blue hover:shadow-neon-blue text-white font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 group/btn"
    :disabled="disabled || loading"
    @click.stop="onClick"
  >
    <span>{{ cardLabel }}</span>
    <span v-if="showTrailingIcon" class="material-symbols-outlined group-hover/btn:translate-x-1 transition-transform text-lg">bolt</span>
  </button>

  <button
    v-else
    class="flex group relative w-full overflow-hidden rounded-2xl p-[2px] transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg mb-2"
    :class="[gradientClass, shadowClass]"
    :disabled="disabled || loading"
    @click="onClick"
  >
    <div class="relative flex h-16 w-full items-center justify-center rounded-[14px] px-8 transition-all" :class="`bg-gradient-to-r ${gradientClass}`">
      <span class="absolute right-0 -mt-12 -mr-12 h-32 w-32 translate-x-1/2 rotate-45 bg-white opacity-10 blur-xl transition-all duration-1000 group-hover:-translate-x-full"></span>

      <span v-if="loading" class="flex items-center gap-2 text-white font-bold animate-pulse">
        <span class="material-symbols-outlined animate-spin">sync</span>
        İŞLENİYOR...
      </span>

      <div v-else class="flex items-center gap-2">
        <span class="material-symbols-outlined text-white text-3xl font-bold" :class="{ 'animate-pulse': animateIcon }">shopping_bag</span>
        <span class="text-2xl font-black text-white tracking-wider uppercase">
          {{ isActive ? 'HEMEN KAP' : 'TÜKENDİ' }}
        </span>
      </div>
    </div>
  </button>
</template>
