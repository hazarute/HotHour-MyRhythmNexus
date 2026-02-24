import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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

    return {
        auctions,
        currentAuction,
        loading,
        error,
        fetchAuctions,
        fetchAuctionById,
        updatePrice
    }
})
