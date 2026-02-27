<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuctionStore } from '@/stores/auction'
import CountDownTimer from '@/components/CountDownTimer.vue'

const router = useRouter()
const store = useAuctionStore()
const searchQuery = ref('')
const statusFilter = ref('ALL') // ALL, ACTIVE, SOLD, DRAFT
const showFilterDropdown = ref(false)

onMounted(() => {
  store.fetchAuctions()
})

const filteredAuctions = computed(() => {
    // Create a copy to avoid mutating the store directly
    let result = [...store.auctions]
    
    // Status Filter
    if (statusFilter.value !== 'ALL') {
        result = result.filter(a => a.status === statusFilter.value)
    }
    
    // Search Filter
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(a => 
            a.title.toLowerCase().includes(query) || 
            (a.description && a.description.toLowerCase().includes(query)) ||
            String(a.id).includes(query)
        )
    }

    // Sort by updated_at (or created_at) descending to show most recent first
    result.sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at || a.updatedAt || a.createdAt || 0)
        const dateB = new Date(b.updated_at || b.created_at || b.updatedAt || b.createdAt || 0)
        return dateB - dateA
    })
    
    return result
})

const activeAuctions = computed(() => store.auctions.filter((a) => a.status === 'ACTIVE').length)
const soldAuctions = computed(() => store.auctions.filter((a) => a.status === 'SOLD').length)

// Real Data Calculations
const totalRevenue = computed(() => {
    return store.auctions
        .filter(a => a.status === 'SOLD' && (a.current_price || a.currentPrice))
        .reduce((sum, a) => sum + Number(a.current_price || a.currentPrice), 0)
})

const avgSoldPrice = computed(() => {
    if (soldAuctions.value === 0) return 0
    return totalRevenue.value / soldAuctions.value
})

// Mock for active bidders as it needs websocket tracking
const activeBidders = ref(Math.floor(Math.random() * 20) + 5) 

