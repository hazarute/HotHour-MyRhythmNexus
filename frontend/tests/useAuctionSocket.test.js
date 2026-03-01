import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'

const { mockSocketStore, mockAuctionStore } = vi.hoisted(() => {
  const mockSocketStore = {
    isConnected: false,
    connect: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    subscribeAuction: vi.fn(),
    unsubscribeAuction: vi.fn()
  }
  const mockAuctionStore = {
    auctions: [{ id: 1, status: 'ACTIVE' }, { id: 2, status: 'ACTIVE' }],
    fetchAuctions: vi.fn().mockResolvedValue(undefined),
    updatePrice: vi.fn(),
    updateAuctionStatus: vi.fn(),
    updateAuctionTurboStartedAt: vi.fn(),
    handleAuctionCreated: vi.fn(),
    handleAuctionUpdated: vi.fn(),
    handleAuctionDeleted: vi.fn(),
    pendingBookingAuctionId: null
  }
  return { mockSocketStore, mockAuctionStore }
})

vi.mock('@/stores/socket', () => ({ useSocketStore: () => mockSocketStore }))
vi.mock('@/stores/auction', () => ({ useAuctionStore: () => mockAuctionStore }))

import { useAuctionSocket } from '@/composables/useAuctionSocket'

const Dummy = defineComponent({
  template: '<div />',
  setup() {
    useAuctionSocket(mockAuctionStore)
    return {}
  }
})

