<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import CountDownTimer from './CountDownTimer.vue'
import HemenKapButton from './HemenKapButton.vue'
import { getAuctionCurrentPrice, getAuctionStartPrice, getAuctionEndTime, isAuctionTurbo } from '../utils/auction'

const props = defineProps({
  auction: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const authStore = useAuthStore()

const formatPrice = (p) => {
    const value = Number(p || 0)
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(value)
}

const goToDetail = () => {
    router.push({ name: 'auction-detail', params: { id: props.auction.id } })
}

const handleHemenKap = () => {
    const targetRoute = { name: 'auction-detail', params: { id: props.auction.id } }

    if (!authStore.isAuthenticated) {
        router.push({
            name: 'login',
            query: { redirect: router.resolve(targetRoute).href }
        })
        return
    }

    router.push(targetRoute)
}

const currentPrice = computed(() => {
    return getAuctionCurrentPrice(props.auction)
})

const startPrice = computed(() => {
    return getAuctionStartPrice(props.auction)
})

const endTime = computed(() => getAuctionEndTime(props.auction))
const isTurbo = computed(() => isAuctionTurbo(props.auction))

// Random image selection for demo purposes if no image provided
const bgImage = computed(() => {
    // Basic placeholder check, normally this comes from backend
    return props.auction.image_url || props.auction.imageUrl || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBzQLXU7vvnTRdJ4MV4keULwtXLs9kob4G3VxrcVseAk9_7W6-DUBymCB389nrrP0dv4LJqbZPibtOIZqpJ9yCQvNBLY2ztMD3KkVCkR2XvJwaIwzi2eB_wRlZzNGkSJZmZLPEdMRxfXvNFb72QNivwO4mePlhNA9dhZkAvHkb21evrbK53XO7qPWYyZzgh8VkDCIxPYOC96choIVf7SgvFPtKGfXOPTBZNDR33gdq4vd0kJIgRgGyLwK64lz8TKvGQh8Zi878Q65k'
})

const studioName = computed(() => props.auction.description || 'Açıklama bilgisi yok')
</script>

<template>
  <div 
        class="glass-card rounded-2xl overflow-hidden group transition-all duration-300 relative flex flex-col cursor-pointer"
        :class="isTurbo ? 'border-neon-orange shadow-neon-blue hover:shadow-neon-blue hover:scale-[1.01]' : 'hover:border-neon-blue/50'"
    @click="goToDetail"
  >
        <div v-if="isTurbo" class="absolute inset-0 pointer-events-none rounded-2xl ring-2 ring-neon-orange/50 animate-pulse"></div>

    <!-- Badge -->
    <div class="absolute top-3 left-3 z-10 bg-black/60 backdrop-blur-md text-neon-orange border border-neon-orange/30 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
        <span class="material-symbols-outlined text-sm animate-pulse">timer</span>
        <CountDownTimer :targetTime="endTime" :showLabel="false" :small="true" />
    </div>

        <div
            v-if="isTurbo"
            class="absolute top-3 right-3 z-10 bg-neon-orange/20 text-neon-orange border border-neon-orange/60 px-3 py-1 rounded-full text-[10px] font-black tracking-wider uppercase flex items-center gap-1 shadow-[0_0_14px_rgba(255,123,0,0.45)]"
        >
            <span class="material-symbols-outlined text-sm">bolt</span>
            Turbo
        </div>

    <!-- Background Image -->
    <div class="h-48 w-full bg-cover bg-center relative group-hover:scale-105 transition-transform duration-500" 
         :style="{ backgroundImage: `url(${bgImage})` }">
        <div class="absolute inset-0 bg-gradient-to-t from-background-dark via-transparent to-transparent"></div>
        <div v-if="isTurbo" class="absolute inset-0 bg-gradient-to-br from-neon-orange/20 via-transparent to-transparent"></div>
        <div v-if="isTurbo" class="absolute bottom-0 left-0 right-0 z-10 bg-gradient-to-r from-neon-orange/90 via-orange-500/90 to-neon-orange/90 text-black text-[10px] font-black uppercase tracking-[0.12em] py-1 text-center">
            ⚡ Turbo Mod Aktif
        </div>
    </div>

    <!-- Content -->
    <div class="p-5 flex flex-col flex-grow relative">
        <!-- Glowing line separator -->
        <div class="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-neon-blue to-transparent opacity-50"></div>
        
        <div class="flex justify-between items-start mb-2">
            <div>
                <h3 class="text-white font-bold text-lg leading-tight group-hover:text-primary transition-colors">{{ props.auction.title }}</h3>
                <p class="text-slate-400 text-xs">{{ studioName }}</p>
            </div>
            <div class="bg-white/5 p-1.5 rounded-lg border border-white/10">
                <span class="material-symbols-outlined text-white text-lg">bookmark</span>
            </div>
        </div>

        <div class="mt-auto pt-4 border-t border-white/5">
            <div class="flex justify-between items-end mb-4">
                <div class="flex flex-col">
                    <span class="text-slate-500 text-xs line-through">{{ formatPrice(startPrice) }}</span>
                                        <span class="font-bold text-2xl flex items-center gap-1" :class="isTurbo ? 'text-neon-orange' : 'text-white'">
                        {{ formatPrice(currentPrice) }}
                        <span class="material-symbols-outlined text-neon-orange text-sm animate-bounce">arrow_downward</span>
                    </span>
                </div>
                <div class="text-right">
                                        <p class="text-xs font-mono" :class="isTurbo ? 'text-neon-orange animate-pulse' : 'text-neon-orange'">
                                            {{ isTurbo ? 'Turbo fiyat akışı' : 'Fiyat düşüyor' }}
                                        </p>
                </div>
            </div>

                        <HemenKapButton
                            variant="card"
                            :card-label="isTurbo ? 'Hemen Kap ⚡' : 'Hemen Kap'"
                            :show-trailing-icon="!isTurbo"
                            @click="handleHemenKap"
                        />
        </div>
    </div>
  </div>
</template>
