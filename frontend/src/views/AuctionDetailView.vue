<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'
import { useAuthStore } from '../stores/auth'
import HemenKapButton from '../components/HemenKapButton.vue'
import { getAuctionField, getAuctionCurrentPrice, getAuctionStartPrice, getAuctionEndTime, getAuctionStatus } from '../utils/auction'

const route = useRoute()
const router = useRouter()
const auctionStore = useAuctionStore()
const socketStore = useSocketStore()
const authStore = useAuthStore()

const auction = computed(() => auctionStore.currentAuction)
const showSuccessModal = ref(false)
const reservation = ref(null)
const bookingLoading = ref(false)
const nowMs = ref(Date.now())
let timerId = null

const startPriceValue = computed(() => getAuctionStartPrice(auction.value))
const currentPriceValue = computed(() => getAuctionCurrentPrice(auction.value))
const endTimeValue = computed(() => getAuctionEndTime(auction.value))
const statusValue = computed(() => getAuctionStatus(auction.value))

const discountPercent = computed(() => {
    if (startPriceValue.value <= 0) return 0
    const discount = ((startPriceValue.value - currentPriceValue.value) / startPriceValue.value) * 100
    return Math.max(0, Math.round(discount))
})

const countdown = computed(() => {
    if (!endTimeValue.value) return { hours: '00', mins: '00', secs: '00' }

    const end = new Date(endTimeValue.value).getTime()
    const diff = end - nowMs.value

    if (diff <= 0) return { hours: '00', mins: '00', secs: '00' }

    const totalSeconds = Math.floor(diff / 1000)
    const hours = Math.floor(totalSeconds / 3600)
    const mins = Math.floor((totalSeconds % 3600) / 60)
    const secs = totalSeconds % 60

    return {
        hours: String(hours).padStart(2, '0'),
        mins: String(mins).padStart(2, '0'),
        secs: String(secs).padStart(2, '0')
    }
})

const isTurbo = computed(() => Boolean(getAuctionField(auction.value, 'turbo_started_at', 'turboStartedAt')))

const themeClasses = computed(() => {
    if (isTurbo.value) {
        return {
            bgMain: 'bg-[#221019]',
            bgCard: 'bg-[#221019]/50',
            borderAccent: 'border-[#f20d80]',
            textAccent: 'text-[#f20d80]',
            textTurbo: 'text-[#ff2a2a]',
            gradientBtn: 'from-[#f20d80] via-[#ff0055] to-[#ff7b00]',
            shadowNeon: 'shadow-[0_0_20px_rgba(242,13,128,0.5),0_0_40px_rgba(255,42,42,0.3)]',
            glowColor: 'rgba(242, 13, 128, 0.5)'
        }
    }

    return {
        bgMain: 'bg-background-dark',
        bgCard: 'bg-[#1a1f2e]/60',
        borderAccent: 'border-neon-blue',
        textAccent: 'text-neon-blue',
        textTurbo: 'text-neon-orange',
        gradientBtn: 'from-primary via-blue-600 to-neon-blue',
        shadowNeon: 'shadow-neon-blue',
        glowColor: 'rgba(0, 240, 255, 0.5)'
    }
})

const onPriceUpdate = (data) => {
    if (data.auction_id == route.params.id) {
        auctionStore.updatePrice(route.params.id, data.current_price)
    }
}

const onAuctionBooked = (data) => {
    if (data.auction_id == route.params.id && auction.value) {
        auction.value.status = 'SOLD'
    }
}

onMounted(async () => {
    const id = route.params.id

    if (!socketStore.isConnected) {
        socketStore.connect()
    }

    socketStore.subscribeAuction(id)
    await auctionStore.fetchAuctionById(id)

    socketStore.on('price_update', onPriceUpdate)
    socketStore.on('auction_booked', onAuctionBooked)

    timerId = setInterval(() => {
        nowMs.value = Date.now()
    }, 1000)
})

const formatPrice = (val) => {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY',
        maximumFractionDigits: 0
    }).format(Number(val || 0))
}

