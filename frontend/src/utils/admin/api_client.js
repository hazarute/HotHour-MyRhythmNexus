export const adminFetch = async (endpoint, options = {}, authStore) => {
    if (!authStore || !authStore.token) {
        throw new Error('Yetkilendirme hatası: Oturum bulunamadı.')
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''
    // endpoint starts with /
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`

    const defaultHeaders = {
        'Authorization': `Bearer ${authStore.token}`
    }

    // JSON içeriği gönderiliyorsa Content-Type ekle
    if (options.body && typeof options.body === 'string') {
        defaultHeaders['Content-Type'] = 'application/json'
    }

    const fetchOptions = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    }

    // If an authStore with fetchWithAuth is provided, prefer it (supports auto-refresh)
    let response
    if (authStore && typeof authStore.fetchWithAuth === 'function') {
        response = await authStore.fetchWithAuth(url.replace(baseUrl, ''), fetchOptions)
    } else {
        response = await fetch(url, fetchOptions)
    }

    if (!response.ok) {
        let errorMsg = 'Sunucu isteği başarısız oldu'
        try {
            const data = await response.json()
            errorMsg = data.detail || errorMsg
        } catch (e) {
            // response body JSON değilse
        }
        throw new Error(errorMsg)
    }

    // 204 No Content
    if (response.status === 204) {
        return null
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
        return await response.json()
    }

    return await response.text()
}