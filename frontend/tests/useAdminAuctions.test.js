import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock styles and stores
const auctionStore = { auctions: [], fetchAuctions: vi.fn(), updatePrice: vi.fn(), updateAuctionStatus: vi.fn(), updateAuctionTurboStartedAt: vi.fn() }
vi.mock('@/stores/auction', () => ({ useAuctionStore: () => auctionStore }))
vi.mock('@/stores/auth', () => ({ useAuthStore: vi.fn(() => ({ user: { studioId: 1 } })) }))
vi.mock('@/services/socket', () => ({ default: { connect: vi.fn(), on: vi.fn(), off: vi.fn(), subscribeAuction: vi.fn(), unsubscribeAuction: vi.fn(), isConnected: false } }))

import SocketService from '@/services/socket'
import { useAdminAuctions } from '@/composables/admin/useAdminAuctions'

const Dummy = defineComponent({
  template: '<div />',
  setup() {
    const comp = useAdminAuctions()
    return { comp }
  }
})

describe('useAdminAuctions (realtime)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('connects socket and registers handlers on mount', async () => {
    const wrapper = mount(Dummy)
    await nextTick()
    expect(SocketService.connect).toHaveBeenCalled()
    expect(SocketService.on).toHaveBeenCalledWith('price_update', expect.any(Function))
    expect(SocketService.on).toHaveBeenCalledWith('auction_booked', expect.any(Function))
    expect(SocketService.on).toHaveBeenCalledWith('turbo_triggered', expect.any(Function))
  })

  it('uses locked_price for sold totalRevenue', async () => {
    // Simulate sold auction with current_price farklı, locked_price doğru değer
    auctionStore.auctions = [{
      id: 1,
      studioId: 1,
      status: 'SOLD',
      current_price: 3846.76,
      locked_price: 5128.98
    }]

    const wrapper = mount(Dummy)
    await nextTick()

    expect(wrapper.vm.comp.totalRevenue.value).toBeCloseTo(5128.98)
    expect(wrapper.vm.comp.avgSoldPrice.value).toBeCloseTo(5128.98)
  })
})
