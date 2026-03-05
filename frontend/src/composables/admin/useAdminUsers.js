import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAdminUsers() {
    const authStore = useAuthStore()
    
    const users = ref([])
    const loading = ref(false)
    const error = ref('')
    
    // Pagination & Filtering
    const searchQuery = ref('')
    const roleFilter = ref('ALL') // ALL, ADMIN, USER
    const showRoleDropdown = ref(false)
    
    const currentPage = ref(1)
    const pageSize = ref(10)
    
    const fetchUsers = async () => {
        loading.value = true
        error.value = ''
        try {
            const data = await authStore.fetchWithAuth('/api/v1/users')
            users.value = data || []
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
                (u.full_name && u.full_name.toLowerCase().includes(q)) ||
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
            await authStore.fetchWithAuth(`/api/v1/users/${userId}`, {
                method: 'DELETE'
            })
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
            const data = await authStore.fetchWithAuth(`/api/v1/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            })
            
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
        updateUser
    }
}
