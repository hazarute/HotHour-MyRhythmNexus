<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue' // Added ref
import { useRoute } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'
import PriceTicker from '../components/PriceTicker.vue'
import CountDownTimer from '../components/CountDownTimer.vue'

const route = useRoute()
const auctionStore = useAuctionStore()
const socketStore = useSocketStore()

const auction = computed(() => auctionStore.currentAuction)

onMounted(async () => {
    const id = route.params.id
    // Connect to socket and subscribe first to be ready
    if (!socketStore.isConnected) {
        socketStore.connect()
    }
    
    // Subscribe to room
    socketStore.subscribeAuction(id)

    // Fetch initial data
    await auctionStore.fetchAuctionById(id)

    // Listen for real-time updates
    socketStore.on('price_update', (data) => {
        // data = { auction_id: ..., current_price: ..., details: ... }
        if (data.auction_id == id) {
             console.log('Price update received:', data)
             auctionStore.updatePrice(id, data.current_price)
             // Ideally update nextDropTime from data.details if backend sends it
        }
    })
})

const handleBook = () => {
    // Phase 6: Booking Integration
    if (!auction.value) return;
    alert(`Booking initiated for ${auction.value.title} at ${auction.value.currentPrice}`)
}

onUnmounted(() => {
    if (route.params.id) {
        socketStore.unsubscribeAuction(route.params.id)
    }
    socketStore.off('price_update')
})
</script>

<template>
  <div v-if="auctionStore.loading" class="flex items-center justify-center min-h-[60vh]">
    <div class="animate-spin h-12 w-12 border-4 border-neon-blue border-t-transparent rounded-full"></div>
  </div>
  
  <div v-else-if="auction" class="max-w-4xl mx-auto py-8 px-4 grid grid-cols-1 md:grid-cols-2 gap-12">
    <!-- Left Column: Visuals & Price -->
    <div class="space-y-8 text-center md:text-left">
      <div class="relative bg-card-bg p-8 rounded-xl border border-neon-blue/30 shadow-[0_0_30px_rgba(0,243,255,0.15)] overflow-hidden">
        <!-- Turbo Indicator -->
        <div v-if="auction.turboActive" class="absolute top-0 left-0 w-full bg-hot-orange text-black font-bold text-center py-1 animate-pulse">
            TURBO MODE ACTIVE 🔥
        </div>
        
        <h2 class="text-gray-400 text-sm tracking-widest uppercase mb-2 mt-4">Current Price</h2>
        <PriceTicker :price="auction.currentPrice" :large="true" />
        
        <div class="mt-8 flex justify-between items-end border-t border-gray-700 pt-4">
            <CountDownTimer :targetTime="auction.nextDropTime" />
            <div class="text-right">
                <span class="block text-xs text-gray-500">Starting Price</span>
                <span class="text-gray-300 line-through">₺{{ auction.startPrice }}</span>
            </div>
        </div>
      </div>
      
      <button 
        @click="handleBook"
        class="w-full bg-gradient-to-r from-neon-blue to-neon-pink p-4 rounded-lg font-bold text-xl text-black hover:scale-[1.02] transform transition-all shadow-lg active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="auction.status !== 'ACTIVE'"
      >
        <span v-if="auction.status === 'ACTIVE'">⚡ HEMEN KAP (BOOK NOW)</span>
        <span v-else>SOLD OUT</span>
      </button>
      
      <p class="text-xs text-center text-gray-500 mt-2">
        * Price locks instantly when you click book. Pay at the venue.
      </p>
    </div>

    <!-- Right Column: Details -->
    <div class="space-y-6">
        <div>
            <h1 class="text-4xl font-bold mb-2 text-white">{{ auction.title }}</h1>
            <div class="flex items-center space-x-2 text-neon-blue">
                <span class="text-lg">Instructed by {{ auction.instructor }}</span>
            </div>
        </div>
        
        <div class="bg-gray-800/50 p-6 rounded-lg">
            <h3 class="font-bold text-gray-300 mb-2">Session Details</h3>
            <p class="text-gray-400 leading-relaxed mb-4">
                {{ auction.description || 'Join us for an intense session focused on core strength and flexibility. Suitable for all levels.' }}
            </p>
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="block text-gray-500">Date</span>
                    <span class="text-white">{{ new Date(auction.startTime).toLocaleDateString() }}</span>
                </div>
                 <div>
                    <span class="block text-gray-500">Time</span>
                    <span class="text-white">{{ new Date(auction.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
                </div>
            </div>
        </div>
        
        <div class="bg-blue-900/20 p-4 rounded border-l-4 border-neon-blue">
            <h4 class="font-bold text-neon-blue mb-1">How it works</h4>
            <p class="text-sm text-gray-300">
                Price drops every few minutes. The longer you wait, the cheaper it gets per person. But wait too long, and someone else might grab it!
            </p>
        </div>
    </div>
  </div>
  
  <div v-else class="text-center py-20">
    <h2 class="text-2xl text-gray-500">Auction not found</h2>
    <router-link to="/" class="text-neon-blue hover:underline mt-4 block">Return Home</router-link>
  </div>
</template>
