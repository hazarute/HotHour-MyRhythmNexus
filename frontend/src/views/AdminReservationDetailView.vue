<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const reservation = ref(null)
const loading = ref(true)
const error = ref(null)

const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Fetch reservation details
const fetchReservation = async () => {
    loading.value = true
    error.value = null
    const id = route.params.id
    try {
        const response = await fetch(`${baseUrl}/api/v1/reservations/admin/${id}`, {
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })
        
        if (!response.ok) {
            throw new Error('Rezervasyon detayları getirilemedi')
        }
        
        reservation.value = await response.json()
    } catch (err) {
        console.error(err)
        error.value = err.message
    } finally {
        loading.value = false
    }
}

const formatDate = (value) => {
    if (!value) return '-'
    return new Date(value).toLocaleString('tr-TR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const getStatusConfig = (status) => {
    switch(status) {
        case 'COMPLETED':
        case 'CHECKED_IN':
            return { label: 'Giriş Yapıldı', class: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300', dot: 'bg-green-500' }
        case 'PENDING_ON_SITE':
        case 'CONFIRMED':
            return { label: 'Bekliyor', class: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300', dot: 'bg-amber-500' }
        case 'CANCELLED':
            return { label: 'İptal Edildi', class: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300', dot: 'bg-red-500' }
        default:
            return { label: status, class: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300', dot: 'bg-slate-500' }
    }
}

const handleCheckIn = async () => {
    if (!confirm('Bu rezervasyonu onaylamak istiyor musunuz?')) return
    const id = reservation.value.id
    try {
        const response = await fetch(`${baseUrl}/api/v1/reservations/admin/${id}/check-in`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })

        if (!response.ok) throw new Error('İşlem başarısız')
        
        await fetchReservation() // Refresh data
        alert('Giriş işlemi başarılı!')
    } catch (err) {
        alert('Hata: ' + err.message)
    }
}

const handleCancel = async () => {
    if (!confirm('Bu rezervasyonu iptal etmek istiyor musunuz?')) return
    const id = reservation.value.id
    try {
        const response = await fetch(`${baseUrl}/api/v1/reservations/admin/${id}/cancel`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })

        if (!response.ok) throw new Error('İşlem başarısız')
        
        await fetchReservation() // Refresh data
        alert('Rezervasyon iptal edildi.')
    } catch (err) {
        alert('Hata: ' + err.message)
    }
}

onMounted(() => {
    fetchReservation()
})
</script>

<template>
  <div class="flex flex-col h-full w-full bg-background-light dark:bg-background-dark overflow-hidden relative">
    
    <!-- Header -->
    <header class="sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between px-4 py-3 md:px-8 md:py-5 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#111811]/80 backdrop-blur-md gap-4">
        <div class="flex items-center gap-4">
            <button @click="router.back()" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <span class="material-symbols-outlined text-slate-600 dark:text-slate-400">arrow_back</span>
            </button>
            <div class="flex flex-col gap-1">
                <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    Rezervasyon Detayı
                    <span v-if="reservation" class="font-mono text-lg opacity-60">#{{ reservation.booking_code }}</span>
                </h2>
            </div>
        </div>
        
        <div class="flex gap-3 w-full md:w-auto justify-end" v-if="reservation && reservation.status !== 'CANCELLED' && reservation.status !== 'COMPLETED'">
            <button @click="handleCancel" class="bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 text-red-600 dark:text-red-400 px-4 py-2 rounded-lg transition-colors text-sm font-medium border border-red-200 dark:border-red-900/30">
                İptal Et
            </button>
            <button @click="handleCheckIn" class="bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors text-sm font-bold shadow-lg shadow-primary/25 active:scale-95 flex items-center">
                <span class="material-symbols-outlined align-middle mr-1 text-[20px]">check_circle</span> Girişi Onayla
            </button>
        </div>
    </header>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto p-4 md:p-8">
        
        <div v-if="loading" class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>

        <div v-else-if="error" class="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-200 dark:border-red-900/30 text-red-600 dark:text-red-400">
            <span class="material-symbols-outlined text-4xl mb-2">error</span>
            <p>{{ error }}</p>
            <button @click="fetchReservation" class="mt-4 text-sm underline hover:no-underline">Tekrar Dene</button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            
            <!-- Status Card -->
            <div class="bg-white dark:bg-[#1a2230] p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center text-center gap-4 md:col-span-1">
                <div class="w-20 h-20 rounded-full flex items-center justify-center bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                    <span class="material-symbols-outlined text-4xl text-primary">confirmation_number</span>
                </div>
                <div>
                   <p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Durum</p>
                   <span :class="getStatusConfig(reservation.status).class" class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold border border-transparent">
                        <span :class="getStatusConfig(reservation.status).dot" class="w-2 h-2 rounded-full"></span>
                        {{ getStatusConfig(reservation.status).label }}
                    </span>
                </div>
                <div class="mt-2 pt-4 w-full border-t border-slate-100 dark:border-slate-800">
                     <p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Kilitlenen Fiyat</p>
                     <div class="text-3xl font-bold text-slate-900 dark:text-white font-mono">
                        ₺{{ parseFloat(reservation.locked_price).toFixed(2) }}
                     </div>
                </div>
                <div class="w-full text-xs text-slate-400 mt-1">
                    Rezervasyon: {{ formatDate(reservation.reserved_at) }}
                </div>
            </div>

            <!-- User Info Card -->
            <div class="bg-white dark:bg-[#1a2230] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden md:col-span-1">
                <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex justify-between items-center">
                    <h3 class="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span class="material-symbols-outlined text-blue-500">person</span>
                        Misafir Bilgileri
                    </h3>
                </div>
                <div class="p-6 flex flex-col gap-4">
                    <div class="flex items-center gap-4">
                        <div class="h-12 w-12 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-lg font-bold text-slate-500">
                            {{ (reservation.user.full_name || 'GK').substring(0,2).toUpperCase() }}
                        </div>
                        <div>
                            <div class="font-medium text-slate-900 dark:text-white">{{ reservation.user.full_name }}</div>
                            <div class="text-sm text-slate-500 dark:text-slate-400">ID: #{{ reservation.user.id }}</div>
                        </div>
                    </div>
                    
                    <div class="space-y-3 mt-2">
                        <div class="flex items-start gap-3">
                            <span class="material-symbols-outlined text-slate-400 text-sm mt-0.5">mail</span>
                            <div>
                                <div class="text-xs text-slate-500 dark:text-slate-400">E-Posta</div>
                                <div class="text-sm font-medium text-slate-700 dark:text-slate-200 break-all">{{ reservation.user.email }}</div>
                            </div>
                        </div>
                        <div class="flex items-start gap-3">
                            <span class="material-symbols-outlined text-slate-400 text-sm mt-0.5">call</span>
                            <div>
                                <div class="text-xs text-slate-500 dark:text-slate-400">Telefon</div>
                                <div class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ reservation.user.phone || '-' }}</div>
                            </div>
                        </div>
                        <div class="flex items-start gap-3">
                            <span class="material-symbols-outlined text-slate-400 text-sm mt-0.5">verified</span>
                            <div>
                                <div class="text-xs text-slate-500 dark:text-slate-400">Hesap Onayı</div>
                                <div class="text-sm font-medium" :class="reservation.user.is_verified ? 'text-green-600' : 'text-orange-500'">
                                    {{ reservation.user.is_verified ? 'Onaylı Hesap' : 'Onaylanmamış' }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Auction Info Card -->
            <div class="bg-white dark:bg-[#1a2230] rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden md:col-span-1">
                <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex justify-between items-center">
                    <h3 class="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <span class="material-symbols-outlined text-purple-500">event</span>
                        Oturum Bilgileri
                    </h3>
                </div>
                <div class="p-6 flex flex-col gap-4">
                     <div>
                        <div class="text-xs text-slate-500 dark:text-slate-400 mb-1">Oturum Başlığı</div>
                        <div class="font-medium text-lg text-slate-900 dark:text-white mb-1">{{ reservation.auction.title }}</div>
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold border"
                            :class="reservation.auction.status === 'ACTIVE' ? 'bg-green-100 text-green-800 border-green-200' : 'bg-slate-100 text-slate-600 border-slate-200'">
                            {{ reservation.auction.status }}
                        </span>
                     </div>
                     
                     <div class="space-y-4 mt-2">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <div class="text-xs text-slate-500 dark:text-slate-400 mb-1">Başlangıç</div>
                                <div class="text-sm font-medium text-slate-700 dark:text-slate-200">
                                    {{ formatDate(reservation.auction.start_time) }}
                                </div>
                            </div>
                            <div>
                                <div class="text-xs text-slate-500 dark:text-slate-400 mb-1">Bitiş</div>
                                <div class="text-sm font-medium text-slate-700 dark:text-slate-200">
                                    {{ formatDate(reservation.auction.end_time) }}
                                </div>
                            </div>
                        </div>

                         <div class="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                            Stüdyo A - Premium ses ekipmanları ve profesyonel kayıt ortamı. Rezervasyon saatinde stüdyoda hazır bulunulması gerekmektedir.
                        </div>
                     </div>
                </div>
            </div>

        </div>
    </div>
  </div>
</template>
