<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useAuthStore } from '../stores/auth'
import AuctionCard from '../components/AuctionCard.vue'

const router = useRouter()
const store = useAuctionStore()
const authStore = useAuthStore()

const searchQuery = ref('')
const filterStatus = ref('ACTIVE')

const filteredAuctions = computed(() => {
  let result = store.auctions
  
  if (filterStatus.value !== 'ALL') {
    result = result.filter(a => a.status === filterStatus.value)
  }
  
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(a => 
      a.title.toLowerCase().includes(query) ||
      a.description?.toLowerCase().includes(query)
    )
  }
  
  return result
})

onMounted(() => {
  store.fetchAuctions()
})

const handleFilterChange = (status) => {
  filterStatus.value = status
}
</script>

<template>
  <div class="w-full">
    <!-- Header Section -->
    <section class="hh-section max-w-7xl py-8 lg:py-12">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-8 border-b border-slate-800 pb-6 mb-8">
        <div class="flex-1">
          <h1 class="text-3xl md:text-4xl lg:text-5xl font-black text-white tracking-tight mb-2">
            Tüm Canlı <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-primary text-glow">Oturumlar</span>
          </h1>
          <p class="text-slate-400 text-sm md:text-base">{{ filteredAuctions.length }} aktif oturum mevcut</p>
        </div>
        <div class="flex items-center gap-2 text-xs text-slate-500">
          <span class="material-symbols-outlined text-sm">schedule</span>
          <span>Canlı fiyat güncellemeleri</span>
        </div>
      </div>

      <!-- Search Bar -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="md:col-span-2">
          <div class="relative">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">search</span>
            <input 
              v-model="searchQuery"
              type="text" 
              placeholder="Oturum ara..."
              class="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-500 focus:border-neon-blue focus:outline-none transition-colors text-sm md:text-base"
            />
          </div>
        </div>

        <!-- Sort/Filter (can be expanded) -->
        <div class="flex gap-2">
          <select 
            v-model="filterStatus"
            class="flex-1 px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm md:text-base focus:border-neon-blue focus:outline-none transition-colors cursor-pointer"
          >
            <option class="bg-slate-800 text-white" value="ALL">Tümü</option>
            <option class="bg-slate-800 text-white" value="ACTIVE">Aktif</option>
            <option class="bg-slate-800 text-white" value="DRAFT">Taslak</option>
            <option class="bg-slate-800 text-white" value="SOLD">Satıldı</option>
            <option class="bg-slate-800 text-white" value="EXPIRED">Süresi Bitti</option>
          </select>
        </div>
      </div>

      <!-- Filters Tabs (Mobile friendly) -->
      <div class="flex gap-2 overflow-x-auto pb-4 mb-8">
        <button 
          @click="handleFilterChange('ALL')"
          :class="[
            'px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium transition-all flex-shrink-0',
            filterStatus === 'ALL' 
              ? 'bg-primary text-white border border-primary' 
              : 'bg-white/5 text-slate-400 border border-white/10 hover:border-white/20'
          ]"
        >
          Tümü
        </button>
        <button 
          @click="handleFilterChange('ACTIVE')"
          :class="[
            'px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium transition-all flex-shrink-0',
            filterStatus === 'ACTIVE' 
              ? 'bg-neon-orange text-black border border-neon-orange' 
              : 'bg-white/5 text-slate-400 border border-white/10 hover:border-white/20'
          ]"
        >
          Aktif Olanlar
        </button>
        <button 
          @click="handleFilterChange('SOLD')"
          :class="[
            'px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium transition-all flex-shrink-0',
            filterStatus === 'SOLD' 
              ? 'bg-neon-orange text-black border border-neon-orange' 
              : 'bg-white/5 text-slate-400 border border-white/10 hover:border-white/20'
          ]"
        >
          Satıldı
        </button>
      </div>
    </section>

    <!-- Auctions Grid -->
    <section class="hh-section max-w-7xl">
      <div v-if="store.loading" class="flex justify-center items-center h-48 md:h-64">
        <div class="flex flex-col items-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 md:h-16 md:w-16 border-t-2 border-b-2 border-neon-blue"></div>
          <p class="text-slate-400 text-sm md:text-base">Oturumlar yükleniyor...</p>
        </div>
      </div>

      <div v-else-if="store.error" class="hh-card border-red-500/60 bg-red-900/20 p-6 text-center">
        <div class="flex items-center justify-center gap-3 mb-2">
          <span class="material-symbols-outlined text-red-400">error</span>
          <p class="text-red-400 font-medium">{{ store.error }}</p>
        </div>
        <p class="text-sm text-slate-400 mt-2">Lütfen sayfayı yenilemek için <button @click="store.fetchAuctions()" class="text-neon-blue hover:underline">buraya tıklayın</button></p>
      </div>

      <div v-else-if="filteredAuctions.length === 0" class="hh-card text-center py-12 md:py-16 px-6 border-dashed border-2 border-slate-700">
        <div class="flex justify-center mb-4">
          <span class="material-symbols-outlined text-5xl md:text-6xl text-slate-600">inbox</span>
        </div>
        <h3 class="text-xl md:text-2xl font-bold text-white mb-2">Oturum Bulunamadı</h3>
        <p class="text-slate-400 mb-6 text-sm md:text-base">
          {{ searchQuery ? 'Arama kriterlerinize uygun oturum yok.' : 'Şu anda aktif oturum bulunmamaktadır.' }}
        </p>
        <button 
          @click="() => { searchQuery = ''; filterStatus = 'ACTIVE' }"
          class="bg-primary hover:bg-blue-600 text-white font-bold py-2 px-6 rounded-lg transition-all inline-flex items-center gap-2 active:scale-95"
        >
          <span class="material-symbols-outlined">refresh</span>
          Temizle
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6 pb-8 md:pb-12">
        <AuctionCard 
          v-for="auction in filteredAuctions" 
          :key="auction.id" 
          :auction="auction" 
        />
      </div>
    </section>

    <!-- Back to Home Link -->
    <section class="hh-section max-w-7xl py-8 lg:py-12 text-center border-t border-slate-800">
      <button 
        @click="router.push('/')"
        class="inline-flex items-center gap-2 text-slate-400 hover:text-neon-blue transition-colors text-sm md:text-base"
      >
        <span class="material-symbols-outlined">arrow_back</span>
        Ana Sayfaya Dön
      </button>
    </section>
  </div>
</template>

<style scoped>
/* Additional styling can be added here if needed */
</style>
