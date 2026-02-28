<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'
import AuctionCard from '../components/AuctionCard.vue'
import { getAuctionStatus, getAuctionField } from '../utils/auction'

const router = useRouter()
const store = useAuctionStore()
const socketStore = useSocketStore()

const searchQuery = ref('')
const filterStatus = ref('ACTIVE')

const filteredAuctions = computed(() => {
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)

  const isWithinLastMonth = (auction) => {
    const dateValue =
      getAuctionField(auction, 'scheduled_at', 'scheduledAt') ??
      getAuctionField(auction, 'start_time', 'startTime') ??
      getAuctionField(auction, 'created_at', 'createdAt')

    if (!dateValue) return true
    const auctionDate = new Date(dateValue)
    if (Number.isNaN(auctionDate.getTime())) return true
    return auctionDate >= oneMonthAgo
  }

  let result = Array.isArray(store.auctions)
    ? store.auctions.filter((auction) => auction && typeof auction === 'object')
    : []

  result = result.filter(isWithinLastMonth)
  
  if (filterStatus.value !== 'ALL') {
    result = result.filter(a => getAuctionStatus(a) === filterStatus.value)
  }
  
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(a => 
      String(a?.title ?? '').toLowerCase().includes(query) ||
      String(a?.description ?? '').toLowerCase().includes(query)
    )
  }
  
  return result
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

const handleFilterChange = (status) => {
  filterStatus.value = status
}
</script>

<template>
  <div class="w-full min-h-screen bg-[#050505] font-sans text-slate-200 selection:bg-neon-blue/30 selection:text-white">
    
    <header class="relative px-6 py-12 md:py-16 overflow-hidden border-b border-white/5">
      <div class="absolute inset-0 bg-gradient-to-b from-neon-blue/5 via-transparent to-transparent pointer-events-none"></div>
      <div class="absolute top-0 right-1/4 w-96 h-96 bg-neon-blue/10 rounded-full blur-[100px] pointer-events-none"></div>
      
      <div class="max-w-7xl mx-auto relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neon-blue mb-4">
            <span class="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
            Canlı Pazar
          </div>
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-black text-white tracking-tight mb-2">
            Fırsatları <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-purple-500 drop-shadow-[0_0_15px_rgba(0,191,255,0.3)]">Keşfet</span>
          </h1>
          <p class="text-slate-400 text-sm md:text-base max-w-xl">
            Stüdyoların boş kalan seansları şu an açık artırmada. Zaman geçtikçe fiyat düşer, ilk basan kazanır.
          </p>
        </div>
        
        <div class="flex items-center gap-2 px-4 py-2 bg-black/50 border border-white/10 rounded-xl backdrop-blur-md">
          <span class="material-symbols-outlined text-neon-blue animate-pulse">sensors</span>
          <span class="text-xs font-bold text-slate-300 tracking-wider uppercase">Canlı Fiyat Akışı Aktif</span>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
      
      <div class="flex flex-col lg:flex-row gap-4 mb-10 sticky top-4 z-20">
        <div class="relative flex-1 group">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <span class="material-symbols-outlined text-slate-500 group-focus-within:text-neon-blue transition-colors">search</span>
          </div>
          <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Pilates türü veya stüdyo ara..."
            class="w-full pl-12 pr-4 py-4 bg-slate-900/60 border border-slate-700 rounded-2xl text-white placeholder-slate-500 backdrop-blur-md focus:bg-slate-900/90 focus:border-neon-blue focus:ring-1 focus:ring-neon-blue focus:outline-none transition-all shadow-lg"
          />
        </div>

        <div class="flex p-1.5 bg-slate-900/60 border border-slate-700 rounded-2xl backdrop-blur-md overflow-x-auto hide-scrollbar">
          <button 
            v-for="status in [
              { id: 'ALL', label: 'Tümü', icon: 'apps' },
              { id: 'ACTIVE', label: 'Aktif Olanlar', icon: 'local_fire_department' },
              { id: 'SOLD', label: 'Satıldı', icon: 'check_circle' }
            ]" 
            :key="status.id"
            @click="handleFilterChange(status.id)"
            class="flex items-center gap-2 px-6 py-2.5 rounded-xl whitespace-nowrap text-sm font-bold transition-all"
            :class="filterStatus === status.id 
              ? 'bg-neon-blue text-black shadow-[0_0_15px_rgba(0,191,255,0.4)]' 
              : 'text-slate-400 hover:text-white hover:bg-white/5'"
          >
            <span class="material-symbols-outlined text-sm" :class="filterStatus === status.id ? 'text-black' : ''">{{ status.icon }}</span>
            {{ status.label }}
          </button>
        </div>
      </div>

      <div v-if="store.loading" class="flex flex-col justify-center items-center py-24">
        <div class="relative w-20 h-20">
          <div class="absolute inset-0 rounded-full border-t-2 border-neon-blue animate-spin"></div>
          <div class="absolute inset-2 rounded-full border-r-2 border-purple-500 animate-spin opacity-70" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
        </div>
        <p class="text-slate-400 mt-6 font-medium animate-pulse">Oturumlar aranıyor...</p>
      </div>

      <div v-else-if="store.error" class="bg-red-950/30 border border-red-900/50 rounded-2xl p-8 text-center max-w-lg mx-auto backdrop-blur-sm mt-12">
        <div class="w-16 h-16 bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="material-symbols-outlined text-red-500 text-3xl">wifi_off</span>
        </div>
        <h3 class="text-xl font-bold text-white mb-2">Bağlantı Hatası</h3>
        <p class="text-red-200 mb-6">{{ store.error }}</p>
        <button @click="store.fetchAuctions()" class="px-6 py-3 bg-red-900/50 hover:bg-red-800/50 text-white rounded-xl transition-colors border border-red-700/50 text-sm font-bold">
          Tekrar Dene
        </button>
      </div>

      <div v-else-if="filteredAuctions.length === 0" class="flex flex-col items-center justify-center py-24 text-center border-2 border-dashed border-slate-800 rounded-3xl bg-slate-900/20">
        <div class="relative w-24 h-24 mb-6">
          <div class="absolute inset-0 bg-neon-blue/10 rounded-full animate-ping opacity-50"></div>
          <div class="relative flex items-center justify-center w-full h-full bg-slate-900 border border-slate-700 rounded-full">
            <span class="material-symbols-outlined text-4xl text-slate-500">radar</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold text-white mb-2">Radarımızda Bir Şey Yok</h3>
        <p class="text-slate-400 mb-8 max-w-md">
          {{ searchQuery ? `"${searchQuery}" aramasıyla eşleşen bir seans bulamadık.` : 'Şu an stüdyolarda boş bir seans bulunmuyor. Radarımız açık, beklemede kal!' }}
        </p>
        <button 
          v-if="searchQuery || filterStatus !== 'ACTIVE'"
          @click="() => { searchQuery = ''; filterStatus = 'ACTIVE' }"
          class="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold rounded-xl transition-colors flex items-center gap-2"
        >
          <span class="material-symbols-outlined text-sm">filter_alt_off</span>
          Filtreleri Temizle
        </button>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12">
        <AuctionCard 
          v-for="auction in filteredAuctions" 
          :key="auction.id" 
          :auction="auction" 
          class="transform hover:-translate-y-1 transition-all duration-300"
        />
      </div>

    </main>
  </div>
</template>

<style scoped>
/* Scrollbar'ı gizlemek için utility class (Filter sekmelerinde yatay kaydırma için) */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>