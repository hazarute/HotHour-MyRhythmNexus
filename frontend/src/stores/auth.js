import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
    const router = useRouter()
    
    // State
    const user = ref(JSON.parse(localStorage.getItem('user')) || null)
    const token = ref(localStorage.getItem('token') || null)
    const loading = ref(false)
    const error = ref(null)

    // Getters
    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'ADMIN' || user.value?.role === 'SUPERUSER')

    // Actions
    async function login(email, password) {
        loading.value = true
        error.value = null
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
            
            // NOTE: Using JSON body for this specific endpoint implementation
            const response = await fetch(`${baseUrl}/api/v1/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            })

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}))
                throw new Error(errData.detail || 'Login failed')
            }

            const data = await response.json()
            
            // Set State
            token.value = data.access_token
            // Ideally decode token or fetch /me to get user details
            // For now, we'll fetch the user profile immediately
            await fetchUserProfile(data.access_token)

            // Persist
            localStorage.setItem('token', token.value)
            
            return true
        } catch (err) {
            console.error("Login error:", err)
            error.value = err.message
            return false
        } finally {
            loading.value = false
        }
    }

    async function fetchUserProfile(accessToken) {
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
            // Endpoint is currently under the auth router prefix
            const response = await fetch(`${baseUrl}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            })
            
            if (response.ok) {
                const userData = await response.json()
                user.value = userData
                localStorage.setItem('user', JSON.stringify(userData))
            }
        } catch (err) {
            console.error("Failed to fetch user profile", err)
        }
    }

    function logout() {
        user.value = null
        token.value = null
        localStorage.removeItem('user')
        localStorage.removeItem('token')
        // router.push('/login') // Can be handled by component
    }

    return {
        user,
        token,
        loading,
        error,
        isAuthenticated,
        isAdmin,
        login,
        logout
    }
})