const formatCurrency = (val) => {
    if (val === undefined || val === null) return '₺0.00'
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(val)
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString('tr-TR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    })
}
</script>

<template>
  <div>
    <!-- Header Area -->
    <header class="sticky top-0 z-10 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3 md:px-8 md:py-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">Aktif Oturumlar</h2>
            <p class="text-slate-500 dark:text-slate-400 text-xs md:text-sm mt-1">Bugünkü dinamik fiyatlandırma oturumlarını yönet</p>
        </div>
        <div class="flex items-center gap-2 md:gap-4 w-full md:w-auto justify-end">
            <button class="flex items-center justify-center p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-[#232d3f] transition-colors">
                <span class="material-symbols-outlined">notifications</span>
            </button>
            <button @click="router.push({ name: 'admin-auction-create' })" class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-primary hover:bg-blue-600 text-white px-4 py-2 md:px-5 md:py-2.5 rounded-lg shadow-lg shadow-primary/25 transition-all active:scale-95 text-sm">
                <span class="material-symbols-outlined" style="font-size: 20px;">add</span>
                <span class="font-medium">Oturum Oluştur</span>
            </button>
        </div>
    </header>

    <div class="p-8 flex flex-col gap-8">
        
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Total Revenue Card -->
            <div class="bg-white dark:bg-[#1a2230] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                <div class="absolute -right-6 -top-6 size-24 bg-primary/10 rounded-full group-hover:scale-110 transition-transform duration-500"></div>
                <div class="flex flex-col gap-4 relative z-10">
                    <div class="flex justify-between items-start">
                        <div class="p-2 bg-slate-100 dark:bg-[#232d3f] rounded-lg text-slate-600 dark:text-slate-400">
                            <span class="material-symbols-outlined">attach_money</span>
                        </div>
                    </div>
                    <div>
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Toplam Ciro</p>
                        <h3 class="text-slate-900 dark:text-white text-3xl font-bold tracking-tight">{{ formatCurrency(totalRevenue) }}</h3>
                    </div>
                </div>
            </div>

            <!-- Sold Spots Card -->
            <div class="bg-white dark:bg-[#1a2230] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                <div class="absolute -right-6 -top-6 size-24 bg-purple-500/10 rounded-full group-hover:scale-110 transition-transform duration-500"></div>
                <div class="flex flex-col gap-4 relative z-10">
                    <div class="flex justify-between items-start">
                         <div class="p-2 bg-slate-100 dark:bg-[#232d3f] rounded-lg text-slate-600 dark:text-slate-400">
                            <span class="material-symbols-outlined">confirmation_number</span>
                        </div>
                    </div>
                    <div>
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Toplam Satılan</p>
                        <h3 class="text-slate-900 dark:text-white text-3xl font-bold tracking-tight">{{ soldAuctions }} Oturum</h3>
                    </div>
                </div>
            </div>
            
            <!-- Avg Price Card -->
            <div class="bg-white dark:bg-[#1a2230] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                <div class="absolute -right-6 -top-6 size-24 bg-orange-500/10 rounded-full group-hover:scale-110 transition-transform duration-500"></div>
                <div class="flex flex-col gap-4 relative z-10">
                    <div class="flex justify-between items-start">
                         <div class="p-2 bg-slate-100 dark:bg-[#232d3f] rounded-lg text-slate-600 dark:text-slate-400">
                            <span class="material-symbols-outlined">analytics</span>
                        </div>
                    </div>
                    <div>
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Ort. Satış Fiyatı</p>
                        <h3 class="text-slate-900 dark:text-white text-3xl font-bold tracking-tight">{{ formatCurrency(avgSoldPrice) }}</h3>
                    </div>
                </div>
            </div>

            <!-- Active Users Card -->
            <div class="bg-white dark:bg-[#1a2230] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                <div class="absolute -right-6 -top-6 size-24 bg-cyan-500/10 rounded-full group-hover:scale-110 transition-transform duration-500"></div>
                <div class="flex flex-col gap-4 relative z-10">
                    <div class="flex justify-between items-start">
                        <div class="p-2 bg-slate-100 dark:bg-[#232d3f] rounded-lg text-slate-600 dark:text-slate-400">
                            <span class="material-symbols-outlined">group</span>
                        </div>
                        <!-- Mock Indicator -->
                        <span class="flex h-2 w-2 relative">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                        </span>
                    </div>
                    <div>
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Aktif Teklif Verenler</p>
                        <h3 class="text-slate-900 dark:text-white text-3xl font-bold tracking-tight">~{{ activeBidders }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Table Section -->
        <div class="flex flex-col rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#1a2230] shadow-sm overflow-hidden">
            <!-- Filters -->
            <div class="flex flex-wrap items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800 gap-4">
                <div class="relative max-w-sm w-full">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500 dark:text-slate-400">
                        <span class="material-symbols-outlined" style="font-size: 20px;">search</span>
                    </span>
                    <input v-model="searchQuery" class="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder-slate-400 dark:placeholder-slate-600 text-sm" placeholder="Oturum ara..." type="text">
                </div>
                <div class="flex items-center gap-2 relative">
                    <button @click="showFilterDropdown = !showFilterDropdown" class="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors">
                        <span class="material-symbols-outlined" style="font-size: 18px;">filter_list</span>
                        {{ 
                            {
                                'ALL': 'Tümü',
                                'DRAFT': 'Taslak',
                                'ACTIVE': 'Aktif',
                                'SOLD': 'Satıldı',
                                'EXPIRED': 'Süresi Dolan',
                                'CANCELLED': 'İptal Edildi'
                            }[statusFilter] || statusFilter
                        }}
                    </button>
                    <!-- Filter Dropdown -->
                    <div v-if="showFilterDropdown" class="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-[#1a2230] rounded-lg shadow-xl border border-slate-200 dark:border-slate-800 z-50 py-1">
                        <button @click="statusFilter = 'ALL'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Tümü</button>
                        <button @click="statusFilter = 'DRAFT'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Taslak</button>
                        <button @click="statusFilter = 'ACTIVE'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Aktif</button>
                        <button @click="statusFilter = 'SOLD'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Satıldı</button>
                        <button @click="statusFilter = 'EXPIRED'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Süresi Dolan</button>
                        <button @click="statusFilter = 'CANCELLED'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">İptal Edildi</button>
                    </div>
                </div>
            </div>

            <!-- Table Container -->
            <div class="overflow-x-auto">
                <!-- Mobile List View -->
                <div class="md:hidden flex flex-col divide-y divide-slate-200 dark:divide-slate-800">
                     <div v-if="filteredAuctions.length === 0" class="p-6 text-center text-slate-500 dark:text-slate-400 text-sm">
                        Kriterlere uygun oturum bulunamadı.
                     </div>
                     <div v-for="auction in filteredAuctions" :key="'mobile-'+auction.id" class="p-4 flex flex-col gap-3">
                        <div class="flex justify-between items-start">
                            <div class="flex flex-col">
                                <span class="font-semibold text-slate-900 dark:text-white">{{ auction.title }}</span>
                                <p class="text-[10px] text-slate-500 dark:text-slate-400 line-clamp-1 max-w-[200px]">{{ auction.description }}</p>
                            </div>
                            <span v-if="auction.status === 'ACTIVE'" class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary border border-primary/20">AKTİF</span>
                            <span v-else-if="auction.status === 'SOLD'" class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-[#0bda5e]/10 text-[#0bda5e] border border-[#0bda5e]/20">SATILDI</span>
                            <span v-else class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700">{{ auction.status }}</span>
                        </div>
                        <div class="flex items-center justify-between text-sm">
                            <div class="flex flex-col">
                                <span class="text-xs text-slate-400">Güncel Fiyat</span>
                                <span class="font-bold text-slate-900 dark:text-white">{{ formatCurrency(auction.current_price || auction.currentPrice || auction.start_price || auction.startPrice) }}</span>
                            </div>
                            <div class="flex flex-col items-end">
                                <span class="text-xs text-slate-400">Kalan Süre</span>
                                <CountDownTimer v-if="auction.status === 'ACTIVE'" :targetTime="auction.end_time || auction.endTime" :showLabel="false" :small="true" />
                                <span v-else class="text-xs font-mono text-slate-600 dark:text-slate-400">-</span>
                            </div>
                        </div>
                     </div>
                </div>

                <!-- Desktop Table View -->
                <table class="w-full text-left border-collapse hidden md:table">
                    <thead>
                        <tr class="bg-slate-50 dark:bg-background-dark/50 text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                            <th class="px-6 py-4 font-semibold w-32">Durum</th>
                            <th class="px-6 py-4 font-semibold">Oturum Adı</th>
                            <th class="px-6 py-4 font-semibold w-36">Başlangıç</th>
                            <th class="px-6 py-4 font-semibold w-36">Bitiş</th>
                            <th class="px-6 py-4 font-semibold">Güncel Fiyat</th>
                            <th class="px-6 py-4 font-semibold">Kalan Süre</th>
                            <th class="px-6 py-4 font-semibold text-right">İşlem</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 dark:divide-slate-800 text-sm">
                        
                        <tr v-if="filteredAuctions.length === 0">
                            <td colspan="5" class="px-6 py-8 text-center text-slate-500 dark:text-slate-400">
                                Kriterlere uygun oturum bulunamadı.
                            </td>
                        </tr>

                        <tr v-for="auction in filteredAuctions" :key="auction.id" class="group hover:bg-slate-50 dark:hover:bg-[#232d3f]/30 transition-colors">
                            <td class="px-6 py-4">
                                <span v-if="auction.status === 'ACTIVE'" class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-primary/10 text-primary border border-primary/20 shadow-[0_0_10px_rgba(37,106,244,0.15)] backdrop-blur-sm">
                                    AKTİF
                                </span>
                                <span v-else-if="auction.status === 'SOLD'" class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-[#0bda5e]/10 text-[#0bda5e] border border-[#0bda5e]/20 shadow-[0_0_10px_rgba(11,218,94,0.15)] backdrop-blur-sm">
                                    SATILDI
                                </span>
                                <span v-else class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700">
                                    {{ auction.status }}
                                </span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span class="text-slate-900 dark:text-white font-medium">{{ auction.title }}</span>
                                    <p class="text-slate-500 dark:text-slate-400 text-xs line-clamp-1 max-w-[300px]">{{ auction.description }}</p>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span class="text-xs text-slate-600 dark:text-slate-300 font-mono">
                                    {{ formatDate(auction.start_time || auction.startTime) }}
                                </span>
                            </td>
                            <td class="px-6 py-4">
                                <span class="text-xs text-slate-600 dark:text-slate-300 font-mono">
                                    {{ formatDate(auction.end_time || auction.endTime) }}
                                </span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2">
                                    <span class="text-slate-900 dark:text-white font-bold">{{ formatCurrency(auction.current_price || auction.currentPrice || auction.start_price || auction.startPrice) }}</span>
                                    <span v-if="auction.status === 'ACTIVE'" class="text-xs text-red-400"> Düşüyor</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2 text-primary font-medium font-mono">
                                    <span class="material-symbols-outlined" style="font-size: 16px;">timer</span>
                                    <CountDownTimer v-if="auction.status === 'ACTIVE'" :targetTime="auction.end_time || auction.endTime" :showLabel="false" :small="true" />
                                    <span v-else class="text-slate-500">-</span>
                                </div>
                            </td>
                            <td class="px-6 py-4 text-right">
                                <div class="flex items-center justify-end gap-2">
                                    <button v-if="['ACTIVE', 'DRAFT'].includes(auction.status)" @click="router.push({ name: 'admin-auction-edit', params: { id: auction.id } })" class="p-2 rounded-lg text-slate-400 hover:text-primary hover:bg-primary/10 transition-colors" title="Düzenle">
                                        <span class="material-symbols-outlined" style="font-size: 20px;">edit</span>
                                    </button>
                                    <button @click="router.push({ name: 'admin-auction-detail', params: { id: auction.id } })" class="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" title="Detaylar">
                                        <span class="material-symbols-outlined" style="font-size: 20px;">visibility</span>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Pagination (Static for demo) -->
            <div class="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>Toplam {{ filteredAuctions.length }} sonuçtan 1 - {{ filteredAuctions.length }} arası gösteriliyor</span>
                <div class="flex gap-2">
                    <button disabled class="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50">
                        <span class="material-symbols-outlined" style="font-size: 18px;">chevron_left</span>
                    </button>
                    <button class="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800">
                        <span class="material-symbols-outlined" style="font-size: 18px;">chevron_right</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>
