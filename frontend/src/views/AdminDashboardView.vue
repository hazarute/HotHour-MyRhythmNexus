<script setup>
import { ref, onMounted } from 'vue'
import { useAuctionStore } from '@/stores/auction'
import AuctionCreateForm from '@/components/AuctionCreateForm.vue'
import { RouterLink } from 'vue-router'

const store = useAuctionStore()
const showForm = ref(false)

onMounted(() => {
  store.fetchAuctions()
})

const handleCreate = async (formData) => {
    try {
        console.log("Submitting auction:", formData)
        // Ensure formData is serialized properly if needed
        await store.createAuction(formData)
        showForm.value = false
        // Fetch fresh list
        await store.fetchAuctions()
    } catch (err) {
        alert('Error creating auction: ' + err.message)
    }
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString('tr-TR', { 
        month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit' 
    })
}
</script>

<template>
    <div class="space-y-6">
        <div class="flex justify-between items-center">
            <h2 class="text-2xl font-bold text-white">Auctions Dashboard</h2>
            <button @click="showForm = !showForm" 
                class="bg-neon-blue hover:bg-blue-400 text-dark-bg px-6 py-2 rounded font-bold shadow-lg shadow-neon-blue/20 transition-all flex items-center gap-2">
                <span v-if="!showForm">
                    + New Auction
                </span>
                <span v-else>Close Form</span>
            </button>
        </div>

        <!-- Create Form Section -->
        <transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-4 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-4 opacity-0">
            <div v-if="showForm" class="mb-10">
                <AuctionCreateForm @create-auction="handleCreate" />
            </div>
        </transition>

        <!-- Error State -->
        <div v-if="store.error" class="bg-red-900/50 border border-red-500 text-red-100 p-4 rounded mb-6">
            {{ store.error }}
        </div>

        <!-- Auction List Table -->
        <div class="bg-card-bg rounded-xl shadow-lg border border-gray-800 overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead class="bg-dark-bg/50 border-b border-gray-700">
                        <tr>
                            <th class="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Session</th>
                            <th class="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Schedule</th>
                            <th class="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Cur. Price</th>
                            <th class="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Floor</th>
                            <th class="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Status</th>
                            <th class="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-800">
                        <tr v-for="auction in store.auctions" :key="auction.id" class="hover:bg-white/5 transition-colors group">
                            <td class="p-4">
                                <div class="font-medium text-white group-hover:text-neon-blue transition-colors">{{ auction.title }}</div>
                                <div class="text-xs text-gray-500 font-mono">ID: {{ auction.id }}</div>
                            </td>
                            <td class="p-4 text-sm text-gray-300">
                                <div>{{ formatDate(auction.start_time || auction.startTime) }}</div>
                            </td>
                            <td class="p-4 text-sm">
                                <span class="text-neon-pink font-bold font-mono text-lg">{{ auction.current_price || auction.currentPrice || auction.start_price }} ₺</span>
                            </td>
                             <td class="p-4 text-sm text-gray-500 font-mono">
                                {{ auction.floor_price || auction.floorPrice }} ₺
                            </td>
                            <td class="p-4">
                                <span class="px-2 py-1 text-xs font-bold border rounded uppercase bg-opacity-10 bg-current inline-block text-center min-w-[80px]"
                                    :class="{
                                        'text-green-400 border-green-400': auction.status === 'ACTIVE',
                                        'text-gray-500 border-gray-500': auction.status === 'EXPIRED' || auction.status === 'CANCELLED',
                                        'text-neon-pink border-neon-pink': auction.status === 'SOLD'
                                    }">
                                    {{ auction.status }}
                                </span>
                                 <div v-if="auction.turbo_active" class="mt-1 text-[10px] text-neon-pink animate-pulse font-bold tracking-widest uppercase">⚡ Turbo</div>
                            </td>
                            <td class="p-4 text-right">
                                 <RouterLink :to="`/auction/${auction.id}`" class="text-gray-400 hover:text-white transition-colors">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 ml-auto">
                                      <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                                    </svg>
                                 </RouterLink>
                            </td>
                        </tr>
                        <tr v-if="store.auctions.length === 0">
                            <td colspan="6" class="p-8 text-center text-gray-500 italic">
                                No active auctions found. Create one to get started.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
