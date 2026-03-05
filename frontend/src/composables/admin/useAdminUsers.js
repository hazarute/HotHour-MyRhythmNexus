import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSocketStore } from '@/stores/socket'

export function useAdminUsers() {
    const authStore = useAuthStore()
    const socketStore = useSocketStore()
    
    const users = ref([])
    const loading = ref(false)
    const error = ref('')
    
    // Pagination & Filtering
    const searchQuery = ref('')
    const roleFilter = ref('ALL') // ALL, ADMIN, USER
    const showRoleDropdown = ref(false)
    
    const currentPage = ref(1)
    const pageSize = ref(20)  // Max 20 users visible per page
    
    // Socket event handlers
    const onUserCreated = (payload) => {
        console.log('[AdminUsers] user_created event received:', payload)
        if (payload && payload.user) {
            // Add new user to the top of the list
            const newUser = payload.user
            // Avoid duplicates
            if (!users.value.find(u => u.id === newUser.id)) {
                users.value.unshift(newUser)
            }
        }
    }
    
    const setupSocketListeners = () => {
        if (!socketStore.isConnected) {
            socketStore.connect()
        }
        
        console.log('[AdminUsers] Setting up socket listeners')
        socketStore.on('user_created', onUserCreated)
    }
    
    const cleanupSocketListeners = () => {
        console.log('[AdminUsers] Cleaning up socket listeners')
        socketStore.off('user_created', onUserCreated)
    }
    
    const fetchUsers = async () => {
        loading.value = true
        error.value = ''
        try {
            const response = await authStore.fetchWithAuth('/api/v1/users')
            if (!response.ok) throw new Error('Kullanıcılar getirilemedi')

            
            const data = await response.json()
            users.value = data || []
            
            // Setup socket listeners after first fetch
            setupSocketListeners()
        } catch (err) {
            console.error('Kullanıcılar yüklenirken hata:', err)
            error.value = 'Kullanıcı listesi alınamadı.'
        } finally {
            loading.value = false
        }
    }
    
    const filteredUsers = computed(() => {
        let result = users.value
        
        // Filter by role
        if (roleFilter.value !== 'ALL') {
            result = result.filter(u => u.role === roleFilter.value)
        }
        
        // Search
        if (searchQuery.value) {
            const q = searchQuery.value.toLowerCase()
            result = result.filter(u => 
                ((u.fullName || u.full_name) && (u.fullName || u.full_name).toLowerCase().includes(q)) ||
                (u.email && u.email.toLowerCase().includes(q)) ||
                (u.phone && u.phone.includes(q))
            )
        }
        
        // Sort newest first
        return result.sort((a, b) => new Date(b.created_at || b.createdAt) - new Date(a.created_at || a.createdAt))
    })
    
    const totalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / pageSize.value)))
    
    const paginatedUsers = computed(() => {
        const start = (currentPage.value - 1) * pageSize.value
        return filteredUsers.value.slice(start, start + pageSize.value)
    })
    
    const goNextPage = () => {
        if (currentPage.value < totalPages.value) currentPage.value++
    }
    const goPrevPage = () => {
        if (currentPage.value > 1) currentPage.value--
    }
    
    const deleteUser = async (userId) => {
        if (!confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) return false
        
        try {
            const resp = await authStore.fetchWithAuth(`/api/v1/users/${userId}`, {
                method: 'DELETE'
            })
            if (!resp.ok) {
                const data = await resp.json()
                throw new Error(data.detail || 'Kullanıcı silinemedi')
            }

            users.value = users.value.filter(u => u.id !== userId)
            
            // Adjust pagination if needed
            if (paginatedUsers.value.length === 0 && currentPage.value > 1) {
                currentPage.value--
            }
            return true
        } catch (err) {
            console.error('Kullanıcı silinemedi:', err)
            alert(err.message || 'Kullanıcı silinirken bir hata oluştu.')
            return false
        }
    }
    
    const updateUser = async (userId, updateData) => {
        try {
            const response = await authStore.fetchWithAuth(`/api/v1/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            })
            
            if (!response.ok) {
                const errData = await response.json()
                throw new Error(errData.detail || 'Kullanıcı güncellenemedi')
            }
            
            const data = await response.json()
            
            // Update in local state
            const index = users.value.findIndex(u => u.id === userId)
            if (index !== -1) {
                users.value[index] = { ...users.value[index], ...data }
            }
            return true
        } catch (err) {
            console.error('Kullanıcı güncellenemedi:', err)
            alert(err.message || 'Kullanıcı güncellenirken bir hata oluştu.')
            return false
        }
    }

    return {
        users,
        loading,
        error,
        searchQuery,
        roleFilter,
        showRoleDropdown,
        currentPage,
        pageSize,
        totalPages,
        filteredUsers,
        paginatedUsers,
        fetchUsers,
        goNextPage,
        goPrevPage,
        deleteUser,
        updateUser,
        setupSocketListeners,
        cleanupSocketListeners
    }
}
