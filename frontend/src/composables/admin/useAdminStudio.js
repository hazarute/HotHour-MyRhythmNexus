import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAdminStudio() {
    const authStore = useAuthStore()

    const studio = ref({
        name: '',
        address: '',
        logoUrl: '',
        googleMapsUrl: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    const successMessage = ref('')

    const fetchStudio = async () => {
        if (!authStore.user?.studioId) {
            error.value = 'Hesabınıza bağlı bir stüdyo bulunmamaktadır.'
            return
        }

        loading.value = true
        error.value = ''
        successMessage.value = ''

        try {
            const response = await authStore.fetchWithAuth('/api/v1/studios/me')
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}))
                throw new Error(errData.detail || 'Failed to fetch studio info')
            }
            
            const data = await response.json()
            studio.value = {
                name: data.name || '',
                address: data.address || '',
                logoUrl: data.logoUrl || '',
                googleMapsUrl: data.googleMapsUrl || ''
            }
        } catch (err) {
            console.error('[AdminStudio] fetch error:', err)
            error.value = err.message || 'Stüdyo bilgileri alınırken bir hata oluştu.'
        } finally {
            loading.value = false
        }
    }

    const updateStudio = async () => {
        loading.value = true
        error.value = ''
        successMessage.value = ''

        try {
            const response = await authStore.fetchWithAuth('/api/v1/studios/me', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(studio.value)
            })

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}))
                throw new Error(errData.detail || 'Failed to update studio info')
            }

            const data = await response.json()

            studio.value = {
                name: data.name || '',
                address: data.address || '',
                logoUrl: data.logoUrl || '',
                googleMapsUrl: data.googleMapsUrl || ''
            }
            
            // Optionally, we could update the authStore user's embedded studio here
            if (authStore.user.studio) {
                authStore.user.studio = { ...authStore.user.studio, ...data }
            }

            successMessage.value = 'Stüdyo bilgileri başarıyla güncellendi!'
            
            // Hide success message after 3 seconds
            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
            
            return true
        } catch (err) {
            console.error('[AdminStudio] update error:', err)
            error.value = err.message || 'Stüdyo bilgileri güncellenirken bir hata oluştu.'
            return false
        } finally {
            loading.value = false
        }
    }

    const uploadLogo = async (file) => {
        loading.value = true
        error.value = ''
        successMessage.value = ''

        const formData = new FormData()
        formData.append('file', file)

        try {
            const response = await authStore.fetchWithAuth('/api/v1/studios/me/logo', {
                method: 'POST',
                // FormData sets the content-type automatically with boundaries
                body: formData
            })

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}))
                throw new Error(errData.detail || 'Failed to upload logo')
            }

            const data = await response.json()

            studio.value.logoUrl = data.logoUrl || ''

            if (authStore.user.studio) {
                authStore.user.studio.logoUrl = data.logoUrl
            }

            successMessage.value = 'Logo başarıyla yüklendi!'

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)

            return true
        } catch (err) {
            console.error('[AdminStudio] logo upload error:', err)
            error.value = err.message || 'Logo yüklenirken bir hata oluştu.'
            return false
        } finally {
            loading.value = false
        }
    }

    return {
        studio,
        loading,
        error,
        successMessage,
        fetchStudio,
        updateStudio,
        uploadLogo

    }
}

