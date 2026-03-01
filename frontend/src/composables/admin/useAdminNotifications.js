import { ref, onMounted, onUnmounted } from 'vue'
import { adminFetch } from '@/utils/admin/api_client'
import { useAuthStore } from '@/stores/auth'
import SocketService from '@/services/socket'

export function useAdminNotifications() {
    const authStore = useAuthStore()
    
    const adminNotifications = ref([])
    const unreadNotificationsCount = ref(0)
    const notificationsLoading = ref(false)
    const deletingNotificationId = ref(null)
    const clearingReadNotifications = ref(false)
    
    const showNotificationsDropdown = ref(false)

    const fetchAdminNotifications = async (silent = false) => {
        if (!silent) notificationsLoading.value = true
        
        try {
            const data = await adminFetch('/api/v1/reservations/admin/notifications/cancellations?limit=20', {}, authStore)
            const raw = Array.isArray(data.notifications) ? data.notifications : []
            // Ensure newest first and cap to 20
            adminNotifications.value = raw
                .slice()
                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                .slice(0, 20)
            unreadNotificationsCount.value = Number(data.unread_count || 0)
        } catch (err) {
            console.error('Admin bildirimleri alınamadı:', err)
        } finally {
            notificationsLoading.value = false
        }
    }

    // Realtime: refresh notifications on relevant socket events
    onMounted(() => {
        if (!SocketService.isConnected) SocketService.connect()

        const handleNotificationCreated = async (payload) => {
            await fetchAdminNotifications(true)
        }

        const handleNotificationDeleted = async (payload) => {
            await fetchAdminNotifications(true)
        }

        SocketService.on('notification_created', handleNotificationCreated)
        SocketService.on('notification_deleted', handleNotificationDeleted)

        // Initial fetch
        ;(async () => {
            try {
                await fetchAdminNotifications()
            } catch (err) {
                // ignore
            }
        })()
    })

    onUnmounted(() => {
        SocketService.off('notification_created')
        SocketService.off('notification_deleted')
    })

    const toggleNotificationsDropdown = async () => {
        showNotificationsDropdown.value = !showNotificationsDropdown.value
        if (showNotificationsDropdown.value) {
            await fetchAdminNotifications()
        }
    }

    const markNotificationAsRead = async (notification) => {
        if (!notification || notification.is_read) return

        try {
            await adminFetch(`/api/v1/reservations/admin/notifications/${notification.id}/read`, { method: 'POST' }, authStore)
            notification.is_read = true
            unreadNotificationsCount.value = Math.max(0, unreadNotificationsCount.value - 1)
        } catch (err) {
            console.error('Bildirim okundu güncelleme hatası:', err)
        }
    }

    const deleteNotification = async (notificationId) => {
        if (!notificationId) return

        try {
            deletingNotificationId.value = notificationId
            await adminFetch(`/api/v1/reservations/admin/notifications/${notificationId}`, { method: 'DELETE' }, authStore)
            await fetchAdminNotifications(true)
        } catch (err) {
            console.error('Bildirim silme hatası:', err)
        } finally {
            deletingNotificationId.value = null
        }
    }

    const clearReadNotifications = async () => {
        try {
            clearingReadNotifications.value = true
            await adminFetch('/api/v1/reservations/admin/notifications/read/all', { method: 'DELETE' }, authStore)
            await fetchAdminNotifications(true)
        } catch (err) {
            console.error('Okunan bildirim temizleme hatası:', err)
        } finally {
            clearingReadNotifications.value = false
        }
    }

    return {
        adminNotifications,
        unreadNotificationsCount,
        notificationsLoading,
        deletingNotificationId,
        clearingReadNotifications,
        showNotificationsDropdown,
        
        fetchAdminNotifications,
        toggleNotificationsDropdown,
        markNotificationAsRead,
        deleteNotification,
        clearReadNotifications
    }
}
