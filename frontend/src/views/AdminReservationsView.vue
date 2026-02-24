<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const reservations = ref([])
const loading = ref(false)
const searchQuery = ref('')
const error = ref(null)

const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Fetch all reservations
const fetchReservations = async () => {
    loading.value = true
    error.value = null
    try {
        const response = await fetch(`${baseUrl}/api/v1/reservations/admin/all`, {
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })
        
        if (!response.ok) {
            throw new Error('Failed to fetch reservations')
        }
        
        const payload = await response.json()
        reservations.value = Array.isArray(payload) ? payload : (payload.reservations || [])
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
        String(res.booking_code || '').toLowerCase().includes(query) ||
        String(res.user_name || '').toLowerCase().includes(query) ||
        String(res.auction_title || '').toLowerCase().includes(query)
    )
})

const formatDate = (value) => {
    if (!value) return '-'
    return new Date(value).toLocaleString('tr-TR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const statusClass = (status) => {
    if (status === 'COMPLETED' || status === 'CONFIRMED') return 'hh-badge-success'
    if (status === 'PENDING_ON_SITE') return 'hh-badge-live'
    return 'hh-badge-muted'
}

onMounted(() => {
    fetchReservations()
})
</script>

<template>
    <div class="space-y-6">
        <div class="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div>
                <h1 class="text-3xl font-black text-white tracking-tight">Reservations</h1>
                <p class="text-slate-400 text-sm mt-1">Search by booking code, user, or auction to verify arrivals quickly.</p>
            </div>
            <button @click="fetchReservations" class="hh-btn-ghost">Refresh</button>
        </div>

        <div class="relative hh-card p-3">
            <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by Booking Code, User or Auction..."
                class="w-full bg-dark-bg/60 border border-slate-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:outline-none focus:border-neon-blue"
            />
            <div class="absolute left-6 top-1/2 -translate-y-1/2 text-slate-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
        </div>

        <div class="hh-card overflow-hidden">
            <div v-if="loading" class="p-8 text-center text-slate-400">
                Loading reservations...
            </div>

            <div v-else-if="error" class="p-8 text-center text-red-400">
                {{ error }}
            </div>

            <table v-else class="w-full text-left">
                <thead class="bg-dark-bg/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                    <tr>
                        <th class="px-6 py-4 font-medium">Code</th>
                        <th class="px-6 py-4 font-medium">Customer</th>
                        <th class="px-6 py-4 font-medium">Auction</th>
                        <th class="px-6 py-4 font-medium">Price</th>
                        <th class="px-6 py-4 font-medium">Date</th>
                        <th class="px-6 py-4 font-medium">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800">
                    <tr v-for="res in filteredReservations" :key="res.id" class="hover:bg-white/5 transition-colors">
                        <td class="px-6 py-4 hh-code-text font-bold text-neon-green">
                            {{ res.booking_code || '-' }}
                        </td>
                        <td class="px-6 py-4">
                            <div class="text-white">{{ res.user_name || 'Unknown User' }}</div>
                            <div class="text-xs text-slate-500">ID: {{ res.user_id || '-' }}</div>
                        </td>
                        <td class="px-6 py-4 text-slate-300">
                            {{ res.auction_title || '-' }}
                        </td>
                        <td class="px-6 py-4 font-bold text-white">
                            ₺{{ res.locked_price ?? '-' }}
                        </td>
                        <td class="px-6 py-4 text-slate-400 text-sm">
                            {{ formatDate(res.reserved_at || res.created_at) }}
                        </td>
                        <td class="px-6 py-4">
                            <span :class="statusClass(res.status)">
                                {{ res.status || 'UNKNOWN' }}
                            </span>
                        </td>
                    </tr>
                    <tr v-if="filteredReservations.length === 0">
                        <td colspan="6" class="px-6 py-8 text-center text-slate-500">
                            No reservations found.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
