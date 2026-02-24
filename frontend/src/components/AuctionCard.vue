<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import CountDownTimer from './CountDownTimer.vue'

const props = defineProps({
  auction: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const formatPrice = (p) => {
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(p)
}

const goToDetail = () => {
    router.push({ name: 'auction-detail', params: { id: props.auction.id } })
}

// Random image selection for demo purposes if no image provided
const bgImage = computed(() => {
    // Basic placeholder check, normally this comes from backend
    return props.auction.imageUrl || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBzQLXU7vvnTRdJ4MV4keULwtXLs9kob4G3VxrcVseAk9_7W6-DUBymCB389nrrP0dv4LJqbZPibtOIZqpJ9yCQvNBLY2ztMD3KkVCkR2XvJwaIwzi2eB_wRlZzNGkSJZmZLPEdMRxfXvNFb72QNivwO4mePlhNA9dhZkAvHkb21evrbK53XO7qPWYyZzgh8VkDCIxPYOC96choIVf7SgvFPtKGfXOPTBZNDR33gdq4vd0kJIgRgGyLwK64lz8TKvGQh8Zi878Q65k'
})

const studioName = computed(() => props.auction.studioName || 'Zenith Stüdyo') // Mock data if missing
const distance = computed(() => '1.2km uzakta') // Mock data
const originalPrice = computed(() => (props.auction.currentPrice || 0) * 1.5) // Mock logic
</script>

<template>
  <div 
    class="glass-card rounded-2xl overflow-hidden group hover:border-neon-blue/50 transition-all duration-300 relative flex flex-col cursor-pointer"
    @click="goToDetail"
  >
    <!-- Badge -->
    <div class="absolute top-3 left-3 z-10 bg-black/60 backdrop-blur-md text-neon-orange border border-neon-orange/30 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
        <span class="material-symbols-outlined text-sm animate-pulse">timer</span>
        <CountDownTimer :endTime="props.auction.endTime" />
    </div>

    <!-- Background Image -->
    <div class="h-48 w-full bg-cover bg-center relative group-hover:scale-105 transition-transform duration-500" 
         :style="{ backgroundImage: `url(${bgImage})` }">
        <div class="absolute inset-0 bg-gradient-to-t from-background-dark via-transparent to-transparent"></div>
    </div>

    <!-- Content -->
    <div class="p-5 flex flex-col flex-grow relative">
        <!-- Glowing line separator -->
        <div class="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-neon-blue to-transparent opacity-50"></div>
        
        <div class="flex justify-between items-start mb-2">
            <div>
                <h3 class="text-white font-bold text-lg leading-tight group-hover:text-primary transition-colors">{{ props.auction.title }}</h3>
                <p class="text-slate-400 text-xs">{{ studioName }}  {{ distance }}</p>
            </div>
            <div class="bg-white/5 p-1.5 rounded-lg border border-white/10">
                <span class="material-symbols-outlined text-white text-lg">bookmark</span>
            </div>
        </div>

        <div class="flex items-center gap-2 my-4">
            <span class="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] text-slate-300 uppercase tracking-wide">Orta Seviye</span>
            <span class="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] text-slate-300 uppercase tracking-wide">60 Dk</span>
        </div>

        <div class="mt-auto pt-4 border-t border-white/5">
            <div class="flex justify-between items-end mb-4">
                <div class="flex flex-col">
                    <span class="text-slate-500 text-xs line-through">{{ formatPrice(originalPrice) }}</span>
                    <span class="text-white font-bold text-2xl flex items-center gap-1">
                        {{ formatPrice(props.auction.currentPrice) }}
                        <span class="material-symbols-outlined text-neon-orange text-sm animate-bounce">arrow_downward</span>
                    </span>
                </div>
                <div class="text-right">
                    <p class="text-neon-orange text-xs font-mono">Fiyat düşüyor</p>
                </div>
            </div>

            <button class="w-full py-3 rounded-lg bg-primary hover:bg-neon-blue hover:shadow-neon-blue text-white font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 group/btn" @click.stop="goToDetail">
                <span>Hemen Kap</span>
                <span class="material-symbols-outlined group-hover/btn:translate-x-1 transition-transform text-lg">bolt</span>
            </button>
        </div>
    </div>
  </div>
</template>
