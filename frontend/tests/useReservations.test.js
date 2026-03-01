import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// --- Mocks ---
const mockPush = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push: mockPush }) }))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    token: 'TEST_TOKEN',
    logout: vi.fn()
  })
}))

// Global fetch mock
global.fetch = vi.fn()

// Clipboard API mock
Object.defineProperty(global.navigator, 'clipboard', {
  value: { writeText: vi.fn().mockResolvedValue(undefined) },
  writable: true
})

import { useReservations } from '@/composables/useReservations'

const Dummy = defineComponent({
  template: '<div />',
  setup() {
    const comp = useReservations()
    return { comp, ...comp }
  }
})

describe('useReservations', () => {

  beforeEach(() => {
    vi.resetAllMocks()
    global.fetch = vi.fn()
    navigator.clipboard.writeText = vi.fn().mockResolvedValue(undefined)
  })

  // ─── Başlangıç state ──────────────────────────────────────────────────────

  describe('initial state', () => {
    it('reservations boş dizi ile başlar', () => {
      const wrapper = mount(Dummy)
      expect(wrapper.vm.reservations).toEqual([])
    })

    it('loading false ile başlar', () => {
      const wrapper = mount(Dummy)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('error null ile başlar', () => {
      const wrapper = mount(Dummy)
      expect(wrapper.vm.error).toBeNull()
    })

    it('copiedReservationId null ile başlar', () => {
      const wrapper = mount(Dummy)
      expect(wrapper.vm.copiedReservationId).toBeNull()
    })

    it('cancellingReservationId null ile başlar', () => {
      const wrapper = mount(Dummy)
      expect(wrapper.vm.cancellingReservationId).toBeNull()
    })

    it('confirmCancelReservationId null ile başlar', () => {
      const wrapper = mount(Dummy)
      expect(wrapper.vm.confirmCancelReservationId).toBeNull()
    })
  })

  // ─── fetchMyReservations ──────────────────────────────────────────────────

  describe('fetchMyReservations', () => {
    it('başarılı fetch sonrası rezervasyonları doldurur', async () => {
      const mockData = {
        reservations: [
          { id: 1, booking_code: 'HOT-1234', status: 'PENDING_ON_SITE' },
          { id: 2, booking_code: 'HOT-5678', status: 'COMPLETED' }
        ]
      }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const wrapper = mount(Dummy)
      await wrapper.vm.fetchMyReservations()
      await nextTick()

      expect(wrapper.vm.reservations.length).toBe(2)
      expect(wrapper.vm.reservations[0].booking_code).toBe('HOT-1234')
      expect(wrapper.vm.loading).toBe(false)
      expect(wrapper.vm.error).toBeNull()
    })

    it('network hatası durumunda error set edilir', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      const wrapper = mount(Dummy)
      await wrapper.vm.fetchMyReservations()
      await nextTick()

      expect(wrapper.vm.error).toBe('Network error')
      expect(wrapper.vm.loading).toBe(false)
    })

    it('401 yanıtında logout ve login yönlendirmesi yapılır', async () => {
      global.fetch.mockResolvedValueOnce({ ok: false, status: 401 })

      const wrapper = mount(Dummy)
      await wrapper.vm.fetchMyReservations()
      await nextTick()

      expect(mockPush).toHaveBeenCalledWith('/login')
    })

    it('fetch sırasında loading true olur, bittikten sonra false döner', async () => {
      let resolveFetch
      global.fetch.mockReturnValueOnce(
        new Promise((res) => { resolveFetch = res })
      )

      const wrapper = mount(Dummy)
      const fetchPromise = wrapper.vm.fetchMyReservations()
      expect(wrapper.vm.loading).toBe(true)
      resolveFetch({ ok: true, json: async () => ({ reservations: [] }) })
      await fetchPromise
      expect(wrapper.vm.loading).toBe(false)
    })

    it('non-401 hata için custom error message set edilir', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.reject()
      })

      const wrapper = mount(Dummy)
      await wrapper.vm.fetchMyReservations()

      expect(wrapper.vm.error).toContain('getirilemedi')
    })
  })

  // ─── openCancelConfirmation / closeCancelConfirmation ─────────────────────

  describe('cancel confirmation akışı', () => {
    it('openCancelConfirmation ID\'yi set eder', () => {
      const wrapper = mount(Dummy)
      wrapper.vm.openCancelConfirmation(42)
      expect(wrapper.vm.confirmCancelReservationId).toBe(42)
    })

    it('openCancelConfirmation feedback state\'ini sıfırlar', () => {
      const wrapper = mount(Dummy)
      wrapper.vm.cancellationFeedback = { type: 'success', message: 'test' }
      wrapper.vm.openCancelConfirmation(42)
      expect(wrapper.vm.cancellationFeedback).toBeNull()
    })

    it('closeCancelConfirmation ID\'yi null yapar', () => {
      const wrapper = mount(Dummy)
      wrapper.vm.openCancelConfirmation(42)
      wrapper.vm.closeCancelConfirmation()
      expect(wrapper.vm.confirmCancelReservationId).toBeNull()
    })
  })

  // ─── cancelReservation ────────────────────────────────────────────────────

  describe('cancelReservation', () => {
    it('confirmCancelReservationId eşleşmezse işlemi iptal eder', async () => {
      const wrapper = mount(Dummy)
      wrapper.vm.openCancelConfirmation(99) // Farklı ID
      await wrapper.vm.cancelReservation(42) // Eşleşmeyen ID
      expect(global.fetch).not.toHaveBeenCalled()
    })

    it('başarılı iptal sonrası rezervasyonları yeniden getirir', async () => {
      // İptal isteği başarılı
      global.fetch.mockResolvedValueOnce({ ok: true })
      // Sonrasındaki fetchMyReservations
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ reservations: [] })
      })

      const wrapper = mount(Dummy)
      wrapper.vm.openCancelConfirmation(42)
      await wrapper.vm.cancelReservation(42)

      expect(global.fetch).toHaveBeenCalledTimes(2)
      expect(wrapper.vm.cancellationFeedback.type).toBe('success')
      expect(wrapper.vm.confirmCancelReservationId).toBeNull()
    })

    it('başarılı iptal sonrası success mesajı set edilir', async () => {
      global.fetch.mockResolvedValueOnce({ ok: true })
      global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({ reservations: [] }) })

      const wrapper = mount(Dummy)
      wrapper.vm.openCancelConfirmation(42)
      await wrapper.vm.cancelReservation(42)

      expect(wrapper.vm.cancellationFeedback.type).toBe('success')
      expect(wrapper.vm.cancellationFeedback.message).toBeTruthy()
    })

    it('iptal hatası durumunda error feedback set edilir', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Sunucu hatası' })
      })

      const wrapper = mount(Dummy)
      wrapper.vm.openCancelConfirmation(42)
      await wrapper.vm.cancelReservation(42)

      expect(wrapper.vm.cancellationFeedback.type).toBe('error')
      expect(wrapper.vm.cancellingReservationId).toBeNull()
    })

    it('iptal 401 dönerse logout + redirect yapılır', async () => {
      global.fetch.mockResolvedValueOnce({ ok: false, status: 401 })

      const wrapper = mount(Dummy)
      wrapper.vm.openCancelConfirmation(42)
      await wrapper.vm.cancelReservation(42)

      expect(mockPush).toHaveBeenCalledWith('/login')
    })
  })

  // ─── copyBookingCode ──────────────────────────────────────────────────────

  describe('copyBookingCode', () => {
    it('clipboard.writeText ile kod kopyalar', async () => {
      const wrapper = mount(Dummy)
      await wrapper.vm.copyBookingCode(1, 'HOT-ABCD')
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('HOT-ABCD')
    })

    it('kopyalama sonrası copiedReservationId set edilir', async () => {
      const wrapper = mount(Dummy)
      await wrapper.vm.copyBookingCode(1, 'HOT-ABCD')
      expect(wrapper.vm.copiedReservationId).toBe(1)
    })

    it('boş kod için kopyalama yapmaz', async () => {
      const wrapper = mount(Dummy)
      await wrapper.vm.copyBookingCode(1, '')
      expect(navigator.clipboard.writeText).not.toHaveBeenCalled()
    })

    it('null kod için kopyalama yapmaz', async () => {
      const wrapper = mount(Dummy)
      await wrapper.vm.copyBookingCode(1, null)
      expect(navigator.clipboard.writeText).not.toHaveBeenCalled()
    })

    it('kod trim edilir', async () => {
      const wrapper = mount(Dummy)
      await wrapper.vm.copyBookingCode(1, '  HOT-TRIM  ')
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('HOT-TRIM')
    })
  })

  // ─── Dönen API yapısı ─────────────────────────────────────────────────────

  describe('dönen obje yapısı', () => {
    it('tüm beklenen state alanlarını içerir', () => {
      const result = (() => {
        let r
        mount(defineComponent({
          template: '<div />',
          setup() { r = useReservations(); return {} }
        }))
        return r
      })()

      expect(result).toHaveProperty('reservations')
      expect(result).toHaveProperty('loading')
      expect(result).toHaveProperty('error')
      expect(result).toHaveProperty('copiedReservationId')
      expect(result).toHaveProperty('cancellingReservationId')
      expect(result).toHaveProperty('confirmCancelReservationId')
      expect(result).toHaveProperty('cancellationFeedback')
      expect(result).toHaveProperty('cancellationFeedbackReservationId')
    })

    it('tüm beklenen action fonksiyonlarını içerir', () => {
      const result = (() => {
        let r
        mount(defineComponent({
          template: '<div />',
          setup() { r = useReservations(); return {} }
        }))
        return r
      })()

      expect(typeof result.fetchMyReservations).toBe('function')
      expect(typeof result.cancelReservation).toBe('function')
      expect(typeof result.copyBookingCode).toBe('function')
      expect(typeof result.openCancelConfirmation).toBe('function')
      expect(typeof result.closeCancelConfirmation).toBe('function')
    })
  })

})
