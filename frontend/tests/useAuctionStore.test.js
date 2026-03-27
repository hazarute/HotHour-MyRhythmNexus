import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { reactive } from 'vue'

let mockAuthStore

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

const buildAuthStore = () => reactive({
  isAuthenticated: true,
  isAdmin: false,
  token: 'TEST_TOKEN',
  user: { id: 7, role: 'USER' },
  fetchWithAuth: vi.fn()
})

describe('useAuctionStore', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    setActivePinia(createPinia())
    mockAuthStore = buildAuthStore()
  })

  it('checkEligibility 400 restriction donerse detail mesajini geri verir', async () => {
    mockAuthStore.fetchWithAuth.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz.' })
    })

    const { useAuctionStore } = await import('@/stores/auction')
    const store = useAuctionStore()
    const result = await store.checkEligibility(15)

    expect(mockAuthStore.fetchWithAuth).toHaveBeenCalledWith('/api/v1/reservations/eligible/15')
    expect(result).toContain('10 gun')
  })

  it('checkEligibility 200 yanitinda null doner', async () => {
    mockAuthStore.fetchWithAuth.mockResolvedValueOnce({ ok: true, json: async () => ({ eligible: true }) })

    const { useAuctionStore } = await import('@/stores/auction')
    const store = useAuctionStore()
    const result = await store.checkEligibility(21)

    expect(result).toBeNull()
  })

  it('bookAuction sektor kisiti gelirse error state set eder ve hatayi firlatir', async () => {
    mockAuthStore.fetchWithAuth.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz.' })
    })

    const { useAuctionStore } = await import('@/stores/auction')
    const store = useAuctionStore()

    await expect(store.bookAuction(99)).rejects.toThrow('Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz.')
    expect(store.error).toContain('10 gun')
    expect(store.pendingBookingAuctionId).toBeNull()
  })

  it('bookAuction basariliysa pending booking sifirlanir ve auction SOLD olur', async () => {
    vi.useFakeTimers()
    mockAuthStore.fetchWithAuth.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, booking_code: 'HOT-0001' })
    })

    const { useAuctionStore } = await import('@/stores/auction')
    const store = useAuctionStore()
    store.auctions = [{ id: 42, status: 'ACTIVE' }]

    const result = await store.bookAuction(42)
    vi.runAllTimers()

    expect(result.booking_code).toBe('HOT-0001')
    expect(store.pendingBookingAuctionId).toBeNull()
    expect(store.auctions.find((item) => item.id === 42)?.status).toBe('SOLD')
    vi.useRealTimers()
  })

  it('bookAuction admin kullaniciyi hemen engeller', async () => {
    mockAuthStore.isAdmin = true

    const { useAuctionStore } = await import('@/stores/auction')
    const store = useAuctionStore()

    await expect(store.bookAuction(5)).rejects.toThrow('Admin kullanıcılar rezervasyon yapamaz.')
    expect(mockAuthStore.fetchWithAuth).not.toHaveBeenCalled()
  })
})