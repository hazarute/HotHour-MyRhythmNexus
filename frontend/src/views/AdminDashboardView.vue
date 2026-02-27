<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuctionStore } from '@/stores/auction'
import AuctionCreateForm from '@/components/AuctionCreateForm.vue'
import CountDownTimer from '@/components/CountDownTimer.vue'

const store = useAuctionStore()
const showForm = ref(false)

onMounted(() => {
  store.fetchAuctions()
})

const handleCreate = async (formData) => {
    try {
        await store.createAuction(formData)
        showForm.value = false
        await store.fetchAuctions()
    } catch (err) {
        alert('Oturum oluşturulurken hata: ' + err.message)
    }
}

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
            <button @click="showForm = !showForm" class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-primary hover:bg-blue-600 text-white px-4 py-2 md:px-5 md:py-2.5 rounded-lg shadow-lg shadow-primary/25 transition-all active:scale-95 text-sm">
                <span class="material-symbols-outlined" style="font-size: 20px;">{{ showForm ? 'close' : 'add' }}</span>
                <span class="font-medium">{{ showForm ? 'Kapat' : 'Oturum Oluştur' }}</span>
            </button>
        </div>
    </header>

    <div class="p-8 flex flex-col gap-8">
        
        <!-- Create Form (Conditionally rendered) -->
        <transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-4 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-4 opacity-0">
            <div v-if="showForm" class="bg-white dark:bg-[#1a2230] p-4 md:p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative z-20">
                <AuctionCreateForm @create-auction="handleCreate" />
            </div>
        </transition>

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
                        <span class="flex items-center gap-1 text-xs font-semibold text-[#0bda5e] bg-[#0bda5e]/10 px-2 py-1 rounded-full">
                            <span class="material-symbols-outlined" style="font-size: 14px;">trending_up</span>
                            +12%
                        </span>
                    </div>
                    <div>
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
                        <span class="flex items-center gap-1 text-xs font-semibold text-[#0bda5e] bg-[#0bda5e]/10 px-2 py-1 rounded-full">
                            <span class="material-symbols-outlined" style="font-size: 14px;">check</span>
                            Satılan
                        </span>
                    </div>
                    <div>
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">Toplam Satılan</p>
                        <h3 class="text-slate-900 dark:text-white text-3xl font-bold tracking-tight">{{ soldAuctions }} Yer</h3>
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
                         <span class="flex items-center gap-1 text-xs font-semibold text-orange-500 bg-orange-500/10 px-2 py-1 rounded-full">
                            Ort.
                        </span>
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
                    <input class="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder-slate-400 dark:placeholder-slate-600 text-sm" placeholder="Oturum ara..." type="text">
                </div>
                <div class="flex items-center gap-2">
                    <button class="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors">
                        <span class="material-symbols-outlined" style="font-size: 18px;">filter_list</span>
                        Filtrele
                    </button>
                    <button class="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors">
                        <span class="material-symbols-outlined" style="font-size: 18px;">download</span>
                        Dışa Aktar
                    </button>
                </div>
            </div>

            <!-- Table Container -->
            <div class="overflow-x-auto">
                <!-- Mobile List View -->
                <div class="md:hidden flex flex-col divide-y divide-slate-200 dark:divide-slate-800">
                     <div v-if="store.auctions.length === 0" class="p-6 text-center text-slate-500 dark:text-slate-400 text-sm">
                        Aktif oturum bulunamadı.
                     </div>
                     <div v-for="auction in store.auctions" :key="'mobile-'+auction.id" class="p-4 flex flex-col gap-3">
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
                            <th class="px-6 py-4 font-semibold">Güncel Fiyat</th>
                            <th class="px-6 py-4 font-semibold">Kalan Süre</th>
                            <th class="px-6 py-4 font-semibold text-right">İşlem</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 dark:divide-slate-800 text-sm">
                        
                        <tr v-if="store.auctions.length === 0">
                            <td colspan="5" class="px-6 py-8 text-center text-slate-500 dark:text-slate-400">
                                Aktif oturum bulunamadı. Başlamak için yeni bir tane oluşturun.
                            </td>
                        </tr>

                        <tr v-for="auction in store.auctions" :key="auction.id" class="group hover:bg-slate-50 dark:hover:bg-[#232d3f]/30 transition-colors">
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
                                <button class="p-2 rounded-lg text-slate-400 hover:text-primary hover:bg-primary/10 transition-colors">
                                    <span class="material-symbols-outlined" style="font-size: 20px;">edit</span>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Pagination (Static for demo) -->
            <div class="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>Toplam {{ store.auctions.length }} sonuçtan 1 - {{ store.auctions.length }} arası gösteriliyor</span>
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
