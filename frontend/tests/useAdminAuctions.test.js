import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock auction store and socket
vi.mock('@/stores/auction', () => ({ useAuctionStore: () => ({ auctions: [], fetchAuctions: vi.fn(), updatePrice: vi.fn(), updateAuctionStatus: vi.fn(), updateAuctionTurboStartedAt: vi.fn() }) }))
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
    vi.resetAllMocks()
  })

  it('connects socket and registers handlers on mount', async () => {
    const wrapper = mount(Dummy)
    await nextTick()
    expect(SocketService.connect).toHaveBeenCalled()
    expect(SocketService.on).toHaveBeenCalledWith('price_update', expect.any(Function))
    expect(SocketService.on).toHaveBeenCalledWith('auction_booked', expect.any(Function))
    expect(SocketService.on).toHaveBeenCalledWith('turbo_triggered', expect.any(Function))
  })
})
