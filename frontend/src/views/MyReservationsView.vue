<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const reservations = ref([])
const loading = ref(false)
const error = ref(null)

const statusLabel = (status) => {
    if (!status) return 'Pending'
    return String(status).replaceAll('_', ' ').toLowerCase().replace(/(^|\s)\S/g, (s) => s.toUpperCase())
}

const isCompleted = (status) => {
    return ['COMPLETED', 'NO_SHOW', 'CANCELLED'].includes(status)
}

const fetchMyReservations = async () => {
    loading.value = true
    error.value = null
    try {
        if (!authStore.token) {
            router.push('/login')
            return
        }

        const baseUrl = import.meta.env.VITE_API_URL || ''
        const response = await fetch(`${baseUrl}/api/v1/reservations/my/all`, {
            headers: {
                'Authorization': `Bearer ${authStore.token}`
            }
        })
        
        if (!response.ok) {
            if (response.status === 401) {
                authStore.logout()
                router.push('/login')
                return
            }
            throw new Error('Failed to fetch reservations')
        }
        
        const data = await response.json()
        reservations.value = data.reservations // The API returns wrapped dict {reservations: [...]}
    } catch (err) {
        console.error(err)
        error.value = err.message
    } finally {
        loading.value = false
    }
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString('en-US', {
        month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'
    })
}

onMounted(() => {
    fetchMyReservations()
})
</script>

<template>
    <div class="hh-section max-w-5xl py-8 lg:py-12">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-800 pb-6 mb-8">
            <div>
                <h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">My Reservations</h1>
                <p class="text-slate-400 text-base mt-2">Your upcoming Pilates sessions and booking history.</p>
            </div>
            <router-link to="/" class="hh-btn-ghost text-sm">Back to Arena</router-link>
        </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin h-10 w-10 border-4 border-neon-blue border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="hh-card border-red-500/60 bg-red-900/20 text-red-200 p-4 mb-6 max-w-lg mx-auto text-center">
        {{ error }}
        <button @click="fetchMyReservations" class="block mx-auto mt-2 text-sm underline">Try Again</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="reservations.length === 0" class="hh-card text-center py-20">
        <div class="text-6xl mb-4 opacity-50">🎫</div>
        <h2 class="text-xl text-gray-300 mb-2">No reservations yet</h2>
        <p class="text-gray-500 mb-6">You haven't booked any sessions yet. Check out what's hot now!</p>
        <router-link to="/" class="hh-btn-neon">
            View Live Auctions
        </router-link>
    </div>

    <!-- Reservations List -->
        <div v-else class="space-y-6">
        <div v-for="res in reservations" :key="res.id" 
                             class="group relative overflow-hidden rounded-xl bg-card-bg border border-slate-700 hover:border-primary/50 transition-all duration-300 shadow-sm hover:shadow-glow">
            
                        <div class="absolute top-0 left-0 w-1 h-full" :class="isCompleted(res.status) ? 'bg-slate-500' : 'bg-neon-green shadow-[0_0_10px_2px_rgba(54,211,153,0.5)]'"></div>

                        <div class="flex flex-col md:flex-row">
                            <div class="flex-1 p-6 flex flex-col justify-between gap-6">
                                <div>
                                    <div class="flex items-center gap-2 mb-2">
                                        <span :class="isCompleted(res.status) ? 'hh-badge-muted' : 'hh-badge-success'">
                                            {{ statusLabel(res.status) }}
                                        </span>
                                        <span class="text-xs text-slate-500">Booked {{ formatDate(res.reserved_at) }}</span>
                                    </div>

                                    <h3 class="text-xl font-bold text-white mb-1 group-hover:text-neon-blue transition-colors">
                                        {{ res.auction_title || 'Pilates Session' }}
                                    </h3>

                                    <div class="text-sm text-slate-400 flex items-center gap-2">
                                        <span>📍</span>
                                        <span>Studio Location</span>
                                    </div>
                </div>

                                <div class="grid grid-cols-2 gap-4 border-t border-slate-800 pt-4 mt-1 text-sm">
                                    <div>
                                        <p class="text-xs text-slate-500 uppercase tracking-wider mb-1">Date & Time</p>
                                        <p class="font-medium text-slate-200">{{ formatDate(res.auction_start_time) }}</p>
                                    </div>
                                    <div>
                                        <p class="text-xs text-slate-500 uppercase tracking-wider mb-1">Locked Price</p>
                                        <p class="font-medium text-slate-200">₺{{ res.locked_price }}</p>
                                    </div>
                                </div>
                            </div>

                            <div class="md:w-[260px] bg-slate-900/60 p-6 flex flex-col items-center justify-center border-y md:border-y-0 md:border-l border-slate-700 relative overflow-hidden">
                                <div class="absolute inset-0 opacity-[0.04]" style="background-image: radial-gradient(#36d399 1px, transparent 1px); background-size: 10px 10px;"></div>
                <div class="text-xs text-gray-500 uppercase tracking-wider mb-1">Booking Code</div>
                                <div class="hh-code-text text-3xl font-bold leading-none mb-2" :class="isCompleted(res.status) ? 'text-slate-500 line-through' : 'text-neon-green'">
                    {{ res.booking_code }}
                </div>
                                <div class="text-[10px] text-slate-400 text-center max-w-[150px]">
                                        Show this code at the front desk for check-in
                </div>
                            </div>

                            <div class="md:w-[180px] p-3 flex flex-col gap-2">
                                <div class="h-28 w-full rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700"></div>
                                <button class="hh-btn-ghost w-full text-xs uppercase tracking-wide">View Receipt</button>
                            </div>
            </div>
        </div>
    </div>
  </div>
</template>
