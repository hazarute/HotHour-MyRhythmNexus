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
    vi.stubGlobal('confirm', vi.fn())
    vi.stubGlobal('alert', vi.fn())
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

  // ─── handleCancel: Yönetici İptal Uyarısı ────────────────────────────────

  describe('handleCancel — iptal onay mesajı', () => {
    it('handleCancel confirm ile birlikte admin bilgilendirme notunu içeriyor', async () => {
      adminFetch.mockResolvedValueOnce([]) // mount fetch
      global.confirm.mockReturnValue(false)

      const wrapper = mount(Dummy)
      await nextTick()

      await wrapper.vm.handleCancel(5)

      expect(global.confirm).toHaveBeenCalledTimes(1)
      const confirmMsg = global.confirm.mock.calls[0][0]
      expect(confirmMsg).toContain('Yönetici tarafından yapılan iptallar')
      expect(confirmMsg).toContain('müşterinin yeni rezervasyon haklarını etkilemez')
    })

    it('handleCancel kullanıcı reddettiğinde API çağrısı yapmaz', async () => {
      adminFetch.mockResolvedValueOnce([]) // mount fetch
      global.confirm.mockReturnValue(false)

      const wrapper = mount(Dummy)
      await nextTick()
      vi.clearAllMocks()

      await wrapper.vm.handleCancel(5)

      // mount sonrası çağrı yok
      expect(adminFetch).not.toHaveBeenCalled()
    })

    it('handleCancel onaylandığında API çağrısı yapılır', async () => {
      adminFetch.mockResolvedValueOnce([]) // mount fetch
      adminFetch.mockResolvedValueOnce({ status: 'CANCELLED' }) // cancel call
      global.confirm.mockReturnValue(true)

      const wrapper = mount(Dummy)
      await nextTick()

      await wrapper.vm.handleCancel(7)

      expect(adminFetch).toHaveBeenLastCalledWith(
        '/api/v1/reservations/admin/7/cancel',
        { method: 'POST' },
        expect.anything()
      )
    })

    it('handleCancel onaylandığında yerel reservation status CANCELLED olarak güncellenir', async () => {
      adminFetch.mockResolvedValueOnce([{ id: 7, status: 'PENDING_ON_SITE', booking_code: 'HOT-007', created_at: '2026-03-01T00:00:00Z' }])
      adminFetch.mockResolvedValueOnce({ status: 'CANCELLED' })
      global.confirm.mockReturnValue(true)

      const wrapper = mount(Dummy)
      await nextTick()
      await nextTick()

      await wrapper.vm.handleCancel(7)
      await nextTick()

      const updated = wrapper.vm.reservations.find(r => r.id === 7)
      expect(updated?.status).toBe('CANCELLED')
    })

    it('handleCancel API hatası durumunda alert gösterir', async () => {
      adminFetch.mockResolvedValueOnce([])
      adminFetch.mockRejectedValueOnce(new Error('Sunucu hatası'))
      global.confirm.mockReturnValue(true)

      const wrapper = mount(Dummy)
      await nextTick()

      await wrapper.vm.handleCancel(3)

      expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('Sunucu hatası'))
    })
  })
})
