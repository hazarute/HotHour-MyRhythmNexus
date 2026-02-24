<script setup>
import { ref, onMounted, computed } from 'vue'
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

const totalAuctions = computed(() => store.auctions.length)
const activeAuctions = computed(() => store.auctions.filter((a) => a.status === 'ACTIVE').length)
const soldAuctions = computed(() => store.auctions.filter((a) => a.status === 'SOLD').length)

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString('tr-TR', { 
        month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit' 
    })
}
</script>

<template>
    <div class="space-y-6">
        <div class="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div>
                <h2 class="text-3xl font-black text-white tracking-tight">Auctions Dashboard</h2>
                <p class="text-slate-400 text-sm mt-1">Create and monitor live session auctions in one place.</p>
            </div>
            <button
                @click="showForm = !showForm"
                class="hh-btn-primary"
            >
                <span v-if="!showForm">+ New Auction</span>
                <span v-else>Close Form</span>
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="hh-glass-card rounded-xl p-4 border-l-4 border-neon-blue">
                <p class="text-xs text-slate-400 uppercase tracking-wider mb-1">Total Auctions</p>
                <p class="text-3xl font-bold text-white">{{ totalAuctions }}</p>
            </div>
            <div class="hh-glass-card rounded-xl p-4 border-l-4 border-neon-green">
                <p class="text-xs text-slate-400 uppercase tracking-wider mb-1">Active</p>
                <p class="text-3xl font-bold text-neon-green">{{ activeAuctions }}</p>
            </div>
            <div class="hh-glass-card rounded-xl p-4 border-l-4 border-neon-magenta">
                <p class="text-xs text-slate-400 uppercase tracking-wider mb-1">Sold</p>
                <p class="text-3xl font-bold text-neon-magenta">{{ soldAuctions }}</p>
            </div>
        </div>

        <!-- Create Form Section -->
        <transition enter-active-class="transition duration-300 ease-out" enter-from-class="transform -translate-y-4 opacity-0" enter-to-class="transform translate-y-0 opacity-100" leave-active-class="transition duration-200 ease-in" leave-from-class="transform translate-y-0 opacity-100" leave-to-class="transform -translate-y-4 opacity-0">
            <div v-if="showForm" class="hh-card p-4 md:p-6">
                <AuctionCreateForm @create-auction="handleCreate" />
            </div>
        </transition>

        <!-- Error State -->
        <div v-if="store.error" class="hh-card border-red-500/60 bg-red-900/30 text-red-100 p-4">
            {{ store.error }}
        </div>

        <!-- Auction List Table -->
        <div class="hh-card overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead class="bg-dark-bg/60 border-b border-slate-700">
                        <tr>
                            <th class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Session</th>
                            <th class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Schedule</th>
                            <th class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Cur. Price</th>
                            <th class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Floor</th>
                            <th class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                            <th class="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800">
                        <tr v-for="auction in store.auctions" :key="auction.id" class="hover:bg-white/5 transition-colors group">
                            <td class="p-4">
                                <div class="font-medium text-white group-hover:text-neon-blue transition-colors">{{ auction.title }}</div>
                                <div class="text-xs text-slate-500 font-mono">ID: {{ auction.id }}</div>
                            </td>
                            <td class="p-4 text-sm text-slate-300">
                                <div>{{ formatDate(auction.start_time || auction.startTime) }}</div>
                            </td>
                            <td class="p-4 text-sm">
                                <span class="text-neon-pink font-bold font-mono text-lg">{{ auction.current_price || auction.currentPrice || auction.start_price }} ₺</span>
                            </td>
                             <td class="p-4 text-sm text-slate-500 font-mono">
                                {{ auction.floor_price || auction.floorPrice }} ₺
                            </td>
                            <td class="p-4">
                                <span class="px-2 py-1 text-xs font-bold border rounded uppercase bg-opacity-10 bg-current inline-block text-center min-w-[80px]"
                                    :class="{
                                        'text-green-400 border-green-400': auction.status === 'ACTIVE',
                                        'text-blue-300 border-blue-300': auction.status === 'DRAFT',
                                        'text-gray-500 border-gray-500': auction.status === 'EXPIRED' || auction.status === 'CANCELLED',
                                        'text-neon-pink border-neon-pink': auction.status === 'SOLD'
                                    }">
                                    {{ auction.status }}
                                </span>
                                 <div v-if="auction.turbo_active" class="mt-1 text-[10px] text-neon-pink animate-pulse font-bold tracking-widest uppercase">⚡ Turbo</div>
                            </td>
                            <td class="p-4 text-right">
                                                                 <RouterLink :to="`/auction/${auction.id}`" class="text-slate-400 hover:text-white transition-colors">
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
