<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue' 
import { useRoute, useRouter } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'
import { useAuthStore } from '../stores/auth'
import PriceTicker from '../components/PriceTicker.vue'
import CountDownTimer from '../components/CountDownTimer.vue'

const route = useRoute()
const router = useRouter()
const auctionStore = useAuctionStore()
const socketStore = useSocketStore()
const authStore = useAuthStore()

const auction = computed(() => auctionStore.currentAuction)
const showSuccessModal = ref(false)
const reservation = ref(null)
const bookingLoading = ref(false)

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
            // Ideally update status in store
            if (auction.value) {
                auction.value.status = 'SOLD'
            }
        }
    })
})

const handleBook = async () => {
    if (!auction.value) return;

    if (!authStore.isAuthenticated) {
        // Redirect to login with return path
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }

    if (!confirm(`Are you sure you want to book this session for ${auction.value.currentPrice} TL?`)) {
        return
    }

    bookingLoading.value = true
    try {
        const result = await auctionStore.bookAuction(auction.value.id)
        reservation.value = result
        showSuccessModal.value = true
    } catch (err) {
        alert(err.message) // Simple alert for now
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
</script>

<template>
  <div v-if="auctionStore.loading && !auction" class="flex items-center justify-center min-h-[60vh]">
    <div class="animate-spin h-12 w-12 border-4 border-neon-blue border-t-transparent rounded-full"></div>
  </div>
  
    <div v-else-if="auction" class="hh-section py-8 md:py-10 grid grid-cols-1 lg:grid-cols-2 gap-8 xl:gap-12 relative">
    
    <!-- Success Modal Overlay -->
    <div v-if="showSuccessModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                <div class="hh-glass-card border-2 border-neon-green rounded-2xl p-8 max-w-md w-full text-center shadow-[0_0_50px_rgba(0,255,0,0.3)]">
            <div class="text-6xl mb-4">🎉</div>
            <h2 class="text-3xl font-bold text-white mb-2">Booking Confirmed!</h2>
                        <p class="text-slate-300 mb-6">You successfully caught this session.</p>
            
                        <div class="bg-white/10 p-4 rounded-lg mb-6 border border-white/10">
                                <div class="text-sm text-slate-400 uppercase tracking-wider mb-1">Your Booking Code</div>
                                <div class="hh-code-text text-4xl font-bold text-neon-green">{{ reservation?.booking_code || 'HOT-XXXX' }}</div>
            </div>
            
                        <div class="text-sm text-slate-400 mb-6">
                Please show this code at the studio reception.<br>
                Locked Price: <span class="text-white font-bold">{{ reservation?.locked_price }} TL</span>
            </div>
            
                        <button @click="showSuccessModal = false" class="hh-btn-neon w-full py-3">
                Close
            </button>
        </div>
    </div>

    <!-- Left Column: Visuals & Price -->
        <div class="space-y-6 text-center md:text-left">
            <div class="relative hh-glass-card p-6 md:p-8 rounded-2xl border border-neon-blue/30 shadow-[0_0_30px_rgba(0,243,255,0.15)] overflow-hidden">
        <!-- Turbo Indicator -->
                <div v-if="auction.turboActive" class="absolute top-0 left-0 w-full bg-neon-orange text-black font-bold text-center py-1.5 animate-pulse">
            TURBO MODE ACTIVE 🔥
        </div>
        
                <h2 class="text-slate-400 text-xs md:text-sm tracking-widest uppercase mb-2 mt-4">Current Price</h2>
        <PriceTicker :price="auction.currentPrice" :large="true" />
        
                <div class="mt-8 flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4 border-t border-slate-700 pt-4">
            <CountDownTimer :targetTime="auction.nextDropTime" />
            <div class="text-right">
                                <span class="block text-xs text-slate-500">Starting Price</span>
                                <span class="text-slate-300 line-through">₺{{ auction.startPrice }}</span>
            </div>
        </div>
      </div>
      
      <button 
        @click="handleBook"
                class="w-full bg-gradient-to-r from-neon-blue to-neon-magenta p-4 rounded-lg font-bold text-xl text-slate-900 hover:scale-[1.02] transform transition-all shadow-neon-blue active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed group relative overflow-hidden"
        :disabled="auction.status !== 'ACTIVE' || bookingLoading"
      >
        <span v-if="bookingLoading" class="flex items-center justify-center gap-2">
                        <svg class="animate-spin h-5 w-5 text-slate-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            BOOKING...
        </span>
        <span v-else-if="auction.status === 'ACTIVE'">⚡ HEMEN KAP (BOOK NOW)</span>
        <span v-else>SOLD OUT</span>
        
        <!-- Shine Effect -->
        <div class="absolute inset-0 -translate-x-full group-hover:animate-shine bg-gradient-to-r from-transparent via-white/30 to-transparent z-10"></div>
      </button>
      
            <p class="text-xs text-center text-slate-500 mt-2">
        * Price locks instantly when you click book. Pay at the venue.
      </p>
    </div>

    <!-- Right Column: Details -->
        <div class="space-y-5">
        <div>
                        <h1 class="text-3xl md:text-4xl font-bold mb-2 text-white">{{ auction.title }}</h1>
                        <div class="flex items-center gap-2 text-neon-blue">
                                <span class="text-base md:text-lg">Instructed by {{ auction.instructor || 'Studio Instructor' }}</span>
            </div>
        </div>

                <div class="hh-card p-5 md:p-6">
                    <h3 class="font-bold text-slate-200 mb-2">Session Details</h3>
                    <p class="text-slate-400 leading-relaxed mb-4">
                        {{ auction.description || 'Join us for an intense session focused on core strength and flexibility. Suitable for all levels.' }}
                    </p>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="block text-slate-500">Date</span>
                            <span class="text-white">{{ new Date(auction.startTime).toLocaleDateString() }}</span>
                        </div>
                        <div>
                            <span class="block text-slate-500">Time</span>
                            <span class="text-white">{{ new Date(auction.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
                        </div>
                        <div>
                            <span class="block text-slate-500">Status</span>
                            <span :class="auction.status === 'ACTIVE' ? 'text-neon-green' : 'text-slate-300'">{{ auction.status }}</span>
                        </div>
                        <div>
                            <span class="block text-slate-500">Floor Price</span>
                            <span class="text-white">₺{{ auction.floorPrice || '-' }}</span>
                        </div>
                    </div>
                </div>

                <div class="hh-card p-5 border-l-4 border-neon-blue">
                        <h4 class="font-bold text-neon-blue mb-1">How it works</h4>
                        <p class="text-sm text-slate-300">
                                Price drops every few minutes. The longer you wait, the cheaper it gets per person. But wait too long, and someone else might grab it.
                        </p>
                </div>

                <router-link to="/" class="hh-btn-ghost w-full">Back to Arena</router-link>
        </div>
    </div>
  
    <div v-else class="hh-section text-center py-20">
        <h2 class="text-2xl text-slate-500">Auction not found</h2>
        <router-link to="/" class="hh-btn-ghost mt-4">Return Home</router-link>
    </div>
</template>

<style scoped>
@keyframes shine {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(100%);
    }
}

.group:hover .group-hover\:animate-shine {
    animation: shine 0.9s ease;
}
</style>
