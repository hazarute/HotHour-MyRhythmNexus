import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
    const router = useRouter()
    
    // State
    const user = ref(JSON.parse(localStorage.getItem('user')) || null)
    const token = ref(localStorage.getItem('token') || null)
    const refreshToken = ref(localStorage.getItem('refresh_token') || null)
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
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            
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
            refreshToken.value = data.refresh_token || null
            // Ideally decode token or fetch /me to get user details
            // For now, we'll fetch the user profile immediately
            await fetchUserProfile(data.access_token)

            // Persist
            localStorage.setItem('token', token.value)
            if (refreshToken.value) localStorage.setItem('refresh_token', refreshToken.value)
            
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
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            // Endpoint is currently under the auth router prefix
            const response = await fetch(`${baseUrl}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${accessToken || token.value}`
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

    async function changePassword(currentPassword, newPassword) {
        loading.value = true
        error.value = null
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            const response = await fetchWithAuth('/api/v1/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
            })

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}))
                throw new Error(errData.detail || 'Password update failed')
            }
            
            return true
        } catch (err) {
            console.error("Password change error:", err)
            error.value = err.message
            return false
        } finally {
            loading.value = false
        }
    }

    function logout() {
        // Try to revoke refresh token on server (best-effort)
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            if (refreshToken.value) {
                fetch(`${baseUrl}/api/v1/auth/revoke`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken.value })
                }).catch(() => {})
            }
        } catch (_e) {
            // ignore
        }

        user.value = null
        token.value = null
        refreshToken.value = null
        localStorage.removeItem('user')
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        router.push('/login')
    }

    async function refreshTokens() {
        if (!refreshToken.value) return false
        try {
            const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
            const resp = await fetch(`${baseUrl}/api/v1/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken.value })
            })
            if (!resp.ok) return false
            const data = await resp.json()
            token.value = data.access_token
            refreshToken.value = data.refresh_token || refreshToken.value
            localStorage.setItem('token', token.value)
            if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
            await fetchUserProfile(token.value)
            return true
        } catch (err) {
            console.error('Refresh token failed', err)
            return false
        }
    }

    async function fetchWithAuth(path, options = {}) {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
        const url = `${baseUrl}${path}`
        options.headers = options.headers || {}
        if (token.value) {
            options.headers['Authorization'] = `Bearer ${token.value}`
        }

        let resp = await fetch(url, options)
        if (resp.status !== 401) return resp

        // Try to refresh once
        const ok = await refreshTokens()
        if (!ok) {
            // Logout and optionally redirect
            logout()
            router.push('/login')
            return resp
        }

        // Retry original request with new token
        options.headers['Authorization'] = `Bearer ${token.value}`
        resp = await fetch(url, options)
        return resp
    }

    return {
        user,
        token,
        refreshToken,
        loading,
        error,
        isAuthenticated,
        isAdmin,
        login,
        logout,
        fetchUserProfile,
        changePassword,
        fetchWithAuth,
        refreshTokens
    }
})
