<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminNotificationDropdown from '@/components/admin/AdminNotificationDropdown.vue'

import { useAdminReservations } from '@/composables/admin/useAdminReservations'
import { formatShortDate } from '@/utils/admin/formatters'
import { getReservationStatusMeta, RESERVATION_FILTERS } from '@/utils/admin/status_metadata'

const router = useRouter()

const {
    loading,
    error,
    searchQuery,
    statusFilter,
    showFilterDropdown,
    currentPage,
    paginatedReservations,
    filteredReservations,
    totalPages,
    shownStart,
    shownEnd,
    totalReservationsCount: totalReservations,
    pendingCheckInsCount: pendingCheckIns,
    checkedInTodayCount: checkedInToday,
    fetchReservations,
    goToPrevPage,
    goToNextPage,
    handleCheckIn,
    handleCancel
} = useAdminReservations()

const filterDropdownRef = ref(null)

const handleDocumentClick = (event) => {
    if (!showFilterDropdown.value) return
    if (filterDropdownRef.value && !filterDropdownRef.value.contains(event.target)) {
        showFilterDropdown.value = false
    }
}

onMounted(() => {
    document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
    document.removeEventListener('click', handleDocumentClick)
})
</script>

<template>
  <div class="flex flex-col h-full w-full bg-background-light dark:bg-background-dark overflow-hidden relative">
    
    <!-- Header -->
    <header class="sticky top-0 z-30 flex flex-col md:flex-row md:items-center justify-between px-4 py-3 md:px-8 md:py-5 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#111811]/80 backdrop-blur-md gap-4 overflow-visible">
        <div class="flex flex-col gap-1">
            <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">Rezervasyon Yönetimi</h2>
            <p class="text-slate-500 dark:text-slate-400 text-xs md:text-sm">Rezervasyonları yönet ve misafir girişlerini kontrol et.</p>
        </div>
        <div class="flex gap-3 w-full md:w-auto justify-end relative z-40 overflow-visible">
            <AdminNotificationDropdown />

            <button @click.prevent="router.push({ name: 'admin-auction-create' })" class="flex items-center gap-2 bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg shadow-primary/25 transition-all active:scale-95 text-sm">
                <span class="material-symbols-outlined" style="font-size: 18px;">add</span>
                <span class="font-medium">Oturum Oluştur</span>
            </button>
        </div>
    </header>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto p-4 md:p-8">
        <div class="flex flex-col gap-6">
            
            <!-- Toolbar moved into table container below -->

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
                <!-- Toolbar: Search, Filters and Refresh (placed directly above the list) -->
                <div class="flex flex-wrap items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800 gap-4">
                    <div class="relative w-full md:max-w-2xl">
                        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <span class="material-symbols-outlined text-slate-400 dark:text-slate-500">search</span>
                        </div>
                        <input
                            v-model="searchQuery"
                            class="w-full pl-10 pr-4 py-2 rounded-lg bg-white dark:bg-[#1a2230] border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary placeholder-slate-400 dark:placeholder-slate-600 text-sm"
                            placeholder="Rezervasyon Kodu, Misafir Adı veya Stüdyo ara..."
                            type="text"
                        />
                    </div>

                    <div class="flex items-center gap-3 md:gap-4">
                        <div ref="filterDropdownRef" class="relative z-50" @click.stop>
                            <button @click.stop="showFilterDropdown = !showFilterDropdown" class="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors">
                                <span class="material-symbols-outlined" style="font-size: 18px;">filter_list</span>
                                {{ RESERVATION_FILTERS[statusFilter] || statusFilter }}
                            </button>
                            <div v-if="showFilterDropdown" class="absolute top-full right-0 mt-2 w-48 bg-white dark:bg-[#1a2230] rounded-lg shadow-xl border border-slate-200 dark:border-slate-800 z-[70] py-1 pointer-events-auto">
                                <button @click="statusFilter = 'ALL'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Tümü</button>
                                <button @click="statusFilter = 'PENDING_ON_SITE'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Bekliyor</button>
                                <button @click="statusFilter = 'NO_SHOW'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Katılmadı</button>
                                <button @click="statusFilter = 'CONFIRMED'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Onaylandı</button>
                                <button @click="statusFilter = 'COMPLETED'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Giriş Yapıldı</button>
                                <button @click="statusFilter = 'CHECKED_IN'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">Check-in</button>
                                <button @click="statusFilter = 'CANCELLED'; showFilterDropdown = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]">İptal</button>
                            </div>
                        </div>

                        <button @click="fetchReservations" class="bg-primary hover:bg-blue-600 text-white px-3 py-2 md:px-4 md:py-2 rounded-lg transition-colors text-sm font-bold shadow-lg shadow-primary/25 active:scale-95 flex items-center">
                            <span class="material-symbols-outlined align-middle mr-1 text-[18px] md:text-[20px]">autorenew</span> Yenile
                        </button>
                    </div>
                </div>
                
                <!-- Mobile List View -->
                <div class="md:hidden flex flex-col divide-y divide-slate-200 dark:divide-slate-800">
                    <div v-if="loading" class="p-6 text-center text-slate-400 animate-pulse">Yükleniyor...</div>
                    <div v-else-if="paginatedReservations.length === 0" class="p-8 text-center text-slate-500 dark:text-slate-400 flex flex-col items-center gap-2">
                        <span class="material-symbols-outlined text-4xl opacity-50">inbox</span>
                        <p>Kayıt bulunamadı.</p>
                    </div>
                    <div v-else v-for="res in paginatedReservations" :key="'mobile-'+res.id" class="p-4 flex flex-col gap-4 bg-white dark:bg-[#1a2230]">
                         <div class="flex justify-between items-start">
                             <div>
                                 <div class="font-mono font-bold text-lg text-slate-900 dark:text-white" :class="{'line-through opacity-50': res.status === 'CANCELLED'}">
                                     #{{ res.booking_code }}
                                 </div>
                                 <div class="text-xs text-slate-400 mt-1">{{ formatShortDate(res.created_at) }}</div>
                             </div>
                             <span :class="getReservationStatusMeta(res.status).class" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium border border-transparent">
                                <span :class="getReservationStatusMeta(res.status).dot" class="w-1.5 h-1.5 rounded-full"></span>
                                {{ getReservationStatusMeta(res.status).label }}
                            </span>
                         </div>
                         
                            <div class="flex items-center gap-3 bg-slate-50 dark:bg-[#232d3f]/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800">
                            <div class="h-10 w-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-500 shrink-0">
                                {{ (res.user_name || 'GK').substring(0,2).toUpperCase() }}
                            </div>
                            <div class="flex flex-col min-w-0">
                                <span class="text-sm font-medium text-slate-900 dark:text-white truncate">{{ res.user_name || 'Misafir' }}</span>
                                <span class="text-xs text-slate-500 dark:text-slate-400 truncate">{{ res.auction_title || 'Bilinmeyen Oturum' }}</span>
                                <span class="text-xs text-slate-400 mt-1">Hizmet: {{ res.scheduled_at ? formatShortDate(res.scheduled_at) : '-' }}</span>
                            </div>
                         </div>

                         <div class="flex justify-end pt-2 border-t border-slate-100 dark:border-slate-800 gap-2">
                            <template v-if="res.status === 'PENDING_ON_SITE'">
                                <button @click="handleCancel(res.id)" class="flex-1 border border-red-200 dark:border-red-900/30 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/10 hover:bg-red-100 dark:hover:bg-red-900/20 text-sm font-medium py-2.5 rounded-lg transition-all">
                                    İptal Et
                                </button>
                                <button @click="handleCheckIn(res.id)" class="flex-1 bg-primary hover:bg-blue-600 text-white text-sm font-bold py-2.5 rounded-lg shadow-lg shadow-primary/20 active:scale-95 transition-all">
                                    Girişi Onayla
                                </button>
                            </template>
                            <button @click="router.push({ name: 'admin-reservation-detail', params: { id: res.id } })" class="flex-1 border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 text-sm font-medium py-2.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
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
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Hizmet Zamanı</th>
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Giriş Durumu</th>
                                <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">İşlem</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-200 dark:divide-slate-800">
                            
                            <tr v-if="loading" class="animate-pulse">
                                <td colspan="6" class="px-6 py-8 text-center text-slate-400">Yükleniyor...</td>
                            </tr>
                            
                            <tr v-else-if="paginatedReservations.length === 0">
                                <td colspan="6" class="px-6 py-12 text-center flex flex-col items-center justify-center gap-2 text-slate-400">
                                    <span class="material-symbols-outlined text-4xl opacity-50">inbox</span>
                                    <p>Aramanızla eşleşen rezervasyon bulunamadı.</p>
                                </td>
                            </tr>

                            <tr v-for="res in paginatedReservations" :key="res.id" class="group hover:bg-slate-50 dark:hover:bg-[#232d3f]/30 transition-colors">
                                <td class="px-6 py-5 whitespace-nowrap">
                                    <div class="text-lg font-bold text-slate-900 dark:text-white font-mono tracking-tight decoration-slate-400" :class="{'line-through opacity-50': res.status === 'CANCELLED'}">
                                        #{{ res.booking_code }}
                                    </div>
                                    <div class="text-xs text-slate-400">{{ formatShortDate(res.created_at) }}</div>
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
                                    <div class="text-sm text-slate-600 dark:text-slate-300 font-medium">{{ res.scheduled_at ? formatShortDate(res.scheduled_at) : '-' }}</div>
                                    <div class="text-xs text-slate-400">{{ res.scheduled_at ? new Date(res.scheduled_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '' }}</div>
                                </td>
                                <td class="px-6 py-5 whitespace-nowrap">
                                    <span :class="getReservationStatusMeta(res.status).class" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border border-transparent">
                                        <span :class="getReservationStatusMeta(res.status).dot" class="w-1.5 h-1.5 rounded-full"></span>
                                        {{ getReservationStatusMeta(res.status).label }}
                                    </span>
                                </td>
                                <td class="px-6 py-5 whitespace-nowrap text-right">
                                    <div class="flex items-center justify-end gap-2">
                                        <template v-if="res.status === 'PENDING_ON_SITE'">
                                        <button @click="handleCancel(res.id)" class="inline-flex items-center justify-center px-4 py-2 border border-red-200 dark:border-red-900/30 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/10 hover:bg-red-100 dark:hover:bg-red-900/20 text-sm font-medium rounded-lg transition-all">
                                            İptal
                                        </button>
                                        <button @click="handleCheckIn(res.id)" class="inline-flex items-center justify-center px-4 py-2 bg-primary hover:bg-blue-600 text-white text-sm font-bold rounded-lg transition-all shadow-lg shadow-primary/20 hover:shadow-primary/40 active:scale-95">
                                            Onayla
                                        </button>
                                        </template>
                                        <button @click="router.push({ name: 'admin-reservation-detail', params: { id: res.id } })" class="inline-flex items-center justify-center px-4 py-2 border border-slate-300 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 text-sm font-medium rounded-lg transition-all">
                                            Detaylar
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Use simple pagination for now (static as API doesn't fully support it yet in this view) -->
                <div class="flex items-center justify-between px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-background-dark/30">
                    <div class="text-sm text-slate-500 dark:text-slate-400">
                        Toplam <span class="font-medium text-slate-900 dark:text-white">{{ filteredReservations.length }}</span> kayıttan <span class="font-medium text-slate-900 dark:text-white">{{ shownStart }}</span> - <span class="font-medium text-slate-900 dark:text-white">{{ shownEnd }}</span> arası gösteriliyor
                    </div>
                    <div class="flex gap-2">
                        <button @click="goToPrevPage" :disabled="currentPage === 1" class="px-3 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                            Önceki
                        </button>
                        <button @click="goToNextPage" :disabled="currentPage === totalPages" class="px-3 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                            Sonraki
                        </button>
                    </div>
                </div>
            </div>
        
        </div>
    </div>
  </div>
</template>
