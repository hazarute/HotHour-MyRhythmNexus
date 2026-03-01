<script setup>
import { onMounted } from 'vue'
import { useReservations } from '../composables/useReservations'
import { formatDate, formatTime, formatCurrency } from '../utils/formatters'
import { getStatusConfig, isCompletedStatus, isCopyAllowedStatus } from '../utils/reservationStatus'

const {
    reservations,
    loading,
    error,
    copiedReservationId,
    cancellingReservationId,
    confirmCancelReservationId,
    cancellationFeedback,
    cancellationFeedbackReservationId,
    fetchMyReservations,
    cancelReservation,
    copyBookingCode,
    openCancelConfirmation,
    closeCancelConfirmation
} = useReservations()

// Template'deki kÄ±sa isimlerle uyum iÃ§in alias
const isCompleted = isCompletedStatus
const isCopyAllowed = isCopyAllowedStatus

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
                    <p class="text-slate-400 mt-2 max-w-lg">StÃ¼dyoda gÃ¶stermek Ã¼zere kilitlediÄŸin fÄ±rsatlar ve geÃ§miÅŸ Pilates seanslarÄ±n.</p>
                </div>
                <button @click="router.push('/')" class="group flex items-center gap-2 text-sm font-bold text-slate-400 hover:text-white transition-colors">
                    <span class="material-symbols-outlined transform group-hover:-translate-x-1 transition-transform">arrow_back</span>
                    Arenaya DÃ¶n
                </button>
            </div>
        </header>

        <main class="max-w-5xl mx-auto px-6 py-10">
            <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4">
                <div class="w-12 h-12 border-4 border-slate-800 border-t-neon-blue rounded-full animate-spin"></div>
                <p class="text-slate-500 animate-pulse">Biletleriniz ÅŸifreleniyor...</p>
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
                <h2 class="text-2xl font-bold text-white mb-2">HenÃ¼z Bir FÄ±rsat YakalamadÄ±n</h2>
                <p class="text-slate-400 mb-8 max-w-md">Hollanda aÃ§Ä±k artÄ±rmasÄ± devam ediyor. Fiyatlar dÃ¼ÅŸerken ilk kapan sen ol ve dijital biletini oluÅŸtur.</p>
                <button @click="router.push('/')" class="px-8 py-4 bg-neon-blue hover:bg-blue-500 text-black font-black rounded-xl transition-all shadow-[0_0_20px_rgba(0,191,255,0.3)] hover:shadow-[0_0_30px_rgba(0,191,255,0.5)] hover:scale-105">
                    CanlÄ± Seanslara Git
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
                                <p class="text-xs text-slate-500 uppercase tracking-wider mb-0.5">Seans ZamanÄ±</p>
                                <p class="text-lg font-bold text-white">{{ formatDate(res.scheduled_at || res.auction_start_time) }}</p>
                                <p class="text-neon-blue font-mono">{{ formatTime(res.scheduled_at || res.auction_start_time) }}</p>
                            </div>
                        </div>

                        <div class="mb-6">
                            <h3 class="text-2xl md:text-3xl font-black text-white mb-2">{{ res.auction_title || 'Ã–zel Pilates SeansÄ±' }}</h3>
                            <p v-if="res.auction_description" class="text-slate-400 text-sm line-clamp-2 max-w-xl">{{ res.auction_description }}</p>
                        </div>

                        <div class="flex items-center gap-4 text-xs text-slate-500 mt-auto border-t border-white/5 pt-4">
                            <div class="flex items-center gap-1">
                                <span class="material-symbols-outlined text-[16px]">shopping_cart_checkout</span>
                                AlÄ±m: {{ formatDate(res.reserved_at) }} - {{ formatTime(res.reserved_at) }}
                            </div>
                        </div>

                        <div v-if="res.status === 'PENDING_ON_SITE'" class="mt-5">
                            <button
                                @click="openCancelConfirmation(res.id)"
                                class="w-full md:w-auto px-4 py-2.5 text-xs font-black uppercase tracking-wider rounded-xl border border-red-500/30 text-red-300 bg-red-950/30 hover:bg-red-950/45 hover:border-red-400/40 transition-colors flex items-center justify-center gap-2"
                                :disabled="cancellingReservationId === res.id"
                            >
                                <span class="material-symbols-outlined text-[16px]">cancel</span>
                                Rezervasyonu Ä°ptal Et
                            </button>

                            <div
                                v-if="confirmCancelReservationId === res.id"
                                class="mt-3 p-4 rounded-xl border border-red-500/40 bg-red-950/35 backdrop-blur-sm"
                            >
                                <div class="flex items-start gap-3">
                                    <span class="material-symbols-outlined text-red-300 mt-0.5">warning</span>
                                    <div class="text-left">
                                        <p class="text-sm font-black text-red-200 uppercase tracking-wide">Dikkat: Bu iÅŸlem geri alÄ±namaz</p>
                                        <p class="text-xs text-red-100/90 mt-1 leading-relaxed">
                                            Bu rezervasyonu iptal ettiÄŸiniz anda giriÅŸ kodunuz kalÄ±cÄ± olarak geÃ§ersiz olur ve aynÄ± seansÄ± bu fiyattan tekrar talep edemezsiniz.
                                        </p>
                                    </div>
                                </div>

                                <div class="mt-4 flex flex-col sm:flex-row gap-2">
                                    <button
                                        @click="cancelReservation(res.id)"
                                        class="px-4 py-2.5 rounded-lg text-xs font-black uppercase tracking-wider bg-red-500 text-white hover:bg-red-400 transition-colors"
                                        :disabled="cancellingReservationId === res.id"
                                    >
                                        {{ cancellingReservationId === res.id ? 'Ä°ptal Ediliyor...' : 'Evet, Ä°ptal Et' }}
                                    </button>
                                    <button
                                        @click="closeCancelConfirmation"
                                        class="px-4 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider border border-white/15 text-slate-300 hover:bg-white/5 transition-colors"
                                        :disabled="cancellingReservationId === res.id"
                                    >
                                        VazgeÃ§
                                    </button>
                                </div>
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

                            <p class="text-xs text-slate-500 uppercase tracking-widest mb-2">GiriÅŸ Kodunuz</p>
                            <div
                                class="bg-black/50 border border-white/10 rounded-lg p-4 mb-3 transition-colors"
                                :class="isCopyAllowed(res.status) ? 'cursor-pointer hover:border-neon-blue/40' : 'cursor-not-allowed opacity-80'"
                                @click="isCopyAllowed(res.status) && copyBookingCode(res.id, res.booking_code)"
                                :title="isCopyAllowed(res.status)
                                  ? (copiedReservationId === res.id ? 'KopyalandÄ±' : 'Kopyalamak iÃ§in tÄ±kla')
                                  : 'Sadece Ã¶deme bekleyen biletlerin kodu kopyalanabilir'"
                            >
                                <p class="text-3xl md:text-4xl font-mono font-black tracking-widest" 
                                   :class="isCompleted(res.status) ? 'text-slate-600 line-through decoration-slate-600/50' : 'text-neon-green drop-shadow-[0_0_8px_rgba(54,211,153,0.8)]'">
                                    {{ res.booking_code }}
                                </p>
                            </div>

                            <p class="text-[11px] font-semibold mb-3"
                               :class="copiedReservationId === res.id ? 'text-neon-blue' : 'text-slate-500'">
                                {{ copiedReservationId === res.id
                                  ? 'KopyalandÄ±'
                                  : (isCopyAllowed(res.status)
                                    ? 'Kopyalamak iÃ§in kodun Ã¼stÃ¼ne tÄ±klayÄ±n'
                                    : 'Bu bilette kopyalama devre dÄ±ÅŸÄ±') }}
                            </p>
                            
                            <p class="text-[11px] text-slate-400 leading-tight">
                                <span v-if="res.status === 'PENDING_ON_SITE'">Ã–demenizi yapmak ve seansa katÄ±lmak iÃ§in bu kodu stÃ¼dyo resepsiyonuna gÃ¶sterin.</span>
                                <span v-else>Bu biletin geÃ§erliliÄŸi sona ermiÅŸtir.</span>
                            </p>

                            <p
                                v-if="cancellationFeedback && cancellationFeedbackReservationId === res.id"
                                class="text-[11px] mt-3 font-semibold"
                                :class="cancellationFeedback.type === 'success' ? 'text-neon-green' : 'text-red-300'"
                            >
                                {{ cancellationFeedback.message }}
                            </p>
                        </div>
                    </div>

                </div>
            </div>
        </main>
    </div>
</template>

<style scoped>
/* Opsiyonel: Bilet kenarlarÄ±ndaki yuvarlak kesikleri daha yumuÅŸak yapmak iÃ§in */
.bg-background-dark {
    background-color: #050505; /* Projenin ana arka plan rengine gÃ¶re ayarla */
}
</style>