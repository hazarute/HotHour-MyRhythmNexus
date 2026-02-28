<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'
import AuctionCard from '../components/AuctionCard.vue'
import { isAuctionActive } from '../utils/auction'

const router = useRouter()
const store = useAuctionStore()
const socketStore = useSocketStore()

const activeAuctions = computed(() => {
    return store.auctions.filter(isAuctionActive)
})

const subscribeToAuctionRooms = () => {
    store.auctions.forEach((auction) => {
        if (auction?.id) {
            socketStore.subscribeAuction(auction.id)
        }
    })
}

const unsubscribeFromAuctionRooms = () => {
    store.auctions.forEach((auction) => {
        if (auction?.id) {
            socketStore.unsubscribeAuction(auction.id)
        }
    })
}

const onPriceUpdate = (data) => {
    if (!data?.auction_id) return
    store.updatePrice(data.auction_id, data.current_price)
}

const onAuctionBooked = (data) => {
    if (!data?.auction_id) return
    store.updateAuctionStatus(data.auction_id, 'SOLD')
}

onMounted(async () => {
    if (!socketStore.isConnected) {
        socketStore.connect()
    }

    socketStore.on('price_update', onPriceUpdate)
    socketStore.on('auction_booked', onAuctionBooked)

    await store.fetchAuctions()
    subscribeToAuctionRooms()
})

onUnmounted(() => {
    unsubscribeFromAuctionRooms()
    socketStore.off('price_update', onPriceUpdate)
    socketStore.off('auction_booked', onAuctionBooked)
})

const goToAllAuctions = () => {
  router.push({ name: 'all-auctions' })
}
</script>

<template>
  <div class="w-full">
    <!-- Hero Section -->
    <section class="w-full relative px-6 md:px-12 py-12 md:py-16 overflow-hidden">
        <!-- Background Gradient/Image -->
        <div class="absolute inset-0 z-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1518310383802-640c2de311b2?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center" data-alt="Dark abstract futuristic gym atmosphere with neon lights"></div>
        <div class="absolute inset-0 z-0 bg-gradient-to-r from-background-dark via-background-dark/95 to-transparent"></div>
        <div class="absolute inset-0 z-0 bg-gradient-to-t from-background-dark via-transparent to-transparent"></div>
        
        <div class="relative z-10 max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-8 lg:gap-12">
            <div class="max-w-2xl w-full text-center lg:text-left">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neon-blue mb-4 md:mb-6">
                    <span class="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
                    Canlı Oturum Arenası
                </div>
                
                <h1 class="text-4xl sm:text-5xl md:text-7xl font-black text-white leading-tight tracking-tight mb-4 md:mb-6">
                    Daha Az Öde. <br>
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-primary text-glow">Yanmaya Hazır Ol.</span>
                </h1>
                
                <p class="text-base md:text-lg text-slate-400 mb-6 md:mb-8 max-w-lg mx-auto lg:mx-0 leading-relaxed">
                    Dinamik fiyatlarla üst düzey Pilates deneyimini yaşa. Saat işliyor, fiyat düşüyor. Tükenmeden yerini kap.
                </p>
                
                <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                    <button @click="goToAllAuctions" class="bg-primary hover:bg-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-neon-blue transition-all flex items-center justify-center gap-2 active:scale-95">
                        <span class="material-symbols-outlined">gavel</span>
                        Canlı Oturumları Gör
                    </button>
                    <button class="bg-transparent hover:bg-white/5 text-white border border-white/20 font-bold py-3 px-8 rounded-lg transition-colors active:scale-95">
                        Daha Fazla Bilgi
                    </button>
                </div>
            </div>
            
            <!-- Hero Stats/Visual -->
            <div class="hidden md:flex lg:flex-col gap-4 w-full md:w-auto lg:w-80 justify-center">
                <div class="glass-card p-6 rounded-xl border-l-4 border-neon-magenta flex-1 lg:flex-none">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-slate-400 text-xs uppercase tracking-wider">Aktif Teklif Verenler</span>
                        <span class="material-symbols-outlined text-neon-magenta">groups</span>
                    </div>
                    <div class="text-3xl font-bold text-white">{{ activeAuctions.length }}</div>
                    <div class="text-xs text-green-400 flex items-center gap-1 mt-1">
                        <span class="material-symbols-outlined text-sm">trending_up</span> Bu saatte +%12
                    </div>
                </div>
                
                <div class="glass-card p-6 rounded-xl border-l-4 border-neon-orange flex-1 lg:flex-none">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-slate-400 text-xs uppercase tracking-wider">Ortalama Tasarruf</span>
                        <span class="material-symbols-outlined text-neon-orange">savings</span>
                    </div>
                    <div class="text-3xl font-bold text-white">%45</div>
                    <div class="text-xs text-slate-400 mt-1">
                        standart fiyatlara göre
                    </div>
                </div>
            </div>

            <!-- Mobile Stats Slider (Visible only on mobile) -->
             <div class="md:hidden w-full overflow-x-auto pb-4 flex gap-4 snap-x snap-mandatory px-1">
                <div class="glass-card p-4 rounded-xl border-l-4 border-neon-magenta min-w-[240px] snap-center">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-slate-400 text-[10px] uppercase tracking-wider">Aktif Teklif Verenler</span>
                        <span class="material-symbols-outlined text-neon-magenta text-lg">groups</span>
                    </div>
                    <div class="text-2xl font-bold text-white">{{ activeAuctions.length }}</div>
                    <div class="text-[10px] text-green-400 flex items-center gap-1 mt-1">
                        <span class="material-symbols-outlined text-[12px]">trending_up</span> Bu saatte +%12
                    </div>
                </div>
                <div class="glass-card p-4 rounded-xl border-l-4 border-neon-orange min-w-[240px] snap-center">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-slate-400 text-[10px] uppercase tracking-wider">Ortalama Tasarruf</span>
                        <span class="material-symbols-outlined text-neon-orange text-lg">savings</span>
                    </div>
                    <div class="text-2xl font-bold text-white">%45</div>
                    <div class="text-[10px] text-slate-400 mt-1">
                        standart fiyatlara göre
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Auction Grid -->
    <section class="w-full max-w-7xl mx-auto px-4 md:px-12 py-8 md:py-12">
        <div class="flex flex-col md:flex-row items-center justify-between mb-6 md:mb-8 gap-2">
            <h2 class="text-xl md:text-2xl font-bold text-white flex items-center gap-3">
                <span class="w-2 h-6 md:h-8 bg-neon-magenta rounded-full"></span>
                Canlı Oturumlar
            </h2>
            <span class="text-slate-500 text-xs md:text-sm">{{ activeAuctions.length }} aktif oturum gösteriliyor</span>
        </div>
        
        <div v-if="store.loading" class="flex justify-center items-center h-48 md:h-64">
            <div class="animate-spin rounded-full h-10 w-10 md:h-12 md:w-12 border-t-2 border-b-2 border-neon-blue"></div>
        </div>

        <div v-else-if="store.error" class="hh-card border-red-500/60 bg-red-900/20 p-4 text-center">
             <p class="text-red-400 text-sm md:text-base">{{ store.error }}</p>
        </div>

        <div v-else-if="activeAuctions.length === 0" class="hh-card text-center text-gray-400 py-10 md:py-12 px-6">
            <p class="mb-4 text-sm md:text-base">Şu anda aktif bir oturum yok.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
            <AuctionCard 
                v-for="auction in activeAuctions" 
                :key="auction.id" 
                :auction="auction" 
            />
        </div>
    </section>
  </div>
</template>
