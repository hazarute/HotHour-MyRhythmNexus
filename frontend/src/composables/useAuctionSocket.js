/**
 * useAuctionSocket — Açık artırma socket abonelik mantığı composable'ı.
 *
 * HomeView ve AllAuctionsView'daki tekrar eden socket kurulum/temizlik bloğunu
 * tek bir yerde toplar. Composable, onMounted / onUnmounted yaşam döngüsünü
 * otomatik olarak yönetir.
 *
 * Kullanım (view içinde):
 *   import { useAuctionSocket } from '@/composables/useAuctionSocket'
 *   const store = useAuctionStore()
 *   useAuctionSocket(store)
 */

import { onMounted, onUnmounted } from 'vue'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'

/**
 * @param {ReturnType<typeof useAuctionStore>} [auctionStore]
 *   Dışarıdan verilmezse composable kendi oluşturur.
 */
export function useAuctionSocket(auctionStore) {
  const store = auctionStore ?? useAuctionStore()
  const socketStore = useSocketStore()

  // --- Oturum odalarına abone ol / aboneliği kaldır ---

  const subscribeToAuctionRooms = () => {
    store.auctions.forEach((auction) => {
      if (auction?.id) {
        socketStore.subscribeAuction(auction.id)
      }
    })
  }

  const unsubscribeFromAuctionRooms = () => {
    store.auctions.forEach((auction) => {
      if (auction?.id) {
        socketStore.unsubscribeAuction(auction.id)
      }
    })
  }

  // --- Event handler'lar ---

  const onPriceUpdate = (data) => {
    if (!data?.auction_id) return
    store.updatePrice(data.auction_id, data.current_price)
  }

  const onAuctionBooked = (data) => {
    if (!data?.auction_id) return
    // Kendi bekleyen rezervasyonumuzu yeniden işaretleme
    if (
      store.pendingBookingAuctionId &&
      String(store.pendingBookingAuctionId) === String(data.auction_id)
    ) return
    store.updateAuctionStatus(data.auction_id, 'SOLD')
  }

  const onTurboTriggered = (data) => {
    if (!data?.auction_id) return
    store.updateAuctionTurboStartedAt(data.auction_id, data.turbo_started_at)
  }

  const onAuctionCreated = (data) => {
    if (data?.auction) {
      store.handleAuctionCreated(data.auction)
      socketStore.subscribeAuction(data.auction.id)
    }
  }

  const onAuctionUpdated = (data) => {
    if (data?.auction) store.handleAuctionUpdated(data.auction)
  }

  const onAuctionDeleted = (data) => {
    if (data?.auction_id) {
      store.handleAuctionDeleted(data.auction_id)
      socketStore.unsubscribeAuction(data.auction_id)
    }
  }

  // --- Yaşam döngüsü ---

  onMounted(async () => {
    if (!socketStore.isConnected) {
      socketStore.connect()
    }

    socketStore.on('price_update', onPriceUpdate)
    socketStore.on('auction_booked', onAuctionBooked)
    socketStore.on('turbo_triggered', onTurboTriggered)
    socketStore.on('auction_created', onAuctionCreated)
    socketStore.on('auction_updated', onAuctionUpdated)
    socketStore.on('auction_deleted', onAuctionDeleted)

    await store.fetchAuctions()
    subscribeToAuctionRooms()
  })

  onUnmounted(() => {
    unsubscribeFromAuctionRooms()
    socketStore.off('price_update', onPriceUpdate)
    socketStore.off('auction_booked', onAuctionBooked)
    socketStore.off('turbo_triggered', onTurboTriggered)
    socketStore.off('auction_created', onAuctionCreated)
    socketStore.off('auction_updated', onAuctionUpdated)
    socketStore.off('auction_deleted', onAuctionDeleted)
  })
}
