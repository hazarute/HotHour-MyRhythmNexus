import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

export const useAuctionStore = defineStore('auction', () => {
    // State
    const auctions = ref([])
    const currentAuction = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // Actions
    async function fetchAuctions() {
        loading.value = true
        error.value = null
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auctions?include_computed=true`)
            if (!response.ok) {
                throw new Error('Failed to fetch auctions')
            }
            auctions.value = await response.json()
        } catch (err) {
            error.value = err.message
            console.error("Failed to fetch auctions:", err)
        } finally {
            loading.value = false
        }
    }

    async function fetchAuctionById(id) {
        loading.value = true
        error.value = null
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auctions/${id}`)
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

    async function createAuction(payload) {
        const authStore = useAuthStore()
        
        loading.value = true
        error.value = null
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            const response = await fetch(`${baseUrl}/api/v1/auctions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.token}`
                },
                body: JSON.stringify(payload)
            })

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
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            // Extract id from payload
            const { id, ...data } = payload
            if (!id) throw new Error("Auction ID is required for update")

            const response = await fetch(`${baseUrl}/api/v1/auctions/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.token}`
                },
                body: JSON.stringify(data)
            })

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
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            const response = await fetch(`${baseUrl}/api/v1/auctions/${auctionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authStore.token}`
                }
            })

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
        
        loading.value = true
        error.value = null
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            const payload = {
                auction_id: auctionId,
                user_id: authStore.user.id
            }

            const response = await fetch(`${baseUrl}/api/v1/reservations/book`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.token}`
                },
                body: JSON.stringify(payload)
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                // Handle specific race condition error 409
                if (response.status === 409) {
                    throw new Error("Sorry! Someone just booked this session seconds ago.")
                }
                throw new Error(errorData.detail || 'Booking failed')
            }

            const reservation = await response.json()
            // Ideally update local auction status to SOLD immediately
            if (currentAuction.value && currentAuction.value.id === auctionId) {
                currentAuction.value.status = 'SOLD'
            }
            updateAuctionStatus(auctionId, 'SOLD')
            return reservation
        } catch (err) {
            console.error("Booking error:", err)
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    return {
        auctions,
        currentAuction,
        loading,
        error,
        fetchAuctions,
        fetchAuctionById,
        createAuction,
        updateAuction,
        cancelAuction,
        deleteAuction,
        bookAuction,
        updatePrice,
        updateAuctionStatus,
        updateAuctionTurboStartedAt
    }
})
