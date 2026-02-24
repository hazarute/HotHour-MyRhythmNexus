<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const reservations = ref([])
const loading = ref(false)
const searchQuery = ref('')
const error = ref(null)

// Fetch all reservations
const fetchReservations = async () => {
    loading.value = true
    error.value = null
    try {
        const response = await fetch('/api/v1/reservations/admin/all', {
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })
        
        if (!response.ok) {
            throw new Error('Failed to fetch reservations')
        }
        
        reservations.value = await response.json()
    } catch (err) {
        console.error(err)
        error.value = err.message
    } finally {
        loading.value = false
    }
}

// Filtered list
const filteredReservations = computed(() => {
    if (!searchQuery.value) return reservations.value
    
    const query = searchQuery.value.toLowerCase()
    return reservations.value.filter(res => 
        res.booking_code.toLowerCase().includes(query) ||
        res.user_name.toLowerCase().includes(query) ||
        res.auction_title.toLowerCase().includes(query)
    )
})

onMounted(() => {
    fetchReservations()
})
</script>

<template>
    <div class="space-y-6">
        <div class="flex justify-between items-center">
            <h1 class="text-3xl font-bold text-white">Reservations</h1>
            <button @click="fetchReservations" class="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-sm text-white">
                Refresh
            </button>
        </div>
        
        <!-- Search -->
        <div class="relative">
            <input 
                v-model="searchQuery"
                type="text" 
                placeholder="Search by Booking Code, User or Auction..." 
                class="w-full bg-card-bg border border-gray-700 rounded-lg py-3 px-4 text-white focus:outline-none focus:border-neon-blue"
            >
            <div class="absolute right-3 top-3 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
        </div>

        <!-- Reservations Table -->
        <div class="bg-card-bg rounded-lg border border-gray-700 overflow-hidden">
            <div v-if="loading" class="p-8 text-center text-gray-400">
                Loading reservations...
            </div>
            
            <div v-else-if="error" class="p-8 text-center text-red-400">
                {{ error }}
            </div>
            
            <table v-else class="w-full text-left">
                <thead class="bg-gray-800 text-gray-400 text-xs uppercase tracking-wider">
                    <tr>
                        <th class="px-6 py-4 font-medium">Code</th>
                        <th class="px-6 py-4 font-medium">Customer</th>
                        <th class="px-6 py-4 font-medium">Auction</th>
                        <th class="px-6 py-4 font-medium">Price</th>
                        <th class="px-6 py-4 font-medium">Date</th>
                        <th class="px-6 py-4 font-medium">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-700">
                    <tr v-for="res in filteredReservations" :key="res.id" class="hover:bg-white/5 transition-colors">
                        <td class="px-6 py-4 font-mono font-bold text-neon-green">
                            {{ res.booking_code }}
                        </td>
                        <td class="px-6 py-4">
                            <div class="text-white">{{ res.user_name }}</div>
                            <div class="text-xs text-gray-500">ID: {{ res.user_id }}</div>
                        </td>
                        <td class="px-6 py-4 text-gray-300">
                            {{ res.auction_title }}
                        </td>
                        <td class="px-6 py-4 font-bold text-white">
                            ₺{{ res.locked_price }}
                        </td>
                        <td class="px-6 py-4 text-gray-400 text-sm">
                            {{ new Date(res.created_at).toLocaleString() }}
                        </td>
                                                <td class="px-6 py-4">
                            <span 
                                class="px-2 py-1 rounded text-xs font-bold"
                                :class="{
                                    'bg-green-900 text-green-300': res.status === 'CONFIRMED' || res.status === 'COMPLETED',
                                    'bg-red-900 text-red-300': res.status === 'CANCELLED' || res.status === 'NO_SHOW',
                                    'bg-yellow-900 text-yellow-300': res.status === 'PENDING_ON_SITE'
                                }"
                            >
                                {{ res.status }}
                            </span>
                        </td>
                    </tr>
                    <tr v-if="filteredReservations.length === 0">
                        <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                            No reservations found.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
