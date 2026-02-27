<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue' 
import { useRoute, useRouter } from 'vue-router'
import { useAuctionStore } from '@/stores/auction'
import CountDownTimer from '@/components/CountDownTimer.vue'

const route = useRoute()
const router = useRouter()
const store = useAuctionStore()

const auction = computed(() => store.currentAuction)
const loading = ref(true)
const error = ref(null)

const activeTab = ref('overview') // overview, reservations, bidders

const formatCurrency = (val) => {
    if (val === undefined || val === null) return '₺0.00'
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(val)
}

const formatDate = (value) => {
    if (!value) return '-'
    return new Date(value).toLocaleString('tr-TR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

onMounted(async () => {
    const id = route.params.id
    if (id) {
        try {
            await store.fetchAuctionById(id)
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }
})

</script>

<template>
    <div class="flex flex-col h-full w-full bg-background-light dark:bg-background-dark overflow-hidden relative">
        <!-- Header -->
        <header class="sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between px-4 py-3 md:px-8 md:py-5 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#111811]/80 backdrop-blur-md gap-4">
            <div class="flex items-center gap-4">
                <button @click="router.back()" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                    <span class="material-symbols-outlined">arrow_back</span>
                </button>
                <div class="flex flex-col gap-1">
                    <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">Oturum Detayı</h2>
                    <p class="text-slate-500 dark:text-slate-400 text-xs md:text-sm">#{{ auction?.id }} - {{ auction?.title }}</p>
                </div>
            </div>
             <div class="flex gap-3 w-full md:w-auto justify-end">
                <button @click="router.push({ name: 'admin-auction-edit', params: { id: auction?.id } })" class="bg-primary hover:bg-blue-600 text-white px-3 py-2 md:px-4 md:py-2 rounded-lg transition-colors text-sm font-bold shadow-lg shadow-primary/25 active:scale-95 flex items-center">
                    <span class="material-symbols-outlined align-middle mr-1 text-[18px] md:text-[20px]">edit</span> Düzenle
                </button>
            </div>
        </header>

         <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 md:p-8">
            <div v-if="loading" class="flex items-center justify-center h-64">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
            
            <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-900/30">
                {{ error }}
            </div>

            <div v-else-if="!auction" class="p-6 text-center text-slate-500 dark:text-slate-400">
                Oturum bulunamadı veya silinmiş.
            </div>

            <div v-else class="flex flex-col gap-6">
                <!-- Info Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-white dark:bg-[#1a2230] p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                        <span class="text-xs text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider">Durum</span>
                         <div class="mt-2">
                            <span v-if="auction?.status === 'ACTIVE'" class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-primary/10 text-primary border border-primary/20">AKTİF</span>
                            <span v-else-if="auction?.status === 'SOLD'" class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-[#0bda5e]/10 text-[#0bda5e] border border-[#0bda5e]/20">SATILDI</span>
                            <span v-else class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700">{{ auction?.status }}</span>
                        </div>
                    </div>
                     <div class="bg-white dark:bg-[#1a2230] p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                        <span class="text-xs text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider">Güncel Fiyat</span>
                        <div class="mt-2 text-xl font-bold text-slate-900 dark:text-white">{{ formatCurrency(auction?.currentPrice || auction?.current_price) }}</div>
                    </div>
                     <div class="bg-white dark:bg-[#1a2230] p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                        <span class="text-xs text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider">Başlangıç Fiyatı</span>
                        <div class="mt-2 text-xl font-bold text-slate-900 dark:text-white">{{ formatCurrency(auction?.startPrice || auction?.start_price) }}</div>
                    </div>
                     <div class="bg-white dark:bg-[#1a2230] p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                        <span class="text-xs text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider">Kalan Süre</span>
                         <div class="mt-2 text-lg font-mono text-primary font-bold">
                            <CountDownTimer v-if="auction?.status === 'ACTIVE'" :targetTime="auction?.endTime || auction?.end_time" :showLabel="false" :small="true" />
                            <span v-else>-</span>
                        </div>
                    </div>
                </div>

                <!-- Tabs -->
                <div class="border-b border-slate-200 dark:border-slate-800">
                    <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                        <button @click="activeTab = 'overview'" :class="[activeTab === 'overview' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
                            Genel Bakış
                        </button>
                        <button @click="activeTab = 'reservations'" :class="[activeTab === 'reservations' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
                            Rezervasyonlar & Kazanan
                        </button>
                    </nav>
                </div>

                <!-- Tab Content -->
                <div v-if="activeTab === 'overview'" class="bg-white dark:bg-[#1a2230] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                    <h3 class="text-lg font-medium text-slate-900 dark:text-white mb-4">Açıklama</h3>
                    <p class="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">{{ auction?.description || 'Açıklama yok.' }}</p>
                    
                    <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                             <h4 class="text-sm font-medium text-slate-900 dark:text-white mb-2">Zamanlama</h4>
                             <ul class="text-sm text-slate-600 dark:text-slate-400 space-y-2">
                                <li class="flex justify-between">
                                    <span>Başlangıç:</span>
                                    <span class="font-medium text-slate-900 dark:text-white">{{ formatDate(auction?.startTime || auction?.start_time) }}</span>
                                </li>
                                <li class="flex justify-between">
                                    <span>Bitiş:</span>
                                    <span class="font-medium text-slate-900 dark:text-white">{{ formatDate(auction?.endTime || auction?.end_time) }}</span>
                                </li>
                             </ul>
                        </div>
                         <div>
                             <h4 class="text-sm font-medium text-slate-900 dark:text-white mb-2">Fiyatlandırma Kuralları</h4>
                             <ul class="text-sm text-slate-600 dark:text-slate-400 space-y-2">
                                <li class="flex justify-between">
                                    <span>Taban Fiyat:</span>
                                    <span class="font-medium text-slate-900 dark:text-white">{{ formatCurrency(auction?.floorPrice || auction?.floor_price) }}</span>
                                </li>
                                <li class="flex justify-between">
                                    <span>Düşüş Aralığı:</span>
                                    <span class="font-medium text-slate-900 dark:text-white">{{ auction?.dropIntervalMins || auction?.drop_interval_mins }} dk</span>
                                </li>
                                <li class="flex justify-between">
                                    <span>Düşüş Miktarı:</span>
                                    <span class="font-medium text-slate-900 dark:text-white">{{ formatCurrency(auction?.dropAmount || auction?.drop_amount) }}</span>
                                </li>
                             </ul>
                        </div>
                    </div>

                    <div class="mt-6 border border-slate-200 dark:border-slate-800 rounded-xl p-4 bg-slate-50/70 dark:bg-[#111811]/50">
                        <h4 class="text-sm font-medium text-slate-900 dark:text-white mb-3">Turbo Mod</h4>
                        <ul class="text-sm text-slate-600 dark:text-slate-400 space-y-2">
                            <li class="flex justify-between">
                                <span>Durum:</span>
                                <span v-if="auction?.turboEnabled || auction?.turbo_enabled" class="font-medium text-primary">Aktif</span>
                                <span v-else class="font-medium text-slate-500">Kapalı</span>
                            </li>
                            <li v-if="auction?.turboEnabled || auction?.turbo_enabled" class="flex justify-between">
                                <span>Tetikleyici:</span>
                                <span class="font-medium text-slate-900 dark:text-white">{{ auction?.turboTriggerMins || auction?.turbo_trigger_mins || '-' }} dk</span>
                            </li>
                            <li v-if="auction?.turboEnabled || auction?.turbo_enabled" class="flex justify-between">
                                <span>Turbo Aralığı:</span>
                                <span class="font-medium text-slate-900 dark:text-white">{{ auction?.turboIntervalMins || auction?.turbo_interval_mins || '-' }} dk</span>
                            </li>
                            <li v-if="auction?.turboEnabled || auction?.turbo_enabled" class="flex justify-between">
                                <span>Turbo Düşüş Miktarı:</span>
                                <span class="font-medium text-slate-900 dark:text-white">{{ formatCurrency(auction?.turboDropAmount || auction?.turbo_drop_amount) }}</span>
                            </li>
                            <li v-if="auction?.turboEnabled || auction?.turbo_enabled" class="flex justify-between">
                                <span>Turbo Başlangıç:</span>
                                <span class="font-medium text-slate-900 dark:text-white">{{ formatDate(auction?.turboStartedAt || auction?.turbo_started_at) }}</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div v-if="activeTab === 'reservations'" class="bg-white dark:bg-[#1a2230] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm text-center py-12">
                   <span class="material-symbols-outlined text-4xl text-slate-300 dark:text-slate-600 mb-2">event_busy</span>
                   <p class="text-slate-500 dark:text-slate-400">Henüz rezervasyon kaydı bulunmamaktadır.</p>
                </div>

            </div>
        </div>
    </div>
</template>