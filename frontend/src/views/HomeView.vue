<script setup>
import { onMounted } from 'vue'
import { useAuctionStore } from '../stores/auction'
import AuctionCard from '../components/AuctionCard.vue'

const store = useAuctionStore()

onMounted(() => {
  store.fetchAuctions()
})
</script>

<template>
  <div class="home-view max-w-7xl mx-auto py-8 px-4">
    <div class="text-center mb-12">
      <h1 class="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-neon-pink mb-4 animate-pulse-slow">
        HotHour Auctions
      </h1>
      <p class="text-gray-400 text-lg max-w-2xl mx-auto">
        Catch premium sessions at unbeatable dynamic prices. The longer you wait, the lower it gets — until it's gone!
      </p>
    </div>

    <!-- Active Auctions Grid -->
    <!-- Loading State -->
    <div v-if="store.loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-neon-blue"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="bg-red-900/20 border border-red-500 rounded p-4 text-center">
      <p class="text-red-400">{{ store.error }}</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="store.auctions.length === 0" class="text-center text-gray-500 py-12">
      No active auctions at the moment.
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <AuctionCard 
            v-for="auction in store.auctions" 
            :key="auction.id" 
            :auction="auction" 
        />
    </div>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
