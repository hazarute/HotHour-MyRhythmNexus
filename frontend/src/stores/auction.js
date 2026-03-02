import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

const normalizeBaseUrl = (value) => {
    if (!value || typeof value !== 'string') return ''
    return value.trim().replace(/\/+$/, '')
}

const getPrimaryApiBase = () => {
    return normalizeBaseUrl(import.meta.env.VITE_API_URL)
}

const getSameOriginBase = () => {
    if (typeof window === 'undefined' || !window.location?.origin) return ''
    return normalizeBaseUrl(window.location.origin)
}

export const useAuctionStore = defineStore('auction', () => {
    // State
    const auctions = ref([])
    const currentAuction = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const pendingBookingAuctionId = ref(null)

    // Actions
    async function fetchAuctions() {
        loading.value = true
        error.value = null
        try {
            const authStore = useAuthStore()
            let response
            const primaryBase = getPrimaryApiBase()
            const sameOriginBase = getSameOriginBase()

            if (authStore && typeof authStore.fetchWithAuth === 'function') {
                response = await authStore.fetchWithAuth('/api/v1/auctions/?include_computed=true')
            } else {
                if (!primaryBase) {
                    throw new Error('VITE_API_URL tanımlı değil')
                }

                try {
                    response = await fetch(`${primaryBase}/api/v1/auctions/?include_computed=true`)
                } catch (networkError) {
                    if (!sameOriginBase) throw networkError
                    response = await fetch(`${sameOriginBase}/api/v1/auctions/?include_computed=true`)
                }
            }

            if (!response.ok) {
                throw new Error('Failed to fetch auctions')
            }
            auctions.value = await response.json()
        } catch (err) {
            error.value = err?.message || 'Bağlantı hatası oluştu'
            console.error("Failed to fetch auctions:", err)
        } finally {
            loading.value = false
        }
    }

    async function fetchAuctionById(id) {
        loading.value = true
        error.value = null
        try {
            const authStore = useAuthStore()
            let response
            if (authStore && typeof authStore.fetchWithAuth === 'function') {
                response = await authStore.fetchWithAuth(`/api/v1/auctions/${id}`)
            } else {
                const primaryBase = getPrimaryApiBase()
                if (!primaryBase) {
                    throw new Error('VITE_API_URL tanımlı değil')
                }
                response = await fetch(`${primaryBase}/api/v1/auctions/${id}`)
            }
            if (!response.ok) {
                throw new Error('Failed to fetch auction details')
            }
            currentAuction.value = await response.json()
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    function updatePrice(auctionId, newPrice) {
        // Update in list
        const index = auctions.value.findIndex(a => a.id == auctionId)
        if (index !== -1) {
            auctions.value[index].currentPrice = newPrice
            auctions.value[index].current_price = newPrice
            auctions.value[index].computedPrice = newPrice
        }
        // Update current view if matches
        if (currentAuction.value && currentAuction.value.id == auctionId) {
            currentAuction.value.currentPrice = newPrice
            currentAuction.value.current_price = newPrice
            currentAuction.value.computedPrice = newPrice
        }
    }

    function updateAuctionStatus(auctionId, newStatus) {
        const index = auctions.value.findIndex(a => a.id == auctionId)
        if (index !== -1) {
            auctions.value[index].status = newStatus
        }

        if (currentAuction.value && currentAuction.value.id == auctionId) {
            currentAuction.value.status = newStatus
        }
    }

    function updateAuctionTurboStartedAt(auctionId, turboStartedAt) {
        const index = auctions.value.findIndex(a => a.id == auctionId)
        if (index !== -1) {
            auctions.value[index].turboStartedAt = turboStartedAt
            auctions.value[index].turbo_started_at = turboStartedAt
            auctions.value[index].turboActive = true
        }

        if (currentAuction.value && currentAuction.value.id == auctionId) {
            currentAuction.value.turboStartedAt = turboStartedAt
            currentAuction.value.turbo_started_at = turboStartedAt
            currentAuction.value.turboActive = true
        }
    }

    function handleAuctionCreated(auction) {
        if (!auctions.value.find(a => a.id === auction.id)) {
            auctions.value.push(auction)
        }
    }

    function handleAuctionUpdated(auction) {
        const index = auctions.value.findIndex(a => a.id === auction.id)
        if (index !== -1) {
            auctions.value[index] = { ...auctions.value[index], ...auction }
        } else {
            auctions.value.push(auction)
        }
        if (currentAuction.value && currentAuction.value.id === auction.id) {
            currentAuction.value = { ...currentAuction.value, ...auction }
        }
    }

    function handleAuctionDeleted(auctionId) {
        auctions.value = auctions.value.filter(a => a.id !== auctionId)
        if (currentAuction.value && currentAuction.value.id === auctionId) {
            // we could either clear it or let the view handle it
            currentAuction.value = null
        }
    }

    async function createAuction(payload) {
        const authStore = useAuthStore()
        
        loading.value = true
        error.value = null
        try {
            let response
            if (authStore && typeof authStore.fetchWithAuth === 'function') {
                response = await authStore.fetchWithAuth('/api/v1/auctions/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
            } else {
                const primaryBase = getPrimaryApiBase()
                if (!primaryBase) throw new Error('VITE_API_URL tanımlı değil')
                response = await fetch(`${primaryBase}/api/v1/auctions/`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` }, body: JSON.stringify(payload) })
            }

            if (!response.ok) {
                const errData = await response.json()
                throw new Error(errData.detail || 'Failed to create auction')
            }

            const newAuction = await response.json()
            auctions.value.push(newAuction)
            return newAuction
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    async function updateAuction(payload) {
        const authStore = useAuthStore()
        loading.value = true
        error.value = null
        
        try {
            // const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            // Extract id from payload
            const { id, ...data } = payload
            if (!id) throw new Error("Auction ID is required for update")

            let response
            if (authStore && typeof authStore.fetchWithAuth === 'function') {
                response = await authStore.fetchWithAuth(`/api/v1/auctions/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
            } else {
                const primaryBase = getPrimaryApiBase()
                if (!primaryBase) throw new Error('VITE_API_URL tanımlı değil')
                response = await fetch(`${primaryBase}/api/v1/auctions/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` }, body: JSON.stringify(data) })
            }

            if (!response.ok) {
                const errData = await response.json()
                throw new Error(errData.detail || 'Failed to update auction')
            }

            const updated = await response.json()
            // Update local list
            const index = auctions.value.findIndex(a => a.id === id)
            if (index !== -1) {
                auctions.value[index] = { ...auctions.value[index], ...updated }
            }
            return updated
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    async function cancelAuction(auctionId) {
        return await updateAuction({ id: auctionId, status: 'CANCELLED' })
    }

    async function deleteAuction(auctionId) {
        const authStore = useAuthStore()
        loading.value = true
        error.value = null

        try {
            let response
            if (authStore && typeof authStore.fetchWithAuth === 'function') {
                response = await authStore.fetchWithAuth(`/api/v1/auctions/${auctionId}`, { method: 'DELETE' })
            } else {
                const primaryBase = getPrimaryApiBase()
                if (!primaryBase) throw new Error('VITE_API_URL tanımlı değil')
                response = await fetch(`${primaryBase}/api/v1/auctions/${auctionId}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${authStore.token}` } })
            }

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}))
                throw new Error(errData.detail || 'Failed to delete auction')
            }

            auctions.value = auctions.value.filter(a => a.id !== auctionId)
            return true
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    async function bookAuction(auctionId) {
        const authStore = useAuthStore()
        
        if (!authStore.isAuthenticated) {
            throw new Error("You must be logged in to book a session.")
        }

        if (authStore.isAdmin) {
            throw new Error("Admin kullanıcılar rezervasyon yapamaz.")
        }
        
        pendingBookingAuctionId.value = auctionId
        error.value = null
        try {
            const payload = {
                auction_id: auctionId,
                user_id: authStore.user.id
            }

            let response
            if (authStore && typeof authStore.fetchWithAuth === 'function') {
                response = await authStore.fetchWithAuth('/api/v1/reservations/book', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
            } else {
                const primaryBase = getPrimaryApiBase()
                if (!primaryBase) throw new Error('VITE_API_URL tanımlı değil')
                response = await fetch(`${primaryBase}/api/v1/reservations/book`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authStore.token}` }, body: JSON.stringify(payload) })
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                // Handle specific race condition error 409
                if (response.status === 409) {
                    throw new Error("Sorry! Someone just booked this session seconds ago.")
                }
                throw new Error(errorData.detail || 'Booking failed')
            }

            const reservation = await response.json()
            // Delay status update to next tick so AuctionCard can emit 'booking-success'
            // before Vue removes it from the filtered list (activeAuctions)
            if (currentAuction.value && currentAuction.value.id === auctionId) {
                currentAuction.value.status = 'SOLD'
            }
            setTimeout(() => updateAuctionStatus(auctionId, 'SOLD'), 0)
            return reservation
        } catch (err) {
            console.error("Booking error:", err)
            error.value = err.message
            throw err
        } finally {
            pendingBookingAuctionId.value = null
        }
    }

    return {
        auctions,
        currentAuction,
        loading,
        error,
        pendingBookingAuctionId,
        fetchAuctions,
        fetchAuctionById,
        createAuction,
        updateAuction,
        cancelAuction,
        deleteAuction,
        bookAuction,
        updatePrice,
        updateAuctionStatus,
        updateAuctionTurboStartedAt,
        handleAuctionCreated,
        handleAuctionUpdated,
        handleAuctionDeleted
    }
})
