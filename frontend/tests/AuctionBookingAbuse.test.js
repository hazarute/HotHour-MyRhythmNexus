import { mount, shallowMount } from '@vue/test-utils'
import { reactive, nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

let mockRouterPush
let mockRoute
let mockAuthStore
let mockAuctionStore
let mockSocketStore

vi.mock('@unhead/vue', () => ({
  useHead: vi.fn()
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockRouterPush, resolve: () => ({ href: '/auctions/1' }) }),
  useRoute: () => mockRoute,
  RouterLink: {
    name: 'RouterLink',
    props: ['to'],
    template: '<a :href="typeof to === \'string\' ? to : \'#\'"><slot /></a>'
  }
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/stores/auction', () => ({
  useAuctionStore: () => mockAuctionStore
}))

vi.mock('@/stores/socket', () => ({
  useSocketStore: () => mockSocketStore
}))

const auctionCardBase = {
  id: 1,
  title: 'Test Fırsat',
  description: 'Aynı sektörde ikinci fırsat',
  allowedGender: 'ANY',
  status: 'ACTIVE',
  currentPrice: 123,
  startPrice: 200,
  endTime: '2026-03-28T09:50:00Z',
  scheduled_at: '2026-03-28T09:50:00Z',
  studio: { name: 'Neon Fit Academy' }
}

const buildAuthStore = () => reactive({
  isAuthenticated: true,
  isAdmin: false,
  token: 'token',
  user: { id: 99, gender: 'FEMALE' },
  fetchWithAuth: vi.fn()
})

const buildAuctionStore = () => reactive({
  checkEligibility: vi.fn().mockResolvedValue(null),
  bookAuction: vi.fn().mockResolvedValue({ id: 55, booking_code: 'HOT-5555' }),
  fetchAuctionById: vi.fn().mockResolvedValue(undefined),
  currentAuction: { ...auctionCardBase },
  loading: false,
  error: null
})

const buildSocketStore = () => ({
  connect: vi.fn(),
  disconnect: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  subscribeAuction: vi.fn(),
  unsubscribeAuction: vi.fn()
})

describe('frontend abuse booking restrictions', () => {
  beforeEach(() => {
    mockRouterPush = vi.fn()
    mockRoute = { params: { id: '1' }, fullPath: '/auctions/1' }
    mockAuthStore = buildAuthStore()
    mockAuctionStore = buildAuctionStore()
    mockSocketStore = buildSocketStore()
    vi.stubGlobal('alert', vi.fn())
    vi.stubGlobal('requestAnimationFrame', (cb) => {
      cb()
      return 1
    })
  })

  it('AuctionCard ayni sektor kisitinda hata panelini gosterir ve rezervasyonu baslatmaz', async () => {
    mockAuctionStore.checkEligibility.mockResolvedValueOnce(
      'Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz.'
    )

    const AuctionCard = (await import('@/components/AuctionCard.vue')).default
    const wrapper = mount(AuctionCard, {
      props: { auction: { ...auctionCardBase } },
      global: {
        stubs: {
          CountDownTimer: { template: '<span>03:53:50</span>' },
          BookingConfirmModal: { template: '<div data-test="booking-confirm-modal" />' },
          HemenKapButton: {
            props: ['disabled', 'loading'],
            emits: ['click'],
            template: '<button data-test="hemen-kap" :disabled="disabled" @click="$emit(\'click\')">Hemen Kap</button>'
          }
        }
      }
    })

    await wrapper.get('[data-test="hemen-kap"]').trigger('click')
    await nextTick()
    await nextTick()

    expect(mockAuctionStore.checkEligibility).toHaveBeenCalledWith(1)
    expect(mockAuctionStore.bookAuction).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Rezervasyon Yapılamıyor')
    expect(wrapper.text()).toContain('10 gun')
  })

  it('AuctionCard giris yapmamis kullaniciyi login yonlendirmesine gonderir', async () => {
    mockAuthStore.isAuthenticated = false

    const AuctionCard = (await import('@/components/AuctionCard.vue')).default
    const wrapper = shallowMount(AuctionCard, {
      props: { auction: { ...auctionCardBase } },
      global: {
        stubs: {
          CountDownTimer: true,
          BookingConfirmModal: true,
          HemenKapButton: {
            emits: ['click'],
            template: '<button data-test="hemen-kap" @click="$emit(\'click\')">Hemen Kap</button>'
          }
        }
      }
    })

    await wrapper.get('[data-test="hemen-kap"]').trigger('click')

    expect(mockRouterPush).toHaveBeenCalled()
    expect(mockAuctionStore.checkEligibility).not.toHaveBeenCalled()
  })

  it('AuctionDetailView ayni sektor kisitini kullaniciya gosterir ve modal acmaz', async () => {
    mockAuctionStore.checkEligibility.mockResolvedValueOnce(
      'Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz.'
    )

    const AuctionDetailView = (await import('@/views/AuctionDetailView.vue')).default
    const wrapper = mount(AuctionDetailView, {
      global: {
        stubs: {
          'router-link': { template: '<a><slot /></a>' },
          BookingConfirmModal: { template: '<div data-test="booking-confirm-modal" />' },
          BookingSuccessModal: { template: '<div data-test="booking-success-modal" />' },
          HemenKapButton: {
            props: ['disabled', 'loading'],
            emits: ['click', 'disabled-click'],
            template: '<button data-test="detail-hemen-kap" :disabled="disabled" @click="$emit(\'click\')">Hemen Kap</button>'
          }
        }
      }
    })

    await nextTick()
    await nextTick()
    await wrapper.get('[data-test="detail-hemen-kap"]').trigger('click')
    await nextTick()
    await nextTick()

    expect(mockAuctionStore.fetchAuctionById).toHaveBeenCalledWith('1')
    expect(mockAuctionStore.checkEligibility).toHaveBeenCalledWith(1)
    expect(mockAuctionStore.bookAuction).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Rezervasyon Yapılamıyor')
    expect(wrapper.text()).toContain('10 gun')
  })
})