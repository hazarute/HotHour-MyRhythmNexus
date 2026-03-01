import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { adminFetch } from '@/utils/admin/api_client'
import { useAuthStore } from '@/stores/auth'
import { sortReservationsByNewest } from '@/utils/sorting'
import SocketService from '@/services/socket'

export function useAdminReservations() {
    const authStore = useAuthStore()

    const reservations = ref([])
    const loading = ref(false)
    const error = ref(null)

    // Form controls & pagination
    const searchQuery = ref('')
    const statusFilter = ref('ALL')
    const currentPage = ref(1)
    const pageSize = 15

    const showFilterDropdown = ref(false)

    // Fetch
    const fetchReservations = async (silent = false) => {
        if (!silent) loading.value = true
        error.value = null
        try {
            const payload = await adminFetch('/api/v1/reservations/admin/all', {}, authStore)
            reservations.value = Array.isArray(payload) ? payload : (payload.reservations || [])
        } catch (err) {
            console.error('Rezervasyonlar getirilemedi:', err)
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    // Realtime: listen for reservation events and refresh
    onMounted(() => {
        if (!SocketService.isConnected) SocketService.connect()

        const handleCreated = async (payload) => {
            // payload may contain reservation or reservation_id
            await fetchReservations(true)
        }

        const handleUpdated = async (payload) => {
            await fetchReservations(true)
        }

        SocketService.on('reservation_created', handleCreated)
        SocketService.on('reservation_updated', handleUpdated)
        SocketService.on('reservation_cancelled', handleUpdated)

        // Initial fetch
        ;(async () => {
            try {
                await fetchReservations()
            } catch (err) {
                // ignore
            }
        })()
    })

    onUnmounted(() => {
        SocketService.off('reservation_created')
        SocketService.off('reservation_updated')
        SocketService.off('reservation_cancelled')
    })

    // Filter logic
    const filteredReservations = computed(() => {
        let result = [...reservations.value]

        if (statusFilter.value !== 'ALL') {
            result = result.filter(res => String(res.status || '').toUpperCase() === statusFilter.value)
        }

        if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase()
            result = result.filter(res => 
                String(res.booking_code || '').toLowerCase().includes(query) ||
                String(res.user_name || '').toLowerCase().includes(query) ||
                String(res.auction_title || '').toLowerCase().includes(query)
            )
        }
        return sortReservationsByNewest(result)
    })

    // Computed values
    const totalPages = computed(() => {
        const pages = Math.ceil(filteredReservations.value.length / pageSize)
        return pages > 0 ? pages : 1
    })

    const paginatedReservations = computed(() => {
        const start = (currentPage.value - 1) * pageSize
        const end = start + pageSize
        return filteredReservations.value.slice(start, end)
    })

    const shownStart = computed(() => {
        if (filteredReservations.value.length === 0) return 0
        return (currentPage.value - 1) * pageSize + 1
    })

    const shownEnd = computed(() => {
        if (filteredReservations.value.length === 0) return 0
        return Math.min(currentPage.value * pageSize, filteredReservations.value.length)
    })

    watch([searchQuery, statusFilter], () => {
        currentPage.value = 1
    })

    watch(filteredReservations, () => {
        if (currentPage.value > totalPages.value) {
            currentPage.value = totalPages.value
        }
    })

    const goToPrevPage = () => {
        if (currentPage.value > 1) {
            currentPage.value -= 1
        }
    }

    const goToNextPage = () => {
        if (currentPage.value < totalPages.value) {
            currentPage.value += 1
        }
    }

    // Stats
    const totalReservationsCount = computed(() => reservations.value.length)
    const pendingCheckInsCount = computed(() => reservations.value.filter(r => r.status === 'PENDING_ON_SITE' || r.status === 'CONFIRMED').length)
    const checkedInTodayCount = computed(() => reservations.value.filter(r => r.status === 'COMPLETED').length) 

    // Actions
    const handleCheckIn = async (reservationId) => {
        if (!confirm('Bu rezervasyonu giriş yapıldı olarak işaretlemek istiyor musunuz?')) return
        
        try {
            await adminFetch(`/api/v1/reservations/admin/${reservationId}/check-in`, { method: 'POST' }, authStore)
            
            const index = reservations.value.findIndex(r => r.id === reservationId)
            if (index !== -1) {
                reservations.value[index].status = 'COMPLETED'
            }
        } catch (err) {
            alert('Hata: ' + err.message)
        }
    }

    const handleCancel = async (reservationId) => {
        if (!confirm('Bu rezervasyonu iptal etmek istiyor musunuz?')) return
        
        try {
            await adminFetch(`/api/v1/reservations/admin/${reservationId}/cancel`, { method: 'POST' }, authStore)

            const index = reservations.value.findIndex(r => r.id === reservationId)
            if (index !== -1) {
                reservations.value[index].status = 'CANCELLED'
            }
        } catch (err) {
            alert('Hata: ' + err.message)
        }
    }

    return {
        // State
        reservations,
        loading,
        error,
        searchQuery,
        statusFilter,
        showFilterDropdown,
        currentPage,
        pageSize,

        // Computed
        filteredReservations,
        paginatedReservations,
        totalPages,
        shownStart,
        shownEnd,
        totalReservationsCount,
        pendingCheckInsCount,
        checkedInTodayCount,

        // Actions
        fetchReservations,
        goToPrevPage,
        goToNextPage,
        handleCheckIn,
        handleCancel
    }
}
