import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAdminStudio } from '@/composables/admin/useAdminStudio'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('useAdminStudio composable', () => {
  let mockAuthStore;

  beforeEach(() => {
    setActivePinia(createPinia())
    mockAuthStore = {
      user: {
        studioId: 1,
        studio: {}
      },
      fetchWithAuth: vi.fn()
    }
    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('initializes with default empty values', () => {
    const { studio, loading, error, successMessage } = useAdminStudio()
    expect(studio.value).toEqual({
      name: '',
      address: '',
      logoUrl: '',
      googleMapsUrl: ''
    })
    expect(loading.value).toBe(false)
    expect(error.value).toBe('')
    expect(successMessage.value).toBe('')
  })

  it('fetchStudio sets error if user has no studioId', async () => {
    mockAuthStore.user.studioId = null
    const { error, fetchStudio } = useAdminStudio()
    await fetchStudio()
    expect(error.value).toBe('Hesabınıza bağlı bir stüdyo bulunmamaktadır.')
  })

  it('fetchStudio fetches studio data successfully', async () => {
    mockAuthStore.fetchWithAuth.mockResolvedValue({
      name: 'Test Studio',
      address: 'Test Address',
      logoUrl: 'http://logo',
      googleMapsUrl: 'http://maps'
    })
    const { studio, loading, fetchStudio } = useAdminStudio()

    const fetchPromise = fetchStudio()
    expect(loading.value).toBe(true)
    await fetchPromise

    expect(loading.value).toBe(false)
    expect(studio.value).toEqual({
      name: 'Test Studio',
      address: 'Test Address',
      logoUrl: 'http://logo',
      googleMapsUrl: 'http://maps'
    })
  })

  it('fetchStudio handles errors', async () => {
    mockAuthStore.fetchWithAuth.mockRejectedValue(new Error('Network Error'))
    const { error, loading, fetchStudio } = useAdminStudio()
    
    await fetchStudio()

    expect(loading.value).toBe(false)
    expect(error.value).toBe('Network Error')
  })

  it('updateStudio updates studio data successfully', async () => {
    mockAuthStore.fetchWithAuth.mockResolvedValue({
      name: 'Updated Studio',
      address: 'Updated Address',
      logoUrl: 'http://logo2',
      googleMapsUrl: 'http://maps2'
    })
    const { studio, successMessage, updateStudio } = useAdminStudio()

    vi.useFakeTimers()
    const result = await updateStudio()

    expect(result).toBe(true)
    expect(successMessage.value).toBe('Stüdyo bilgileri başarıyla güncellendi!')
    expect(studio.value.name).toBe('Updated Studio')
    expect(mockAuthStore.user.studio.name).toBe('Updated Studio')

    vi.advanceTimersByTime(3000)
    expect(successMessage.value).toBe('')
    vi.useRealTimers()
  })

  it('updateStudio handles errors', async () => {
    mockAuthStore.fetchWithAuth.mockRejectedValue(new Error('Update failed'))
    const { error, updateStudio } = useAdminStudio()

    const result = await updateStudio()

    expect(result).toBe(false)
    expect(error.value).toBe('Update failed')
  })

  it('uploadLogo uploads successfully', async () => {
    mockAuthStore.fetchWithAuth.mockResolvedValue({
      logoUrl: 'http://uploaded-logo'
    })
    const { studio, successMessage, uploadLogo } = useAdminStudio()

    vi.useFakeTimers()
    const file = new File(['content'], 'logo.png', { type: 'image/png' })
    const result = await uploadLogo(file)

    expect(result).toBe(true)
    expect(successMessage.value).toBe('Logo başarıyla yüklendi!')
    expect(studio.value.logoUrl).toBe('http://uploaded-logo')
    expect(mockAuthStore.user.studio.logoUrl).toBe('http://uploaded-logo')

    vi.advanceTimersByTime(3000)
    expect(successMessage.value).toBe('')
    vi.useRealTimers()
  })

  it('uploadLogo handles errors', async () => {
    mockAuthStore.fetchWithAuth.mockRejectedValue(new Error('Upload failed'))
    const { error, uploadLogo } = useAdminStudio()

    const file = new File(['content'], 'logo.png', { type: 'image/png' })
    const result = await uploadLogo(file)

    expect(result).toBe(false)
    expect(error.value).toBe('Upload failed')
  })
})