describe('useAuctionSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuctionStore.fetchAuctions = vi.fn().mockResolvedValue(undefined)
    mockAuctionStore.pendingBookingAuctionId = null
    mockAuctionStore.auctions = [{ id: 1, status: 'ACTIVE' }, { id: 2, status: 'ACTIVE' }]
  })

  describe('onMounted', () => {
    it('connect cagirilir', async () => {
      mount(Dummy)
      await nextTick()
      expect(mockSocketStore.connect).toHaveBeenCalled()
    })

    it('fetchAuctions cagirilir', async () => {
      mount(Dummy)
      await nextTick()
      await nextTick()
      expect(mockAuctionStore.fetchAuctions).toHaveBeenCalled()
    })

    it('price_update handler kaydedilir', async () => {
      mount(Dummy)
      await nextTick()
      expect(mockSocketStore.on).toHaveBeenCalledWith('price_update', expect.any(Function))
    })

    it('auction_booked handler kaydedilir', async () => {
      mount(Dummy)
      await nextTick()
      expect(mockSocketStore.on).toHaveBeenCalledWith('auction_booked', expect.any(Function))
    })

    it('turbo_triggered handler kaydedilir', async () => {
      mount(Dummy)
      await nextTick()
      expect(mockSocketStore.on).toHaveBeenCalledWith('turbo_triggered', expect.any(Function))
    })

    it('auction_created handler kaydedilir', async () => {
      mount(Dummy)
      await nextTick()
      expect(mockSocketStore.on).toHaveBeenCalledWith('auction_created', expect.any(Function))
    })

    it('auction_updated handler kaydedilir', async () => {
      mount(Dummy)
      await nextTick()
      expect(mockSocketStore.on).toHaveBeenCalledWith('auction_updated', expect.any(Function))
    })

    it('auction_deleted handler kaydedilir', async () => {
      mount(Dummy)
      await nextTick()
      expect(mockSocketStore.on).toHaveBeenCalledWith('auction_deleted', expect.any(Function))
    })

    it('subscribeAuction her auction icin cagirilir', async () => {
      mount(Dummy)
      await nextTick()
      await nextTick()
      await Promise.resolve()
      expect(mockSocketStore.subscribeAuction).toHaveBeenCalledWith(1)
      expect(mockSocketStore.subscribeAuction).toHaveBeenCalledWith(2)
    })
  })

  describe('onUnmounted', () => {
    it('tum handlerlar off ile kaldirilir', async () => {
      const wrapper = mount(Dummy)
      await nextTick()
      await nextTick()
      await Promise.resolve()
      wrapper.unmount()
      expect(mockSocketStore.off).toHaveBeenCalledWith('price_update', expect.any(Function))
      expect(mockSocketStore.off).toHaveBeenCalledWith('auction_booked', expect.any(Function))
      expect(mockSocketStore.off).toHaveBeenCalledWith('turbo_triggered', expect.any(Function))
      expect(mockSocketStore.off).toHaveBeenCalledWith('auction_created', expect.any(Function))
      expect(mockSocketStore.off).toHaveBeenCalledWith('auction_updated', expect.any(Function))
      expect(mockSocketStore.off).toHaveBeenCalledWith('auction_deleted', expect.any(Function))
    })

    it('unsubscribeAuction cagirilir', async () => {
      const wrapper = mount(Dummy)
      await nextTick()
      await nextTick()
      await Promise.resolve()
      wrapper.unmount()
      expect(mockSocketStore.unsubscribeAuction).toHaveBeenCalledWith(1)
      expect(mockSocketStore.unsubscribeAuction).toHaveBeenCalledWith(2)
    })

    it('auction_booked sadece bir kez off edilir', async () => {
      const wrapper = mount(Dummy)
      await nextTick()
      wrapper.unmount()
      const offCalls = mockSocketStore.off.mock.calls.filter(([event]) => event === 'auction_booked')
      expect(offCalls.length).toBe(1)
    })
  })

  describe('event handler davranislari', () => {
    it('price_update auction_id yoksa updatePrice cagirilmaz', async () => {
      mount(Dummy)
      await nextTick()
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'price_update')
      expect(calls.length).toBeGreaterThan(0)
      calls[0][1]({})
      expect(mockAuctionStore.updatePrice).not.toHaveBeenCalled()
    })

    it('price_update auction_id varsa updatePrice cagirilir', async () => {
      mount(Dummy)
      await nextTick()
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'price_update')
      calls[0][1]({ auction_id: 5, current_price: 300 })
      expect(mockAuctionStore.updatePrice).toHaveBeenCalledWith(5, 300)
    })

    it('auction_created handler odaya subscribe olur', async () => {
      mount(Dummy)
      await nextTick()
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'auction_created')
      calls[0][1]({ auction: { id: 99 } })
      expect(mockAuctionStore.handleAuctionCreated).toHaveBeenCalledWith({ id: 99 })
      expect(mockSocketStore.subscribeAuction).toHaveBeenCalledWith(99)
    })

    it('auction_deleted handler odadan unsubscribe olur', async () => {
      mount(Dummy)
      await nextTick()
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'auction_deleted')
      calls[0][1]({ auction_id: 7 })
      expect(mockAuctionStore.handleAuctionDeleted).toHaveBeenCalledWith(7)
      expect(mockSocketStore.unsubscribeAuction).toHaveBeenCalledWith(7)
    })

    it('auction_updated auction store metodunu cagirip gunceller', async () => {
      mount(Dummy)
      await nextTick()
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'auction_updated')
      calls[0][1]({ auction: { id: 3, status: 'ACTIVE' } })
      expect(mockAuctionStore.handleAuctionUpdated).toHaveBeenCalledWith({ id: 3, status: 'ACTIVE' })
    })

    it('turbo_triggered turbo bilgisini gunceller', async () => {
      mount(Dummy)
      await nextTick()
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'turbo_triggered')
      calls[0][1]({ auction_id: 3, turbo_started_at: '2026-03-01T10:00:00Z' })
      expect(mockAuctionStore.updateAuctionTurboStartedAt).toHaveBeenCalledWith(3, '2026-03-01T10:00:00Z')
    })

    it('auction_booked kendi rezervasyonunu atlar', async () => {
      mount(Dummy)
      await nextTick()
      mockAuctionStore.pendingBookingAuctionId = '5'
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'auction_booked')
      calls[0][1]({ auction_id: 5 })
      expect(mockAuctionStore.updateAuctionStatus).not.toHaveBeenCalled()
    })

    it('auction_booked baskasi icin SOLD olarak gunceller', async () => {
      mount(Dummy)
      await nextTick()
      mockAuctionStore.pendingBookingAuctionId = null
      const calls = mockSocketStore.on.mock.calls.filter(([e]) => e === 'auction_booked')
      calls[0][1]({ auction_id: 5 })
      expect(mockAuctionStore.updateAuctionStatus).toHaveBeenCalledWith(5, 'SOLD')
    })
  })
})
