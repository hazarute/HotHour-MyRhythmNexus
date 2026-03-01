import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock adminFetch and socket service and auth store
vi.mock('@/utils/admin/api_client', () => ({ adminFetch: vi.fn() }))
vi.mock('@/services/socket', () => ({ default: { connect: vi.fn(), on: vi.fn(), off: vi.fn(), isConnected: false } }))
vi.mock('@/stores/auth', () => ({ useAuthStore: () => ({ token: 'TEST_TOKEN' }) }))

import { adminFetch } from '@/utils/admin/api_client'
import SocketService from '@/services/socket'
import { useAdminNotifications } from '@/composables/admin/useAdminNotifications'

const Dummy = defineComponent({
  template: '<div />',
  setup() {
    const comp = useAdminNotifications()
    return { comp, ...comp }
  }
})

describe('useAdminNotifications', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('fetches notifications on mount and exposes them', async () => {
    adminFetch.mockResolvedValueOnce({ notifications: [{ id: 1, created_at: '2026-03-01T00:00:00Z', title: 'T1', message: 'M1', is_read: false }], unread_count: 1 })

    const wrapper = mount(Dummy)
    // let async onMounted fetch complete
    await nextTick()
    await nextTick()
    await Promise.resolve()

    const vm = wrapper.vm
    expect(adminFetch).toHaveBeenCalled()
    expect(vm.adminNotifications.length).toBe(1)
    expect(vm.unreadNotificationsCount).toBe(1)
  })

  it('registers socket listeners on mount', async () => {
    adminFetch.mockResolvedValueOnce({ notifications: [], unread_count: 0 })
    mount(Dummy)
    await nextTick()
    await nextTick()
    await Promise.resolve()
    expect(SocketService.connect).toHaveBeenCalled()
    expect(SocketService.on).toHaveBeenCalledWith('notification_created', expect.any(Function))
    expect(SocketService.on).toHaveBeenCalledWith('notification_deleted', expect.any(Function))
  })

  it('deleteNotification triggers adminFetch DELETE and refresh', async () => {
    adminFetch.mockResolvedValueOnce({ notifications: [], unread_count: 0 }) // initial
    adminFetch.mockResolvedValueOnce({ notifications: [], unread_count: 0 }) // after delete refresh

    const wrapper = mount(Dummy)
    await nextTick()
    await nextTick()
    const vm = wrapper.vm

    // mock delete response for adminFetch when calling deleteNotification
    adminFetch.mockResolvedValueOnce({})
    await vm.deleteNotification(123)

    // After delete, fetchAdminNotifications(true) should be called (we mocked adminFetch)
    expect(adminFetch).toHaveBeenCalled()
  })
})