const handleBook = async () => {
    if (!auction.value) return

    if (!authStore.isAuthenticated) {
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }

    if (!confirm(`${formatPrice(currentPriceValue.value)} tutarındaki bu oturumu rezerve etmek istediğinize emin misiniz?`)) {
        return
    }

    bookingLoading.value = true
    try {
        const result = await auctionStore.bookAuction(auction.value.id)
        reservation.value = result
        showSuccessModal.value = true
    } catch (err) {
        alert(err.message)
    } finally {
        bookingLoading.value = false
    }
}

onUnmounted(() => {
    if (route.params.id) {
        socketStore.unsubscribeAuction(route.params.id)
    }

    socketStore.off('price_update', onPriceUpdate)
    socketStore.off('auction_booked', onAuctionBooked)

    if (timerId) {
        clearInterval(timerId)
        timerId = null
    }
})
</script>

<template>
  <!-- Loading State -->
  <div v-if="auctionStore.loading && !auction" class="flex items-center justify-center min-h-screen bg-background-dark text-white">
    <div class="animate-spin h-12 w-12 border-4 border-neon-blue border-t-transparent rounded-full"></div>
  </div>

  <!-- Main Content -->
  <div v-else-if="auction" 
       class="layout-container min-h-screen flex flex-col items-center justify-start md:justify-center pt-20 pb-8 md:py-8 px-4 sm:px-6 lg:px-8 relative transition-colors duration-700 overflow-x-hidden"
       :class="[themeClasses.bgMain]">
       
    <!-- Background Glow Effects -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-[128px] pointer-events-none transition-colors duration-700"
         :style="{ backgroundColor: themeClasses.glowColor, opacity: 0.2 }"></div>
    <div class="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-[128px] pointer-events-none transition-colors duration-700"
         :style="{ backgroundColor: isTurbo ? 'rgba(255, 123, 0, 0.2)' : 'rgba(37, 106, 244, 0.2)' }"></div>

    <!-- Details Container -->
    <div class="layout-content-container flex flex-col w-full items-center justify-center relative z-10 font-display transition-all duration-300">
        
        <!-- Right Column: Price & Action -->
        <div class="w-full max-w-lg md:max-w-2xl flex flex-col items-center relative">
            
            <!-- Breadcrumbs (Mobile only) -->
            <nav class="flex md:hidden flex-wrap gap-2 mb-6 items-center justify-center">
                <router-link to="/" class="text-slate-400 hover:text-white text-xs font-medium transition-colors">Ana Sayfa</router-link>
                <span class="text-slate-600 text-xs font-medium">/</span>
                <span class="text-slate-400 text-xs font-medium">Pilates</span>
                <span class="text-slate-600 text-xs font-medium">/</span>
                <span class="text-xs font-medium flex items-center gap-1 transition-colors duration-500" :class="themeClasses.textAccent">
                    <span class="material-symbols-outlined text-xs">bolt</span>
                    {{ isTurbo ? 'Turbo' : 'Normal' }}
                </span>
            </nav>

            <!-- Main Card -->
            <div class="relative w-full min-h-[550px] md:min-h-[600px] rounded-[2rem] p-[1px] overflow-hidden transition-all duration-500 shadow-2xl"
                 :class="[themeClasses.shadowNeon, isTurbo ? 'border-2 border-[#f20d80]/50' : 'border border-white/10']">
            
                <!-- Animated Border (Turbo only) -->
                <div v-if="isTurbo" class="absolute inset-0 bg-gradient-to-r from-[#f20d80] via-[#ff7b00] to-[#f20d80] opacity-20 animate-pulse pointer-events-none"></div>
                
                <div class="rounded-[2rem] p-6 sm:p-8 md:p-10 relative overflow-hidden flex flex-col items-center text-center gap-4 md:gap-6 h-full justify-between transition-colors duration-500 bg-background-dark/90 backdrop-blur-3xl">
                    
                    <!-- Header -->
                    <div class="w-full flex justify-between items-start">
                        <div class="flex flex-col items-start gap-1">
                            <div class="flex items-center gap-2">
                                <span class="relative flex h-3 w-3">
                                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="isTurbo ? 'bg-[#ff2a2a]' : 'bg-green-500'"></span>
                                    <span class="relative inline-flex rounded-full h-3 w-3" :class="isTurbo ? 'bg-[#ff2a2a]' : 'bg-green-500'"></span>
                                </span>
                                <p class="font-bold tracking-widest text-[10px] sm:text-xs uppercase" :class="isTurbo ? 'text-[#ff2a2a]' : 'text-green-500'">
                                    Canlı Oturum
                                </p>
                            </div>
                            <h1 class="text-white text-2xl sm:text-3xl md:text-4xl font-black leading-tight mt-1 text-left">{{ auction.title }}</h1>
                            <p class="text-slate-400 text-xs sm:text-sm text-left">{{ auction.description || 'Bu oturum için açıklama bilgisi bulunmuyor.' }}</p>
                        </div>
                    </div>

                    <!-- Price Section -->
                    <div class="flex flex-col items-center justify-center py-4 sm:py-8 w-full relative">
                        <div class="text-slate-400 text-xs sm:text-sm font-medium mb-2 uppercase tracking-wider">Güncel Fiyat</div>
                        
                        <div class="relative">
                            <h1 class="text-white text-[72px] sm:text-[100px] md:text-[120px] font-mono font-black leading-none tracking-tighter transition-all duration-300 transform"
                                :class="{ 'drop-shadow-[0_0_25px_rgba(242,13,128,0.5)]': isTurbo }">
                                {{ formatPrice(currentPriceValue) }}
                            </h1>
                            <!-- Glitch bg -->
                            <div v-if="isTurbo" class="absolute -inset-1 bg-[#f20d80]/20 blur-xl -z-10 animate-pulse"></div>
                        </div>

                        <div class="mt-4 flex items-center gap-2 px-4 py-1.5 rounded-full border transition-colors duration-500"
                            :class="isTurbo ? 'bg-red-500/10 border-red-500/20' : 'bg-blue-500/10 border-blue-500/20'">
                            <span class="material-symbols-outlined text-sm" :class="isTurbo ? 'text-red-500' : 'text-blue-400'">trending_down</span>
                            <p class="text-xs font-bold uppercase tracking-wide" :class="isTurbo ? 'text-red-400' : 'text-blue-400'">
                                {{ isTurbo ? 'Hızlı Düşüş' : 'Fiyat Düşüyor' }}
                            </p>
                        </div>
                    </div>

                    <!-- Timer Grid (Compact on Mobile) -->
                    <div class="grid grid-cols-3 gap-2 sm:gap-4 w-full max-w-sm mb-2 sm:mb-6">
                        <!-- Hours -->
                        <div class="flex flex-col items-center gap-1 sm:gap-2 p-2 sm:p-4 rounded-2xl border border-white/5 transition-colors"
                            :class="isTurbo ? 'bg-[#2a1621]' : 'bg-white/5'">
                            <span class="text-xl sm:text-3xl font-bold text-white font-mono">{{ countdown.hours }}</span>
                            <span class="text-[8px] sm:text-[10px] uppercase text-slate-400 font-bold tracking-wider">Saat</span>
                        </div>
                        <!-- Mins -->
                        <div class="flex flex-col items-center gap-1 sm:gap-2 p-2 sm:p-4 rounded-2xl border border-white/5 transition-colors"
                            :class="isTurbo ? 'bg-[#2a1621]' : 'bg-white/5'">
                            <span class="text-xl sm:text-3xl font-bold text-white font-mono">{{ countdown.mins }}</span>
                            <span class="text-[8px] sm:text-[10px] uppercase text-slate-400 font-bold tracking-wider">Dk</span>
                        </div>
                        <!-- Secs (Active) -->
                        <div class="flex flex-col items-center gap-1 sm:gap-2 p-2 sm:p-4 rounded-2xl border relative overflow-hidden transition-all"
                            :class="isTurbo ? 'bg-[#2a1621] border-[#ff2a2a]/30 shadow-[0_0_15px_rgba(255,42,42,0.15)]' : 'bg-white/5 border-neon-blue/30'">
                            <div v-if="isTurbo" class="absolute inset-0 bg-[#ff2a2a]/5 animate-pulse"></div>
                            <span class="text-xl sm:text-3xl font-bold font-mono relative z-10" :class="themeClasses.textTurbo">
                                {{ countdown.secs }}
                            </span>
                            <span class="text-[8px] sm:text-[10px] uppercase font-bold tracking-wider relative z-10" :class="themeClasses.textTurbo">Sn</span>
                        </div>
                    </div>

                    <!-- Info Row -->
                    <div class="grid grid-cols-2 gap-3 sm:gap-4 w-full mb-2 sm:mb-4">
                        <div class="p-3 sm:p-4 rounded-xl border border-white/5 text-left transition-colors" :class="isTurbo ? 'bg-[#2a1621]/50' : 'bg-white/5'">
                            <p class="text-slate-400 text-[10px] sm:text-xs mb-1 uppercase tracking-wider">Başlangıç</p>
                            <p class="text-white font-bold line-through decoration-slate-500 text-sm sm:text-base">{{ formatPrice(startPriceValue) }}</p>
                        </div>
                        <div class="p-3 sm:p-4 rounded-xl border border-white/5 text-left transition-colors" :class="isTurbo ? 'bg-[#2a1621]/50' : 'bg-white/5'">
                            <p class="text-slate-400 text-[10px] sm:text-xs mb-1 uppercase tracking-wider">Kazanç</p>
                            <p class="font-bold text-green-400 text-sm sm:text-base">
                                %{{ discountPercent }} İndirim
                            </p>
                        </div>
                    </div>

                    <!-- CTA Button -->
                    <HemenKapButton
                        variant="detail"
                        :loading="bookingLoading"
                        :disabled="statusValue !== 'ACTIVE'"
                        :is-active="statusValue === 'ACTIVE'"
                        :animate-icon="isTurbo"
                        :gradient-class="themeClasses.gradientBtn"
                        :shadow-class="themeClasses.shadowNeon"
                        @click="handleBook"
                    />

                    <p class="block text-slate-500 text-xs">Tıklayarak <a href="#" class="hover:underline transition-colors" :class="themeClasses.textAccent">Kullanım Şartlarını</a> kabul etmiş olursunuz.</p>
                </div>
            </div>

            <!-- Removed Mobile Sticky Bottom Action Bar -->

        </div>

    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
        <div class="bg-[#1a1f2e] border-2 rounded-2xl p-8 max-w-md w-full text-center shadow-2xl relative overflow-hidden" :class="themeClasses.borderAccent">
            <div class="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>
            <div class="relative z-10">
                <div class="text-6xl mb-4"></div>
                <h2 class="text-3xl font-bold text-white mb-2">Rezervasyon Onaylandı!</h2>
                <p class="text-slate-300 mb-6">Bu oturumu başarıyla yakaladınız.</p>
                
                <div class="bg-white/10 p-4 rounded-lg mb-6 border border-white/10">
                    <div class="text-sm text-slate-400 uppercase tracking-wider mb-1">Rezervasyon Kodunuz</div>
                    <div class="text-4xl font-bold tracking-widest font-mono" :class="themeClasses.textAccent">
                        {{ reservation?.booking_code || 'HOT-XXXX' }}
                    </div>
                </div>
                
                <button @click="showSuccessModal = false" class="w-full py-3 rounded-xl font-bold text-white uppercase tracking-wide transition-all hover:scale-[1.02]" :class="`bg-gradient-to-r ${themeClasses.gradientBtn}`">
                    Kapat
                </button>
            </div>
        </div>
    </div>

  </div>
  
  <div v-else class="min-h-screen flex flex-col items-center justify-center bg-background-dark text-white">
        <h2 class="text-2xl text-slate-500">Oturum bulunamadı</h2>
        <router-link to="/" class="mt-4 px-6 py-2 rounded-lg border border-white/20 hover:bg-white/10 transition-colors">Ana Sayfaya Dön</router-link>
  </div>
</template>
