<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const reservations = ref([])
const loading = ref(false)
const searchQuery = ref('')
const error = ref(null)

const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Fetch all reservations
const fetchReservations = async () => {
    loading.value = true
    error.value = null
    try {
        const response = await fetch(`${baseUrl}/api/v1/reservations/admin/all`, {
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })
        
        if (!response.ok) {
            throw new Error('Reervasyonlar getirilemedi')
        }
        
        const payload = await response.json()
        reservations.value = Array.isArray(payload) ? payload : (payload.reservations || [])
    } catch (err) {
        console.error(err)
        error.value = err.message
    } finally {
        loading.value = false
    }
}

// Filtered list
const filteredReservations = computed(() => {
    if (!searchQuery.value) return reservations.value
    
    const query = searchQuery.value.toLowerCase()
    return reservations.value.filter(res => 
        String(res.booking_code || '').toLowerCase().includes(query) ||
        String(res.user_name || '').toLowerCase().includes(query) ||
        String(res.auction_title || '').toLowerCase().includes(query)
    )
})

const formatDate = (value) => {
    if (!value) return '-'
    return new Date(value).toLocaleString('tr-TR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// Stats (Mocked or derived from real data if available)
const totalReservations = computed(() => reservations.value.length)
const pendingCheckIns = computed(() => reservations.value.filter(r => r.status === 'PENDING_ON_SITE' || r.status === 'CONFIRMED').length)
const checkedInToday = computed(() => reservations.value.filter(r => r.status === 'COMPLETED').length) // Assuming COMPLETED means checked in

const getStatusConfig = (status) => {
    switch(status) {
        case 'COMPLETED':
        case 'CHECKED_IN':
            return { label: 'Giriş Yapıldı', class: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300', dot: 'bg-green-500' }
        case 'PENDING_ON_SITE':
        case 'CONFIRMED':
            return { label: 'Bekliyor', class: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300', dot: 'bg-amber-500' }
        case 'CANCELLED':
            return { label: 'İptal', class: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300', dot: 'bg-red-500' }
        default:
            return { label: status, class: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300', dot: 'bg-slate-500' }
    }
}


onMounted(() => {
    fetchReservations()
})
</script>

<template>
  <div class="flex flex-col h-full w-full bg-background-light dark:bg-background-dark overflow-hidden relative">
    
    <!-- Header -->
    <header class="sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between px-4 py-3 md:px-8 md:py-5 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#111811]/80 backdrop-blur-md gap-4">
        <div class="flex flex-col gap-1">
            <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">Rezervasyon Yönetimi</h2>
            <p class="text-slate-500 dark:text-slate-400 text-xs md:text-sm">Rezervasyonları yönet ve misafir girişlerini kontrol et.</p>
        </div>
        <div class="flex gap-3 w-full md:w-auto justify-end">
            <button class="flex items-center gap-2 bg-slate-100 dark:bg-[#232d3f] hover:bg-slate-200 dark:hover:bg-[#344a34] text-slate-900 dark:text-white px-3 py-2 md:px-4 md:py-2 rounded-lg transition-colors text-sm font-medium">
                <span class="material-symbols-outlined text-[18px] md:text-[20px]">filter_list</span>
                Filtrele
            </button>
            <button @click="fetchReservations" class="bg-primary hover:bg-blue-600 text-white px-3 py-2 md:px-4 md:py-2 rounded-lg transition-colors text-sm font-bold shadow-lg shadow-primary/25 active:scale-95 flex items-center">
                <span class="material-symbols-outlined align-middle mr-1 text-[18px] md:text-[20px]">autorenew</span> Yenile
            </button>
        </div>
    </header>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto p-4 md:p-8">
        <div class="flex flex-col gap-6">
            
            <!-- Search Bar -->
            <div class="relative w-full">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span class="material-symbols-outlined text-slate-400 dark:text-slate-500">search</span>
                </div>
                <input 
                    v-model="searchQuery"
                    class="w-full bg-white dark:bg-[#1a2230] border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white text-base rounded-xl py-4 pl-12 pr-4 focus:ring-2 focus:ring-primary focus:border-transparent placeholder-slate-400 dark:placeholder-slate-600 shadow-sm transition-all outline-none" 
                    placeholder="Rezervasyon Kodu, Misafir Adı veya Stüdyo ara..." 
                    type="text"
                />
            </div>

            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- Total Reservations -->
                <div class="bg-white dark:bg-[#1a2230] p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                    <div class="absolute -right-6 -top-6 size-24 bg-primary/10 rounded-full group-hover:scale-110 transition-transform duration-500"></div>
                    <div class="flex justify-between items-start mb-2 relative z-10">
                        <div class="p-2 bg-primary/20 rounded-lg text-primary">
                            <span class="material-symbols-outlined">event_seat</span>
                        </div>
                        <span class="text-xs font-bold text-primary bg-primary/10 px-2 py-1 rounded-full">+12%</span>
                    </div>
                    <div class="relative z-10">
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Toplam Rezervasyon</p>
                        <h3 class="text-2xl font-bold text-slate-900 dark:text-white">{{ totalReservations }}</h3>
                    </div>
                </div>

                <!-- Pending Check-ins -->
                <div class="bg-white dark:bg-[#1a2230] p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                    <div class="absolute -right-6 -top-6 size-24 bg-orange-500/10 rounded-full group-hover:scale-110 transition-transform duration-500"></div>
                    <div class="flex justify-between items-start mb-2 relative z-10">
                        <div class="p-2 bg-orange-500/20 rounded-lg text-orange-500">
                            <span class="material-symbols-outlined">pending</span>
                        </div>
                        <span class="text-xs font-bold text-orange-500 bg-orange-500/10 px-2 py-1 rounded-full">İşlem Gerekli</span>
                    </div>
                    <div class="relative z-10">
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Bekleyen Girişler</p>
                        <h3 class="text-2xl font-bold text-slate-900 dark:text-white">{{ pendingCheckIns }}</h3>
                    </div>
                </div>

                <!-- Checked In Today -->
                <div class="bg-white dark:bg-[#1a2230] p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                    <div class="absolute -right-6 -top-6 size-24 bg-green-500/10 rounded-full group-hover:scale-110 transition-transform duration-500"></div>
                    <div class="flex justify-between items-start mb-2 relative z-10">
                        <div class="p-2 bg-green-500/20 rounded-lg text-green-500">
                            <span class="material-symbols-outlined">check_circle</span>
                        </div>
                    </div>
                    <div class="relative z-10">
                        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Bugün Giriş Yapanlar</p>
                        <h3 class="text-2xl font-bold text-slate-900 dark:text-white">{{ checkedInToday }}</h3>
                    </div>
                </div>
            </div>

            <!-- Table Container -->
            <div class="bg-white dark:bg-[#1a2230] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden flex flex-col">
                
                <!-- Mobile List View -->
                <div class="md:hidden flex flex-col divide-y divide-slate-200 dark:divide-slate-800">
                    <div v-if="loading" class="p-6 text-center text-slate-400 animate-pulse">Yükleniyor...</div>
                    <div v-else-if="filteredReservations.length === 0" class="p-8 text-center text-slate-500 dark:text-slate-400 flex flex-col items-center gap-2">
                        <span class="material-symbols-outlined text-4xl opacity-50">inbox</span>
                        <p>Kayıt bulunamadı.</p>
                    </div>
                    <div v-else v-for="res in filteredReservations" :key="'mobile-'+res.id" class="p-4 flex flex-col gap-4 bg-white dark:bg-[#1a2230]">
                         <div class="flex justify-between items-start">
                             <div>
                                 <div class="font-mono font-bold text-lg text-slate-900 dark:text-white" :class="{'line-through opacity-50': res.status === 'CANCELLED'}">
                                     #{{ res.booking_code }}
                                 </div>
                                 <div class="text-xs text-slate-400 mt-1">{{ formatDate(res.created_at) }}</div>
                             </div>
                             <span :class="getStatusConfig(res.status).class" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium border border-transparent">
                                <span :class="getStatusConfig(res.status).dot" class="w-1.5 h-1.5 rounded-full"></span>
                                {{ getStatusConfig(res.status).label }}
                            </span>
                         </div>
                         
                         <div class="flex items-center gap-3 bg-slate-50 dark:bg-[#232d3f]/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800">
                            <div class="h-10 w-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-500 shrink-0">
                                {{ (res.user_name || 'GK').substring(0,2).toUpperCase() }}
                            </div>
                            <div class="flex flex-col min-w-0">
                                <span class="text-sm font-medium text-slate-900 dark:text-white truncate">{{ res.user_name || 'Misafir' }}</span>
                                <span class="text-xs text-slate-500 dark:text-slate-400 truncate">{{ res.auction_title || 'Bilinmeyen Oturum' }}</span>
                            </div>
                         </div>

                         <div class="flex justify-end pt-2 border-t border-slate-100 dark:border-slate-800">
                            <button v-if="res.status !== 'CANCELLED' && res.status !== 'COMPLETED'" class="flex-1 bg-primary hover:bg-blue-600 text-white text-sm font-bold py-2.5 rounded-lg shadow-lg shadow-primary/20 active:scale-95 transition-all">
                                Girişi Onayla
                            </button>
                            <button v-else class="flex-1 border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 text-sm font-medium py-2.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
                                Detaylar
                            </button>
                         </div>
                    </div>
                </div>

                <!-- Desktop Table View -->
                <div class="overflow-x-auto hidden md:block">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-slate-50 dark:bg-background-dark/50 border-b border-slate-200 dark:border-slate-800">
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Rezervasyon Kodu</th>
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Misafir Adı</th>
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Oturum Adı</th>
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Giriş Durumu</th>
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">İşlem</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-200 dark:divide-slate-800">
                            
                            <tr v-if="loading" class="animate-pulse">
                                <td colspan="5" class="px-6 py-8 text-center text-slate-400">Yükleniyor...</td>
                            </tr>
                            
                            <tr v-else-if="filteredReservations.length === 0">
                                <td colspan="5" class="px-6 py-12 text-center flex flex-col items-center justify-center gap-2 text-slate-400">
                                    <span class="material-symbols-outlined text-4xl opacity-50">inbox</span>
                                    <p>Aramanızla eşleşen rezervasyon bulunamadı.</p>
                                </td>
                            </tr>

                            <tr v-for="res in filteredReservations" :key="res.id" class="group hover:bg-slate-50 dark:hover:bg-[#232d3f]/30 transition-colors">
                                <td class="px-6 py-5 whitespace-nowrap">
                                    <div class="text-lg font-bold text-slate-900 dark:text-white font-mono tracking-tight decoration-slate-400" :class="{'line-through opacity-50': res.status === 'CANCELLED'}">
                                        #{{ res.booking_code }}
                                    </div>
                                    <div class="text-xs text-slate-400">{{ formatDate(res.created_at) }}</div>
                                </td>
                                <td class="px-6 py-5 whitespace-nowrap">
                                    <div class="flex items-center gap-3">
                                        <div class="h-8 w-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-500">
                                            {{ (res.user_name || 'GK').substring(0,2).toUpperCase() }}
                                        </div>
                                        <div class="text-sm font-medium text-slate-900 dark:text-slate-200">{{ res.user_name || 'Misafir' }}</div>
                                    </div>
                                </td>
                                <td class="px-6 py-5 whitespace-nowrap">
                                    <div class="text-sm text-slate-600 dark:text-slate-300 font-medium">{{ res.auction_title || 'Bilinmeyen Oturum' }}</div>
                                    <div class="text-xs text-slate-400">Stüdyo A</div>
                                </td>
                                <td class="px-6 py-5 whitespace-nowrap">
                                    <span :class="getStatusConfig(res.status).class" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border border-transparent">
                                        <span :class="getStatusConfig(res.status).dot" class="w-1.5 h-1.5 rounded-full"></span>
                                        {{ getStatusConfig(res.status).label }}
                                    </span>
                                </td>
                                <td class="px-6 py-5 whitespace-nowrap text-right">
                                    <button v-if="res.status !== 'CANCELLED' && res.status !== 'COMPLETED'" class="inline-flex items-center justify-center px-4 py-2 bg-primary hover:bg-blue-600 text-white text-sm font-bold rounded-lg transition-all shadow-lg shadow-primary/20 hover:shadow-primary/40 active:scale-95">
                                        Girişi Onayla
                                    </button>
                                    <button v-else class="inline-flex items-center justify-center px-4 py-2 border border-slate-300 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 text-sm font-medium rounded-lg transition-all">
                                        Detaylar
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Use simple pagination for now (static as API doesn't fully support it yet in this view) -->
                <div class="flex items-center justify-between px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-background-dark/30">
                    <div class="text-sm text-slate-500 dark:text-slate-400">
                        Toplam <span class="font-medium text-slate-900 dark:text-white">{{ reservations.length }}</span> kayıttan <span class="font-medium text-slate-900 dark:text-white">1</span> - <span class="font-medium text-slate-900 dark:text-white">{{ filteredReservations.length }}</span> arası gösteriliyor
                    </div>
                    <div class="flex gap-2">
                        <button disabled class="px-3 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                            Önceki
                        </button>
                        <button disabled class="px-3 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                            Sonraki
                        </button>
                    </div>
                </div>
            </div>
        
        </div>
    </div>
  </div>
</template>
