<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const reservations = ref([])
const loading = ref(false)
const error = ref(null)

const getStatusConfig = (status) => {
    const configs = {
        'PENDING_ON_SITE': { label: 'Ödeme Bekleniyor', color: 'text-neon-green', border: 'border-neon-green/50', bg: 'bg-neon-green/10', glow: 'shadow-[0_0_15px_rgba(54,211,153,0.15)]' },
        'COMPLETED': { label: 'Tamamlandı', color: 'text-slate-400', border: 'border-slate-700', bg: 'bg-slate-800/50', glow: '' },
        'CHECKED_IN': { label: 'Giriş Yapıldı', color: 'text-neon-blue', border: 'border-neon-blue/50', bg: 'bg-neon-blue/10', glow: '' },
        'CANCELLED': { label: 'İptal Edildi', color: 'text-red-400', border: 'border-red-900/50', bg: 'bg-red-900/10', glow: '' },
        'NO_SHOW': { label: 'Katılmadı', color: 'text-orange-400', border: 'border-orange-900/50', bg: 'bg-orange-900/10', glow: '' }
    }
    return configs[status] || { label: status || 'Bilinmiyor', color: 'text-slate-400', border: 'border-slate-700', bg: 'bg-slate-800/50', glow: '' }
}

const isCompleted = (status) => {
    return ['COMPLETED', 'NO_SHOW', 'CANCELLED'].includes(status)
}

const fetchMyReservations = async () => {
    loading.value = true
    error.value = null
    try {
        if (!authStore.token) {
            router.push('/login')
            return
        }

        const baseUrl = import.meta.env.VITE_API_URL || ''
        const response = await fetch(`${baseUrl}/api/v1/reservations/my/all`, {
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })
        
        if (!response.ok) {
            if (response.status === 401) {
                authStore.logout()
                router.push('/login')
                return
            }
            throw new Error('Rezervasyonlar getirilemedi. Lütfen bağlantınızı kontrol edin.')
        }
        
        const data = await response.json()
        reservations.value = data.reservations 
    } catch (err) {
        console.error(err)
        error.value = err.message
    } finally {
        loading.value = false
    }
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('tr-TR', {
        weekday: 'short', month: 'short', day: 'numeric'
    })
}

const formatTime = (dateStr) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleTimeString('tr-TR', {
        hour: '2-digit', minute:'2-digit'
    })
}

const formatCurrency = (amount) => {
    return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 0 }).format(amount)
}

onMounted(() => {
    fetchMyReservations()
})
</script>

