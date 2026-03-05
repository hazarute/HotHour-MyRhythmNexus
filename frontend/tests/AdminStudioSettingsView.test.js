import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AdminStudioSettingsView from '@/views/admin/AdminStudioSettingsView.vue'
import { useAdminStudio } from '@/composables/admin/useAdminStudio'
import { ref } from 'vue'

// Mock the child component to prevent related errors
vi.mock('@/components/admin/AdminNotificationDropdown.vue', () => ({
  default: {
    name: 'AdminNotificationDropdown',
    template: '<div class="mock-notification-dropdown"></div>'
  }
}))

// Mock the composable
vi.mock('@/composables/admin/useAdminStudio', () => ({
  useAdminStudio: vi.fn()
}))

describe('AdminStudioSettingsView', () => {
  let mockStudio;
  let mockLoading;
  let mockError;
  let mockSuccessMessage;
  let mockFetchStudio;
  let mockUpdateStudio;
  let mockUploadLogo;

  beforeEach(() => {
    vi.resetAllMocks()

    mockStudio = ref({
      name: '',
      address: '',
      logoUrl: '',
      googleMapsUrl: ''
    })
    mockLoading = ref(false)
    mockError = ref('')
    mockSuccessMessage = ref('')
    mockFetchStudio = vi.fn()
    mockUpdateStudio = vi.fn()
    mockUploadLogo = vi.fn()

    useAdminStudio.mockReturnValue({
      studio: mockStudio,
      loading: mockLoading,
      error: mockError,
      successMessage: mockSuccessMessage,
      fetchStudio: mockFetchStudio,
      updateStudio: mockUpdateStudio,
      uploadLogo: mockUploadLogo
    })
  })

  const createWrapper = () => mount(AdminStudioSettingsView, {
    global: {
      stubs: {
        AdminNotificationDropdown: true
      }
    }
  })

  it('calls fetchStudio on mount', () => {
    createWrapper()
    expect(mockFetchStudio).toHaveBeenCalledTimes(1)
  })

  it('renders default skeleton when studio details are empty', () => {
    const wrapper = createWrapper()
    const nameInput = wrapper.find('input[placeholder="Örn: SoundHub Kadıköy"]')
    expect(nameInput.exists()).toBe(true)
    expect(nameInput.element.value).toBe('')
  })

  it('binds studio data to inputs', async () => {
    mockStudio.value = {
      name: 'Super Studio',
      address: 'Test Mah. No:1',
      logoUrl: 'https://test.com/logo.png',
      googleMapsUrl: 'https://maps.test.com'
    }
    const wrapper = createWrapper()
    
    const nameInput = wrapper.find('input[type="text"][placeholder="Örn: SoundHub Kadıköy"]')
    const addressInput = wrapper.find('textarea')
    
    expect(nameInput.element.value).toBe('Super Studio')
    expect(addressInput.element.value).toBe('Test Mah. No:1')
  })

  it('shows error message if error is present', async () => {
    mockError.value = 'Failed to load studio.'
    const wrapper = createWrapper()
    
    const errorDiv = wrapper.find('.bg-red-50')
    expect(errorDiv.exists()).toBe(true)
    expect(errorDiv.text()).toContain('Failed to load studio.')
  })

  it('shows success message if successMessage is present', async () => {
    mockSuccessMessage.value = 'Saved successfully!'
    const wrapper = createWrapper()
    
    const successDiv = wrapper.find('.bg-emerald-50')
    expect(successDiv.exists()).toBe(true)
    expect(successDiv.text()).toContain('Saved successfully!')
  })

  it('calls updateStudio on form submit', async () => {
    const wrapper = createWrapper()
    
    mockStudio.value.name = 'New Name' // At least name is required
    const form = wrapper.find('form')
    await form.trigger('submit.prevent')
    
    expect(mockUpdateStudio).toHaveBeenCalledTimes(1)
  })

  it('disables buttons when loading', async () => {
    mockLoading.value = true
    const wrapper = createWrapper()
    
    const buttons = wrapper.findAll('button')
    buttons.forEach(button => {
      expect(button.attributes('disabled')).toBeDefined()
    })
  })

  it('shows image placeholder if logo is missing or invalid', async () => {
    mockStudio.value.logoUrl = 'invalid-url'
    const wrapper = createWrapper()
    
    const invalidIcons = wrapper.findAll('.material-symbols-outlined')
    const hasImageText = invalidIcons.some(icon => icon.text() === 'image')
    expect(hasImageText).toBe(true)
  })

  it('re-fetches studio on cancel click', async () => {
    const wrapper = createWrapper()
    
    // fetchStudio is called on mount
    expect(mockFetchStudio).toHaveBeenCalledTimes(1)
    
    const cancelButton = wrapper.find('button[type="button"]')
    await cancelButton.trigger('click')
    
    expect(mockFetchStudio).toHaveBeenCalledTimes(2)
  })

  it('calls uploadLogo when file input changes', async () => {
    const wrapper = createWrapper()
    const fileInput = wrapper.find('input[type="file"]')
    
    Object.defineProperty(fileInput.element, 'files', {
      value: [new File([''], 'logo.png', { type: 'image/png' })]
    })
    
    await fileInput.trigger('change')
    
    expect(mockUploadLogo).toHaveBeenCalledTimes(1)
  })
})
