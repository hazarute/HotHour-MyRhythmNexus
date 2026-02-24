<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const reservations = ref([])
const loading = ref(false)
const error = ref(null)

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
  <div class="max-w-4xl mx-auto py-8 px-4">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white tracking-tight">My Reservations</h1>
        <router-link to="/" class="text-neon-blue hover:underline text-sm">Back to Home</router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin h-10 w-10 border-4 border-neon-blue border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="bg-red-900/20 border border-red-500 text-red-200 p-4 rounded-lg mb-6 max-w-lg mx-auto text-center">
        {{ error }}
        <button @click="fetchMyReservations" class="block mx-auto mt-2 text-sm underline">Try Again</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="reservations.length === 0" class="text-center py-20 bg-card-bg/50 rounded-xl border border-gray-800">
        <div class="text-6xl mb-4 opacity-50">🎫</div>
        <h2 class="text-xl text-gray-300 mb-2">No reservations yet</h2>
        <p class="text-gray-500 mb-6">You haven't booked any sessions yet. Check out what's hot now!</p>
        <router-link to="/" class="bg-neon-blue text-black font-bold py-2 px-6 rounded hover:bg-blue-400 transition-colors inline-block">
            View Live Auctions
        </router-link>
    </div>

    <!-- Reservations List -->
    <div v-else class="space-y-4">
        <div v-for="res in reservations" :key="res.id" 
             class="bg-card-bg border border-gray-700 rounded-lg p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-neon-blue/50 transition-colors shadow-lg">
            
            <!-- Context -->
            <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                    <span class="text-xs font-bold px-2 py-0.5 rounded bg-gray-800 text-gray-400 uppercase tracking-wider">
                        {{ res.status }}
                    </span>
                    <span class="text-xs text-gray-500">
                        booked on {{ formatDate(res.reserved_at) }}
                    </span>
                </div>
                
                <h3 class="text-xl font-bold text-white mb-1 group-hover:text-neon-blue transition-colors">
                    {{ res.auction_title || 'Unknown Session' }}
                </h3>
                
                <div class="text-sm text-gray-400 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    {{ formatDate(res.auction_start_time) }}
                </div>
            </div>

            <!-- Price & Code -->
            <div class="text-right w-full md:w-auto bg-gray-900/50 p-3 rounded-lg border border-gray-800 min-w-[140px]">
                <div class="text-xs text-gray-500 uppercase tracking-wider mb-1">Booking Code</div>
                <div class="font-mono text-2xl font-bold text-neon-green tracking-widest leading-none mb-2">
                    {{ res.booking_code }}
                </div>
                <div class="text-sm font-bold text-white border-t border-gray-700 pt-1 mt-1">
                    Locked: ₺{{ res.locked_price }}
                </div>
            </div>
        
        </div>
    </div>
  </div>
</template>
