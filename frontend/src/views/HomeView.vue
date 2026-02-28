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

const onTurboTriggered = (data) => {
    if (!data?.auction_id) return
    store.updateAuctionTurboStartedAt(data.auction_id, data.turbo_started_at)
}

onMounted(async () => {
    if (!socketStore.isConnected) {
        socketStore.connect()
    }

    socketStore.on('price_update', onPriceUpdate)
    socketStore.on('auction_booked', onAuctionBooked)
    socketStore.on('turbo_triggered', onTurboTriggered)

    await store.fetchAuctions()
    subscribeToAuctionRooms()
})

onUnmounted(() => {
    unsubscribeFromAuctionRooms()
    socketStore.off('price_update', onPriceUpdate)
    socketStore.off('auction_booked', onAuctionBooked)
    socketStore.off('turbo_triggered', onTurboTriggered)
})

const goToAllAuctions = () => {
  router.push({ name: 'all-auctions' })
}

const goToHowItWorks = () => {
    router.push({ name: 'how-it-works' })
}
</script>

<template>
  <div class="w-full min-h-screen bg-[#050505] font-sans text-slate-200 selection:bg-neon-blue/30 selection:text-white overflow-x-hidden">
    
    <section class="relative w-full pt-20 pb-16 md:pt-32 md:pb-24 overflow-hidden border-b border-white/5">
        <div class="absolute top-0 left-1/4 w-[40rem] h-[40rem] bg-neon-blue/10 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
        <div class="absolute bottom-0 right-1/4 w-[30rem] h-[30rem] bg-[#f20d80]/10 rounded-full blur-[100px] pointer-events-none mix-blend-screen"></div>
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')] opacity-50 z-0"></div>
        
        <div class="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 flex flex-col items-center text-center">
            
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neon-blue/10 border border-neon-blue/30 text-xs font-black uppercase tracking-widest text-neon-blue mb-8 backdrop-blur-md shadow-[0_0_15px_rgba(0,191,255,0.2)]">
                <span class="relative flex h-2.5 w-2.5">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-neon-blue opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-neon-blue"></span>
                </span>
                Canlı Oturum Arenası
            </div>
            
            <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black text-white leading-[1.1] tracking-tighter mb-6 drop-shadow-2xl">
                Zaman <span class="text-transparent bg-clip-text bg-gradient-to-br from-slate-300 to-slate-600">Daralıyor.</span><br>
                Fiyatlar <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#f20d80] to-[#ff7b00] drop-shadow-[0_0_15px_rgba(242,13,128,0.5)]">Eriyor.</span>
            </h1>
            
            <p class="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed font-medium">
                Premium Pilates seanslarında boş kalan yerleri Hollanda Açık Artırması ile satıyoruz. 
                Fiyat her geçen an düşer, butona ilk basan piyasanın çok altında stüdyoya girer.
            </p>
            
            <div class="flex flex-col sm:flex-row gap-4 w-full sm:w-auto justify-center z-20">
                <button @click="goToAllAuctions" class="group relative px-8 py-4 bg-neon-blue text-black font-black uppercase tracking-widest rounded-2xl overflow-hidden transition-all hover:scale-105 shadow-[0_0_30px_rgba(0,191,255,0.3)] hover:shadow-[0_0_40px_rgba(0,191,255,0.6)]">
                    <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
                    <span class="relative flex items-center justify-center gap-2">
                        <span class="material-symbols-outlined text-[20px]">local_fire_department</span>
                        Fırsatları Gör
                    </span>
                </button>
                <button @click="goToHowItWorks" class="px-8 py-4 bg-white/5 hover:bg-white/10 text-white border border-white/10 hover:border-white/20 font-bold uppercase tracking-widest rounded-2xl transition-all flex items-center justify-center gap-2 backdrop-blur-md">
                    <span class="material-symbols-outlined text-[20px]">help</span>
                    Sistem Nasıl Çalışır?
                </button>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-4xl mt-16 md:mt-24">
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 backdrop-blur-md flex flex-col items-center text-center">
                    <span class="material-symbols-outlined text-neon-blue mb-2 text-3xl">radar</span>
                    <span class="text-3xl font-black text-white font-mono">{{ activeAuctions.length }}</span>
                    <span class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">Aktif Seans</span>
                </div>
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 backdrop-blur-md flex flex-col items-center text-center">
                    <span class="material-symbols-outlined text-green-400 mb-2 text-3xl">trending_down</span>
                    <span class="text-3xl font-black text-white font-mono">%45</span>
                    <span class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">Ortalama İndirim</span>
                </div>
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 backdrop-blur-md flex flex-col items-center text-center hidden md:flex">
                    <span class="material-symbols-outlined text-[#f20d80] mb-2 text-3xl">bolt</span>
                    <span class="text-3xl font-black text-white font-mono">2s</span>
                    <span class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">Turbo Mod Süresi</span>
                </div>
                <div class="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 backdrop-blur-md flex flex-col items-center text-center hidden md:flex">
                    <span class="material-symbols-outlined text-slate-400 mb-2 text-3xl">storefront</span>
                    <span class="text-3xl font-black text-white font-mono">Yerinde</span>
                    <span class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mt-1">Ödeme Modeli</span>
                </div>
            </div>
        </div>
    </section>
    
    <section class="w-full max-w-7xl mx-auto px-6 lg:px-8 py-16 md:py-24 relative z-10">
        
        <div class="flex flex-col md:flex-row items-center justify-between mb-10 gap-4 border-b border-slate-800 pb-6">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-neon-blue/10 border border-neon-blue/30 flex items-center justify-center">
                    <span class="material-symbols-outlined text-neon-blue">live_tv</span>
                </div>
                <div>
                    <h2 class="text-2xl md:text-3xl font-black text-white tracking-tight">Yayındaki Oturumlar</h2>
                    <p class="text-slate-400 text-sm mt-1">Şu an fiyatı düşmeye devam eden sıcak fırsatlar.</p>
                </div>
            </div>
            
            <button @click="goToAllAuctions" class="text-sm font-bold text-slate-400 hover:text-neon-blue transition-colors flex items-center gap-1 uppercase tracking-wider group">
                Tümünü Gör 
                <span class="material-symbols-outlined text-[16px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
            </button>
        </div>
        
        <div v-if="store.loading" class="flex flex-col justify-center items-center py-20">
            <div class="relative w-16 h-16">
                <div class="absolute inset-0 rounded-full border-t-2 border-neon-blue animate-spin"></div>
            </div>
            <p class="text-slate-500 mt-4 font-mono uppercase tracking-widest text-xs">Arenaya Bağlanılıyor...</p>
        </div>

        <div v-else-if="store.error" class="bg-red-950/20 border border-red-900/50 rounded-2xl p-6 text-center backdrop-blur-sm max-w-lg mx-auto">
             <span class="material-symbols-outlined text-red-500 text-4xl mb-2">wifi_off</span>
             <p class="text-red-300 font-medium">{{ store.error }}</p>
        </div>

        <div v-else-if="activeAuctions.length === 0" class="flex flex-col items-center justify-center py-20 text-center bg-slate-900/20 border-2 border-dashed border-slate-800 rounded-3xl">
            <div class="w-20 h-20 bg-slate-900 border border-slate-700 rounded-full flex items-center justify-center mb-4 relative">
                <div class="absolute inset-0 rounded-full border border-slate-600 animate-ping opacity-20"></div>
                <span class="material-symbols-outlined text-3xl text-slate-500">hourglass_empty</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Şu An Fırsat Yok</h3>
            <p class="text-slate-400 text-sm max-w-sm">
                Şu anda aktif veya fiyatı düşen bir oturum bulunmuyor. Stüdyolar yeni seanslar eklediğinde burada görünecek.
            </p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <AuctionCard 
                v-for="auction in activeAuctions" 
                :key="auction.id" 
                :auction="auction" 
                class="transform hover:-translate-y-1 transition-all duration-300"
            />
        </div>
    </section>
  </div>
</template>

<style scoped>
/* Opsiyonel: Grid arka plan deseni için ekstra sınıf */
</style>