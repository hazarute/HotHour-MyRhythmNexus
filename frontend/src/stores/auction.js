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
            // TODO: Replace with actual API call
            // const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auctions`)
            // auctions.value = await response.json()
            
            // Mock Data for UI Development
            await new Promise(r => setTimeout(r, 500)) // Fake latency
            auctions.value = [
                {
                    id: 1,
                    title: "Morning Pilates Reformer",
                    instructor: "Esra Hoca",
                    startTime: new Date(Date.now() + 3600000).toISOString(), // 1 hour later
                    startPrice: 500.00,
                    currentPrice: 450.00,
                    status: "ACTIVE",
                    turboActive: false
                },
                {
                    id: 2,
                    title: "Advanced Yoga Flow",
                    instructor: "Can Hoca",
                    startTime: new Date(Date.now() + 7200000).toISOString(), // 2 hours later
                    startPrice: 400.00,
                    currentPrice: 400.00,
                    status: "ACTIVE",
                    turboActive: false
                },
                {
                    id: 3,
                    title: "HIIT Cardio",
                    instructor: "Melis Hoca",
                    startTime: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
                    startPrice: 300.00,
                    currentPrice: 150.00,
                    status: "SOLD",
                    turboActive: true
                }
            ]
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
            // TODO: Replace with actual API call
            // const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auctions/${id}`)
            // currentAuction.value = await response.json()

            // Simulate fetch
            await new Promise(r => setTimeout(r, 300))
            const found = auctions.value.find(a => a.id == id)
            if (found) {
                currentAuction.value = found
            } else {
                // Mock individual fetch if not in list
                currentAuction.value = {
                    id: id,
                    title: "Morning Pilates Reformer (Detail)",
                    description: "A comprehensive energetic morning session to wake up your body.",
                    instructor: "Esra Hoca",
                    startTime: new Date(Date.now() + 3600000).toISOString(),
                    startPrice: 500.00,
                    currentPrice: 385.50,
                    floorPrice: 200.00,
                    status: "ACTIVE",
                    turboActive: false,
                    nextDropTime: new Date(Date.now() + 15000).toISOString() // 15 sec later
                }
            }
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
        }
        // Update current view if matches
        if (currentAuction.value && currentAuction.value.id == auctionId) {
            currentAuction.value.currentPrice = newPrice
        }
    }

    async function createAuction(payload) {
        const authStore = useAuthStore()
        // ... (existing code)
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
        bookAuction,
        updatePrice
    }
})
