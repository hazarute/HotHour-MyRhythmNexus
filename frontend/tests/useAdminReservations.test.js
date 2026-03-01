import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/utils/admin/api_client', () => ({ adminFetch: vi.fn() }))
vi.mock('@/services/socket', () => ({ default: { connect: vi.fn(), on: vi.fn(), off: vi.fn(), isConnected: false } }))
vi.mock('@/stores/auth', () => ({ useAuthStore: () => ({ token: 'TEST_TOKEN' }) }))

import { adminFetch } from '@/utils/admin/api_client'
import SocketService from '@/services/socket'
import { useAdminReservations } from '@/composables/admin/useAdminReservations'

const Dummy = defineComponent({
  template: '<div />',
  setup() {
    const comp = useAdminReservations()
    return { comp, ...comp }
  }
})

describe('useAdminReservations', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('fetches reservations on mount and exposes them', async () => {
    adminFetch.mockResolvedValueOnce([{ id: 1, booking_code: 'ABC', created_at: '2026-03-01T00:00:00Z' }])
    const wrapper = mount(Dummy)
    await nextTick()
    await nextTick()
    await Promise.resolve()
    const vm = wrapper.vm
    expect(adminFetch).toHaveBeenCalled()
    expect(vm.paginatedReservations.length).toBeGreaterThanOrEqual(0)
  })

  it('registers socket listeners for reservations', async () => {
    adminFetch.mockResolvedValueOnce([])
    mount(Dummy)
    await nextTick()
    expect(SocketService.connect).toHaveBeenCalled()
    expect(SocketService.on).toHaveBeenCalledWith('reservation_created', expect.any(Function))
    expect(SocketService.on).toHaveBeenCalledWith('reservation_updated', expect.any(Function))
    expect(SocketService.on).toHaveBeenCalledWith('reservation_cancelled', expect.any(Function))
  })
})
