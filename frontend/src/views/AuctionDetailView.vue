<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue' 
import { useRoute, useRouter } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auctionStore = useAuctionStore()
const socketStore = useSocketStore()
const authStore = useAuthStore()

const auction = computed(() => auctionStore.currentAuction)
const showSuccessModal = ref(false)
const reservation = ref(null)
const bookingLoading = ref(false)

// Turbo Mode Logic
const isTurbo = computed(() => auction.value?.turboActive || false)

// Dynamic Theme Classes
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
    } else {
        return {
            bgMain: 'bg-background-dark',
            bgCard: 'bg-[#1a1f2e]/60', // glass-card default
            borderAccent: 'border-neon-blue',
            textAccent: 'text-neon-blue',
            textTurbo: 'text-neon-orange',
            gradientBtn: 'from-primary via-blue-600 to-neon-blue',
            shadowNeon: 'shadow-neon-blue',
            glowColor: 'rgba(0, 240, 255, 0.5)'
        }
    }
})

onMounted(async () => {
    const id = route.params.id
    if (!socketStore.isConnected) {
        socketStore.connect()
    }
    socketStore.subscribeAuction(id)
    await auctionStore.fetchAuctionById(id)

    socketStore.on('price_update', (data) => {
        if (data.auction_id == id) {
             auctionStore.updatePrice(id, data.current_price)
        }
    })

    socketStore.on('auction_booked', (data) => {
        if (data.auction_id == id) {
            console.log('Auction booked by another user:', data)
            if (auction.value) {
                auction.value.status = 'SOLD'
            }
        }
    })
})

const handleBook = async () => {
    if (!auction.value) return;

    if (!authStore.isAuthenticated) {
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }

    if (!confirm(`${auction.value.currentPrice} TL tutarýndaki bu oturumu rezerve etmek istediðinize emin misiniz?`)) {
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
    socketStore.off('price_update')
})

// Format helpers
const formatPrice = (val) => Math.floor(val)
const formatTime = (isoString) => {
    if(!isoString) return '--';
    const d = new Date(isoString);
    const now = new Date();
    const diff = Math.floor((d - now) / 1000);
    if(diff < 0) return '00';
    return String(diff % 60).padStart(2, '0');
}

// Mock countdown parts for the visual design
const hours = '00'
const mins = '00'
// We'll use a simple reactive counter for seconds for the visual effect if needed, 
// but for now let's just rely on the static design or simple update logic if we want.
</script>

