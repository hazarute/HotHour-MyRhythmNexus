<script setup>
import { onMounted } from 'vue'
import { useAuctionStore } from '../stores/auction'
import AuctionCard from '../components/AuctionCard.vue'

const store = useAuctionStore()

onMounted(() => {
  store.fetchAuctions()
})
</script>

<template>
  <div class="w-full">
    <!-- Hero Section -->
    <section class="w-full relative px-6 md:px-12 py-16 overflow-hidden">
        <!-- Background Gradient/Image -->
        <div class="absolute inset-0 z-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1518310383802-640c2de311b2?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center" data-alt="Dark abstract futuristic gym atmosphere with neon lights"></div>
        <div class="absolute inset-0 z-0 bg-gradient-to-r from-background-dark via-background-dark/95 to-transparent"></div>
        <div class="absolute inset-0 z-0 bg-gradient-to-t from-background-dark via-transparent to-transparent"></div>
        
        <div class="relative z-10 max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-12">
            <div class="max-w-2xl">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neon-blue mb-6">
                    <span class="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
                    Canlý Oturum Arenasý
                </div>
                
                <h1 class="text-5xl md:text-7xl font-black text-white leading-tight tracking-tight mb-6">
                    Daha Az Öde. <br>
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-primary text-glow">Yanmaya Hazýr Ol.</span>
                </h1>
                
                <p class="text-lg text-slate-400 mb-8 max-w-lg leading-relaxed">
                    Dinamik fiyatlarla üst düzey Pilates deneyimini yaþa. Saat iþliyor, fiyat düþüyor. Tükenmeden yerini kap.
                </p>
                
                <div class="flex flex-wrap gap-4">
                    <button class="bg-primary hover:bg-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-neon-blue transition-all flex items-center gap-2">
                        <span class="material-symbols-outlined">gavel</span>
                        Canlý Oturumlarý Gör
                    </button>
                    <button class="bg-transparent hover:bg-white/5 text-white border border-white/20 font-bold py-3 px-8 rounded-lg transition-colors">
                        Daha Fazla Bilgi
                    </button>
                </div>
            </div>
            
            <!-- Hero Stats/Visual -->
            <div class="hidden md:flex flex-col gap-4 w-80">
                <div class="glass-card p-6 rounded-xl border-l-4 border-neon-magenta">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-slate-400 text-xs uppercase tracking-wider">Aktif Teklif Verenler</span>
                        <span class="material-symbols-outlined text-neon-magenta">groups</span>
                    </div>
                    <div class="text-3xl font-bold text-white">{{ store.auctions.length > 0 ? store.auctions.length * 137 : 1248 }}</div>
                    <div class="text-xs text-green-400 flex items-center gap-1 mt-1">
                        <span class="material-symbols-outlined text-sm">trending_up</span> Bu saatte +%12
                    </div>
                </div>
                
                <div class="glass-card p-6 rounded-xl border-l-4 border-neon-orange">
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
        </div>
    </section>
    
    <!-- Auction Grid -->
    <section class="w-full max-w-7xl mx-auto px-6 md:px-12 py-12">
        <div class="flex items-center justify-between mb-8">
            <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                <span class="w-2 h-8 bg-neon-magenta rounded-full"></span>
                Canlý Oturumlar
            </h2>
            <span class="text-slate-500 text-sm">{{ store.auctions.length }} aktif oturum gösteriliyor</span>
        </div>
        
        <div v-if="store.loading" class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-neon-blue"></div>
        </div>

        <div v-else-if="store.error" class="hh-card border-red-500/60 bg-red-900/20 p-4 text-center">
             <p class="text-red-400">{{ store.error }}</p>
        </div>

        <div v-else-if="store.auctions.length === 0" class="hh-card text-center text-gray-400 py-12 px-6">
            <p class="mb-4">Þu anda aktif bir oturum yok.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <AuctionCard 
                v-for="auction in store.auctions" 
                :key="auction.id" 
                :auction="auction" 
            />
        </div>
    </section>
  </div>
</template>