<template>
    <div class="w-full min-h-screen bg-background-dark font-sans text-slate-200">
        <header class="relative px-6 py-12 overflow-hidden border-b border-white/5">
            <div class="absolute inset-0 bg-gradient-to-br from-neon-blue/5 to-transparent pointer-events-none"></div>
            <div class="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-end gap-6 relative z-10">
                <div>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neon-blue mb-4">
                        <span class="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
                        Profilim
                    </div>
                    <h1 class="text-4xl md:text-5xl font-black text-white tracking-tight">Dijital Biletlerim</h1>
                    <p class="text-slate-400 mt-2 max-w-lg">Stüdyoda göstermek üzere kilitlediğin fırsatlar ve geçmiş Pilates seansların.</p>
                </div>
                <button @click="router.push('/')" class="group flex items-center gap-2 text-sm font-bold text-slate-400 hover:text-white transition-colors">
                    <span class="material-symbols-outlined transform group-hover:-translate-x-1 transition-transform">arrow_back</span>
                    Arenaya Dön
                </button>
            </div>
        </header>

        <main class="max-w-5xl mx-auto px-6 py-10">
            <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4">
                <div class="w-12 h-12 border-4 border-slate-800 border-t-neon-blue rounded-full animate-spin"></div>
                <p class="text-slate-500 animate-pulse">Biletleriniz şifreleniyor...</p>
            </div>
            
            <div v-else-if="error" class="bg-red-950/30 border border-red-900/50 rounded-xl p-6 text-center max-w-lg mx-auto backdrop-blur-sm">
                <span class="material-symbols-outlined text-red-500 text-4xl mb-2">error</span>
                <p class="text-red-200 mb-4">{{ error }}</p>
                <button @click="fetchMyReservations" class="px-6 py-2 bg-red-900/50 hover:bg-red-800/50 text-white rounded-lg transition-colors border border-red-700/50 text-sm font-bold">
                    Tekrar Dene
                </button>
            </div>

            <div v-else-if="reservations.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
                <div class="w-24 h-24 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-slate-800">
                    <span class="material-symbols-outlined text-5xl text-slate-700">local_activity</span>
                </div>
                <h2 class="text-2xl font-bold text-white mb-2">Henüz Bir Fırsat Yakalamadın</h2>
                <p class="text-slate-400 mb-8 max-w-md">Hollanda açık artırması devam ediyor. Fiyatlar düşerken ilk kapan sen ol ve dijital biletini oluştur.</p>
                <button @click="router.push('/')" class="px-8 py-4 bg-neon-blue hover:bg-blue-500 text-black font-black rounded-xl transition-all shadow-[0_0_20px_rgba(0,191,255,0.3)] hover:shadow-[0_0_30px_rgba(0,191,255,0.5)] hover:scale-105">
                    Canlı Seanslara Git
                </button>
            </div>

            <div v-else class="space-y-6">
                <div v-for="res in reservations" :key="res.id" 
                     class="relative flex flex-col md:flex-row bg-slate-900/40 rounded-2xl border backdrop-blur-md overflow-hidden transition-all duration-300 group"
                     :class="[getStatusConfig(res.status).border, getStatusConfig(res.status).glow, isCompleted(res.status) ? 'opacity-70 grayscale-[30%]' : 'hover:-translate-y-1']">
                    
                    <div class="flex-1 p-6 md:p-8 flex flex-col justify-between relative">
                        <div class="flex justify-between items-start mb-6">
                            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md border text-xs font-bold uppercase tracking-wider"
                                 :class="[getStatusConfig(res.status).bg, getStatusConfig(res.status).color, getStatusConfig(res.status).border]">
                                <span v-if="res.status === 'PENDING_ON_SITE'" class="w-1.5 h-1.5 rounded-full bg-neon-green animate-pulse"></span>
                                {{ getStatusConfig(res.status).label }}
                            </div>
                            <div class="text-right">
                                <p class="text-xs text-slate-500 uppercase tracking-wider mb-0.5">Seans Zamanı</p>
                                <p class="text-lg font-bold text-white">{{ formatDate(res.scheduled_at || res.auction_start_time) }}</p>
                                <p class="text-neon-blue font-mono">{{ formatTime(res.scheduled_at || res.auction_start_time) }}</p>
                            </div>
                        </div>

                        <div class="mb-6">
                            <h3 class="text-2xl md:text-3xl font-black text-white mb-2">{{ res.auction_title || 'Özel Pilates Seansı' }}</h3>
                            <p v-if="res.auction_description" class="text-slate-400 text-sm line-clamp-2 max-w-xl">{{ res.auction_description }}</p>
                        </div>

                        <div class="flex items-center gap-4 text-xs text-slate-500 mt-auto border-t border-white/5 pt-4">
                            <div class="flex items-center gap-1">
                                <span class="material-symbols-outlined text-[16px]">shopping_cart_checkout</span>
                                Alım: {{ formatDate(res.reserved_at) }} - {{ formatTime(res.reserved_at) }}
                            </div>
                        </div>
                    </div>

                    <div class="hidden md:flex flex-col items-center justify-between relative w-0">
                        <div class="absolute -top-3 -left-3 w-6 h-6 bg-background-dark rounded-full border-b border-r border-slate-800" :class="getStatusConfig(res.status).border"></div>
                        <div class="h-full border-l-2 border-dashed border-slate-700/50 absolute left-0"></div>
                        <div class="absolute -bottom-3 -left-3 w-6 h-6 bg-background-dark rounded-full border-t border-r border-slate-800" :class="getStatusConfig(res.status).border"></div>
                    </div>
                    
                    <div class="md:hidden w-full h-0 border-t-2 border-dashed border-slate-700/50 relative">
                        <div class="absolute -left-3 -top-3 w-6 h-6 bg-background-dark rounded-full border-r border-b border-slate-800" :class="getStatusConfig(res.status).border"></div>
                        <div class="absolute -right-3 -top-3 w-6 h-6 bg-background-dark rounded-full border-l border-b border-slate-800" :class="getStatusConfig(res.status).border"></div>
                    </div>

                    <div class="w-full md:w-72 bg-black/40 p-6 md:p-8 flex flex-col items-center justify-center text-center relative overflow-hidden group-hover:bg-black/60 transition-colors">
                        <div class="absolute inset-0 opacity-[0.03]" style="background-image: radial-gradient(#fff 1px, transparent 1px); background-size: 16px 16px;"></div>
                        
                        <div class="relative z-10 w-full">
                            <p class="text-xs text-slate-500 uppercase tracking-widest mb-1">Kilitlenen Fiyat</p>
                            <p class="text-3xl font-black mb-6" :class="isCompleted(res.status) ? 'text-slate-400' : 'text-white'">
                                {{ formatCurrency(res.locked_price) }}
                            </p>

                            <div class="w-full h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent mb-6"></div>

                            <p class="text-xs text-slate-500 uppercase tracking-widest mb-2">Giriş Kodunuz</p>
                            <div class="bg-black/50 border border-white/10 rounded-lg p-4 mb-3">
                                <p class="text-3xl md:text-4xl font-mono font-black tracking-widest" 
                                   :class="isCompleted(res.status) ? 'text-slate-600 line-through decoration-slate-600/50' : 'text-neon-green drop-shadow-[0_0_8px_rgba(54,211,153,0.8)]'">
                                    {{ res.booking_code }}
                                </p>
                            </div>
                            
                            <p class="text-[11px] text-slate-400 leading-tight">
                                <span v-if="res.status === 'PENDING_ON_SITE'">Ödemenizi yapmak ve seansa katılmak için bu kodu stüdyo resepsiyonuna gösterin.</span>
                                <span v-else>Bu biletin geçerliliği sona ermiştir.</span>
                            </p>
                        </div>
                    </div>

                </div>
            </div>
        </main>
    </div>
</template>

<style scoped>
/* Opsiyonel: Bilet kenarlarındaki yuvarlak kesikleri daha yumuşak yapmak için */
.bg-background-dark {
    background-color: #050505; /* Projenin ana arka plan rengine göre ayarla */
}
</style>