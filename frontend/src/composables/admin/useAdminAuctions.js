import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useAuctionStore } from '@/stores/auction'
import { sortAuctionsByNewest } from '@/utils/sorting'
import SocketService from '@/services/socket'

export function useAdminAuctions() {
    const store = useAuctionStore()
    
    // Filters & Pagination
    const searchQuery = ref('')
    const statusFilter = ref('ALL') // ALL, ACTIVE, SOLD, DRAFT
    const showFilterDropdown = ref(false)
    const currentPage = ref(1)
    const pageSize = 15

    // Fetch
    const fetchAuctions = async () => {
        await store.fetchAuctions()
    }

    // List and Filtering
    const filteredAuctions = computed(() => {
        let result = [...store.auctions]
        
        if (statusFilter.value !== 'ALL') {
            result = result.filter(a => a.status === statusFilter.value)
        }
        
        if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase()
            result = result.filter(a => 
                a.title.toLowerCase().includes(query) || 
                (a.description && a.description.toLowerCase().includes(query)) ||
                String(a.id).includes(query)
            )
        }

        return sortAuctionsByNewest(result)
    })

    const totalPages = computed(() => {
        const pages = Math.ceil(filteredAuctions.value.length / pageSize)
        return pages > 0 ? pages : 1
    })

    const paginatedAuctions = computed(() => {
        const start = (currentPage.value - 1) * pageSize
        const end = start + pageSize
        return filteredAuctions.value.slice(start, end)
    })

    watch([searchQuery, statusFilter], () => {
        currentPage.value = 1
    })

    watch(totalPages, (newTotal) => {
        if (currentPage.value > newTotal) {
            currentPage.value = newTotal
        }
    })

    const goNextPage = () => {
        if (currentPage.value < totalPages.value) {
            currentPage.value += 1
        }
    }

    const goPrevPage = () => {
        if (currentPage.value > 1) {
            currentPage.value -= 1
        }
    }

    // Actions
    const handleCancelAuction = async (auction) => {
        const ok = confirm(`"${auction.title}" oturumunu iptal etmek istiyor musun?`)
        if (!ok) return

        try {
            await store.cancelAuction(auction.id)
            await fetchAuctions()
        } catch (error) {
            alert(error?.message || 'Oturum iptal edilirken bir hata oluştu.')
        }
    }

    const handleDeleteDraftAuction = async (auction) => {
        const ok = confirm(`"${auction.title}" taslak oturumu silinsin mi? Bu işlem geri alınamaz.`)
        if (!ok) return

        try {
            await store.deleteAuction(auction.id)
            await fetchAuctions()
        } catch (error) {
            alert(error?.message || 'Taslak oturum silinirken bir hata oluştu.')
        }
    }

    // Statistics
    const activeAuctionsCount = computed(() => store.auctions.filter((a) => a.status === 'ACTIVE').length)
    const soldAuctionsCount = computed(() => store.auctions.filter((a) => a.status === 'SOLD').length)

    const totalRevenue = computed(() => {
        return store.auctions
            .filter(a => a.status === 'SOLD' && (a.current_price || a.currentPrice))
            .reduce((sum, a) => sum + Number(a.current_price || a.currentPrice), 0)
    })

    const avgSoldPrice = computed(() => {
        if (soldAuctionsCount.value === 0) return 0
        return totalRevenue.value / soldAuctionsCount.value
    })

    const activeBiddersMock = ref(Math.floor(Math.random() * 20) + 5) 

    // ── Realtime socket handlers ───────────────────────────────────────────
    // Defined at composable scope so both onMounted and onUnmounted can reference them.
    const onPriceUpdate = (payload) => {
        if (payload?.auction_id) {
            store.updatePrice(payload.auction_id, payload.current_price)
        }
    }

    const onAuctionBooked = (payload) => {
        if (payload?.auction_id) {
            store.updateAuctionStatus(payload.auction_id, 'SOLD')
        }
    }

    const onTurboTriggered = (payload) => {
        if (payload?.auction_id) {
            store.updateAuctionTurboStartedAt(payload.auction_id, payload.turbo_started_at)
        }
    }

    const onAuctionCreated = (payload) => {
        if (payload?.auction) {
            store.handleAuctionCreated(payload.auction)
            SocketService.subscribeAuction(payload.auction.id)
        }
    }

    const onAuctionUpdated = (payload) => {
        if (payload?.auction) store.handleAuctionUpdated(payload.auction)
    }

    const onAuctionDeleted = (payload) => {
        if (payload?.auction_id) {
            store.handleAuctionDeleted(payload.auction_id)
            SocketService.unsubscribeAuction(payload.auction_id)
        }
    }

    // Realtime socket subscriptions: connect and listen for auction updates when this composable is used
    onMounted(() => {
        if (!SocketService.isConnected) SocketService.connect()

        SocketService.on('price_update', onPriceUpdate)
        SocketService.on('auction_booked', onAuctionBooked)
        SocketService.on('turbo_triggered', onTurboTriggered)
        SocketService.on('auction_created', onAuctionCreated)
        SocketService.on('auction_updated', onAuctionUpdated)
        SocketService.on('auction_deleted', onAuctionDeleted)

        ;(async () => {
            try {
                await fetchAuctions()
                store.auctions.forEach(a => {
                    if (a?.id) SocketService.subscribeAuction(a.id)
                })
            } catch (err) {
                // ignore
            }
        })()
    })

    onUnmounted(() => {
        try {
            store.auctions.forEach(a => {
                if (a?.id) SocketService.unsubscribeAuction(a.id)
            })
        } finally {
            SocketService.off('price_update', onPriceUpdate)
            SocketService.off('auction_booked', onAuctionBooked)
            SocketService.off('turbo_triggered', onTurboTriggered)
            SocketService.off('auction_created', onAuctionCreated)
            SocketService.off('auction_updated', onAuctionUpdated)
            SocketService.off('auction_deleted', onAuctionDeleted)
        }
    })

    return {
        // State
        searchQuery,
        statusFilter,
        showFilterDropdown,
        currentPage,
        pageSize,

        // Computed
        allAuctionsStoreRef: computed(() => store.auctions),
        filteredAuctions,
        paginatedAuctions,
        totalPages,
        activeAuctionsCount,
        soldAuctionsCount,
        totalRevenue,
        avgSoldPrice,
        activeBiddersMock,

        // Actions
        fetchAuctions,
        goNextPage,
        goPrevPage,
        handleCancelAuction,
        handleDeleteDraftAuction
    }
}

// Realtime socket subscriptions: connect and listen for auction updates when this composable is used
// This runs inside the composable's lifecycle so tests and components mount/unmount behave correctly.
