import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const mockPush = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push: mockPush }) }))

// Helper to reset localStorage in tests
function clearLocalStorage() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}

import { useAuthStore } from '@/stores/auth'

const Dummy = defineComponent({
  template: '<div />',
  setup() {
    const s = useAuthStore()
    return { s }
  }
})

describe('useAuthStore', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    clearLocalStorage()
    global.fetch = vi.fn()
    // Ensure Pinia is active for store usage in mounted components
    setActivePinia(createPinia())
  })

  it('login stores tokens and user', async () => {
    const fakeTokens = { access_token: 'A1', refresh_token: 'R1' }
    const fakeUser = { id: 1, email: 'a@b.com' }

    // Mock login response
    global.fetch.mockImplementationOnce(() => Promise.resolve({ ok: true, json: async () => fakeTokens }))
    // Mock /me response
    global.fetch.mockImplementationOnce(() => Promise.resolve({ ok: true, json: async () => fakeUser }))

    const wrapper = mount(Dummy)
    const store = wrapper.vm.s
    const ok = await store.login('a@b.com', 'pw')
    await nextTick()

    expect(ok).toBe(true)
    expect(store.token).toBe('A1')
    expect(store.refreshToken).toBe('R1')
    expect(localStorage.getItem('token')).toBe('A1')
    expect(localStorage.getItem('refresh_token')).toBe('R1')
    expect(store.user).toEqual(fakeUser)
  })

  it('refreshTokens exchanges refresh token and updates storage', async () => {
    // seed tokens
    localStorage.setItem('refresh_token', 'R1')
    const wrapper = mount(Dummy)
    const store = wrapper.vm.s
    store.refreshToken = 'R1'

    // Mock /refresh response
    const newTokens = { access_token: 'A2', refresh_token: 'R2' }
    global.fetch.mockImplementationOnce(() => Promise.resolve({ ok: true, json: async () => newTokens }))
    // Mock /me response
    global.fetch.mockImplementationOnce(() => Promise.resolve({ ok: true, json: async () => ({ id: 2, email: 'b@c.com' }) }))

    const ok = await store.refreshTokens()
    expect(ok).toBe(true)
    expect(store.token).toBe('A2')
    expect(store.refreshToken).toBe('R2')
    expect(localStorage.getItem('token')).toBe('A2')
    expect(localStorage.getItem('refresh_token')).toBe('R2')
  })

  it('logout revokes refresh token and clears storage', async () => {
    localStorage.setItem('refresh_token', 'RR')
    const wrapper = mount(Dummy)
    const store = wrapper.vm.s
    store.refreshToken = 'RR'

    global.fetch = vi.fn(() => Promise.resolve({ ok: true }))

    store.logout()
    await nextTick()

    expect(global.fetch).toHaveBeenCalled()
    expect(store.token).toBeNull()
    expect(store.refreshToken).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})