<template>
  <!-- Loading State -->
  <div v-if="auctionStore.loading && !auction" class="flex items-center justify-center min-h-screen bg-background-dark text-white">
    <div class="animate-spin h-12 w-12 border-4 border-neon-blue border-t-transparent rounded-full"></div>
  </div>

  <!-- Main Content -->
  <div v-else-if="auction" 
       class="layout-container min-h-screen flex flex-col items-center justify-center py-8 px-4 sm:px-6 lg:px-8 relative transition-colors duration-700"
       :class="[themeClasses.bgMain]">
       
    <!-- Background Glow Effects -->
    <div class="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-[128px] pointer-events-none transition-colors duration-700"
         :style="{ backgroundColor: themeClasses.glowColor, opacity: 0.2 }"></div>
    <div class="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-[128px] pointer-events-none transition-colors duration-700"
         :style="{ backgroundColor: isTurbo ? 'rgba(255, 123, 0, 0.2)' : 'rgba(37, 106, 244, 0.2)' }"></div>

    <!-- Details Container -->
    <div class="layout-content-container flex flex-col w-full max-w-[640px] relative z-10 font-display">
        
        <!-- Breadcrumbs -->
        <nav class="flex flex-wrap gap-2 mb-8 items-center justify-center sm:justify-start">
            <router-link to="/" class="text-slate-400 hover:text-white text-sm font-medium transition-colors">Ana Sayfa</router-link>
            <span class="text-slate-600 text-sm font-medium">/</span>
            <span class="text-slate-400 text-sm font-medium">Pilates Oturumlarý</span>
            <span class="text-slate-600 text-sm font-medium">/</span>
            <span class="text-sm font-medium flex items-center gap-1 transition-colors duration-500" :class="themeClasses.textAccent">
                <span class="material-symbols-outlined text-sm">bolt</span>
                {{ isTurbo ? 'Turbo Mod' : 'Normal Mod' }}
            </span>
        </nav>

        <!-- Main Card -->
        <div class="relative rounded-3xl p-1 overflow-hidden transition-all duration-500"
             :class="[themeClasses.shadowNeon, isTurbo ? 'border-2 border-[#f20d80]/50' : 'border border-white/10']">
            
            <!-- Animated Border (Turbo only) -->
            <div v-if="isTurbo" class="absolute inset-0 bg-gradient-to-r from-[#f20d80] via-[#ff7b00] to-[#f20d80] opacity-20 animate-pulse pointer-events-none"></div>
            
            <div class="rounded-[1.3rem] p-6 sm:p-10 relative overflow-hidden flex flex-col items-center text-center gap-6 h-full transition-colors duration-500"
                 :class="[isTurbo ? 'bg-background-dark' : 'bg-[#1a1f2e]/90 backdrop-blur-xl']">
                
                <!-- Header -->
                <div class="w-full flex justify-between items-start mb-4">
                    <div class="flex flex-col items-start gap-1">
                        <div class="flex items-center gap-2">
                            <span class="relative flex h-3 w-3">
                                <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="isTurbo ? 'bg-[#ff2a2a]' : 'bg-green-500'"></span>
                                <span class="relative inline-flex rounded-full h-3 w-3" :class="isTurbo ? 'bg-[#ff2a2a]' : 'bg-green-500'"></span>
                            </span>
                            <p class="font-bold tracking-widest text-xs uppercase" :class="isTurbo ? 'text-[#ff2a2a]' : 'text-green-500'">
                                Canlý Oturum
                            </p>
                        </div>
                        <h1 class="text-white text-2xl sm:text-3xl font-bold leading-tight mt-1">{{ auction.title }}</h1>
                        <p class="text-slate-400 text-sm text-left">{{ auction.studioName || 'Zenith Stüdyo' }}</p>
                    </div>
                    <div class="px-3 py-1 rounded-lg border border-white/10" :class="isTurbo ? 'bg-[#392830]' : 'bg-white/5'">
                        <span class="text-slate-300 text-xs font-mono">ID: #{{ auction.id }}</span>
                    </div>
                </div>

                <!-- Price Section -->
                <div class="flex flex-col items-center justify-center py-6 w-full relative">
                    <div class="text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">Güncel Fiyat</div>
                    
                    <div class="relative">
                        <h1 class="text-white text-[80px] sm:text-[100px] font-mono font-black leading-none tracking-tighter transition-all duration-300 transform"
                            :class="{ 'drop-shadow-[0_0_25px_rgba(242,13,128,0.5)]': isTurbo }">
                            ?{{ formatPrice(auction.currentPrice) }}
                        </h1>
                        <!-- Glitch bg -->
                        <div v-if="isTurbo" class="absolute -inset-1 bg-[#f20d80]/20 blur-xl -z-10 animate-pulse"></div>
                    </div>

                    <div class="mt-4 flex items-center gap-2 px-4 py-1.5 rounded-full border transition-colors duration-500"
                         :class="isTurbo ? 'bg-red-500/10 border-red-500/20' : 'bg-blue-500/10 border-blue-500/20'">
                        <span class="material-symbols-outlined text-sm" :class="isTurbo ? 'text-red-500' : 'text-blue-400'">trending_down</span>
                        <p class="text-xs font-bold uppercase tracking-wide" :class="isTurbo ? 'text-red-400' : 'text-blue-400'">
                            {{ isTurbo ? 'Hýzlý Düþüþ' : 'Fiyat Düþüyor' }}
                        </p>
                    </div>
                </div>

                <!-- Timer Grid -->
                <div class="grid grid-cols-3 gap-3 w-full max-w-sm mb-6">
                    <!-- Hours -->
                    <div class="flex flex-col items-center gap-2 p-3 rounded-xl border border-white/5 transition-colors"
                         :class="isTurbo ? 'bg-[#2a1621]' : 'bg-white/5'">
                        <span class="text-3xl font-bold text-white font-mono">{{ hours }}</span>
                        <span class="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Saat</span>
                    </div>
                     <!-- Mins -->
                    <div class="flex flex-col items-center gap-2 p-3 rounded-xl border border-white/5 transition-colors"
                         :class="isTurbo ? 'bg-[#2a1621]' : 'bg-white/5'">
                        <span class="text-3xl font-bold text-white font-mono">{{ mins }}</span>
                        <span class="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Dk</span>
                    </div>
                     <!-- Secs (Active) -->
                    <div class="flex flex-col items-center gap-2 p-3 rounded-xl border relative overflow-hidden transition-all"
                         :class="isTurbo ? 'bg-[#2a1621] border-[#ff2a2a]/30 shadow-[0_0_15px_rgba(255,42,42,0.15)]' : 'bg-white/5 border-neon-blue/30'">
                        <div v-if="isTurbo" class="absolute inset-0 bg-[#ff2a2a]/5 animate-pulse"></div>
                        <!-- We assume logic to calculate remaining seconds for drop exists, using placeholder for visual match -->
                        <span class="text-3xl font-bold font-mono relative z-10" :class="themeClasses.textTurbo">
                            {{ formatTime(auction.nextDropTime) }}
                        </span>
                        <span class="text-[10px] uppercase font-bold tracking-wider relative z-10" :class="themeClasses.textTurbo">Sn</span>
                    </div>
                </div>

                <!-- Info Row -->
                <div class="grid grid-cols-2 gap-4 w-full mb-4">
                    <div class="p-3 rounded-xl border border-white/5 text-left transition-colors" :class="isTurbo ? 'bg-[#2a1621]/50' : 'bg-white/5'">
                        <p class="text-slate-400 text-xs mb-1">Baþlangýç Fiyatý</p>
                        <p class="text-white font-bold line-through decoration-slate-500">?{{ auction.startPrice }}</p>
                    </div>
                    <div class="p-3 rounded-xl border border-white/5 text-left transition-colors" :class="isTurbo ? 'bg-[#2a1621]/50' : 'bg-white/5'">
                        <p class="text-slate-400 text-xs mb-1">Tasarruf</p>
                        <p class="font-bold text-green-400">
                            %{{ Math.round(((auction.startPrice - auction.currentPrice) / auction.startPrice) * 100) }} Ýndirim
                        </p>
                    </div>
                </div>

                <!-- CTA Button -->
                <button @click="handleBook" 
                        :disabled="auction.status !== 'ACTIVE' || bookingLoading"
                        class="group relative w-full overflow-hidden rounded-2xl p-[2px] transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg"
                        :class="[themeClasses.gradientBtn, themeClasses.shadowNeon]">
                    
                    <div class="relative flex h-16 w-full items-center justify-center rounded-[14px] px-8 transition-all"
                         :class="`bg-gradient-to-r ${themeClasses.gradientBtn}`">
                        
                        <span class="absolute right-0 -mt-12 -mr-12 h-32 w-32 translate-x-1/2 rotate-45 bg-white opacity-10 blur-xl transition-all duration-1000 group-hover:-translate-x-full"></span>
                        
                        <span v-if="bookingLoading" class="flex items-center gap-2 text-white font-bold animate-pulse">
                             <span class="material-symbols-outlined animate-spin">sync</span>
                             ÝÞLENÝYOR...
                        </span>
                        <div v-else class="flex items-center gap-2">
                             <span class="material-symbols-outlined text-white text-3xl font-bold" :class="{'animate-pulse': isTurbo}">shopping_bag</span>
                             <span class="text-2xl font-black text-white tracking-wider uppercase">
                                 {{ auction.status === 'ACTIVE' ? 'HEMEN KAP' : 'TÜKENDÝ' }}
                             </span>
                        </div>
                    </div>
                </button>

                <p class="text-slate-500 text-xs mt-4">Týklayarak <a href="#" class="hover:underline transition-colors" :class="themeClasses.textAccent">Kullaným Þartlarýný</a> kabul etmiþ olursunuz. Ýadeler kabul edilmemektedir.</p>
            </div>
        </div>

        <!-- Live Feed (Static Mock) -->
        <div class="mt-8 grid gap-3 w-full">
            <p class="text-slate-400 text-sm font-medium mb-1 px-2">Canlý Hareketler</p>
            <div class="flex items-center justify-between p-3 rounded-xl border border-white/5 transition-colors" :class="isTurbo ? 'bg-[#2a1621]' : 'bg-white/5'">
                <div class="flex items-center gap-3">
                     <div class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-600 flex items-center justify-center text-xs font-bold text-white">
                         ED
                     </div>
                     <div>
                         <p class="text-white text-sm font-medium">Elif D.</p>
                         <p class="text-slate-400 text-xs">Sýraya girdi</p>
                     </div>
                </div>
                <span class="text-slate-500 text-xs">2sn önce</span>
            </div>
        </div>

    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
        <div class="bg-[#1a1f2e] border-2 rounded-2xl p-8 max-w-md w-full text-center shadow-2xl relative overflow-hidden" :class="themeClasses.borderAccent">
            <div class="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>
            <div class="relative z-10">
                <div class="text-6xl mb-4"></div>
                <h2 class="text-3xl font-bold text-white mb-2">Rezervasyon Onaylandý!</h2>
                <p class="text-slate-300 mb-6">Bu oturumu baþarýyla yakaladýnýz.</p>
                
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
        <h2 class="text-2xl text-slate-500">Oturum bulunamadý</h2>
        <router-link to="/" class="mt-4 px-6 py-2 rounded-lg border border-white/20 hover:bg-white/10 transition-colors">Ana Sayfaya Dön</router-link>
  </div>
</template>
