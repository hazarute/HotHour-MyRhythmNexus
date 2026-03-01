<template>
    <div ref="notificationsDropdownRef" class="relative flex items-center justify-end">
        <button @click="toggleNotificationsDropdown" class="relative flex items-center justify-center p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-[#232d3f] transition-colors">
            <span class="material-symbols-outlined">notifications</span>
            <span
                v-if="unreadNotificationsCount > 0"
                class="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center"
            >
                {{ unreadNotificationsCount > 99 ? '99+' : unreadNotificationsCount }}
            </span>
        </button>

        <teleport to="body">
            <div v-if="showNotificationsDropdown" ref="portalRef" :style="portalStyle" class="bg-white dark:bg-[#1a2230] rounded-xl border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden">
                <div class="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                    <p class="text-sm font-semibold text-slate-900 dark:text-white">İptal Bildirimleri</p>
                    <div class="flex items-center gap-3">
                        <button
                            @click="clearReadNotifications"
                            class="text-xs text-slate-500 hover:text-red-500 hover:underline"
                            :disabled="clearingReadNotifications"
                        >
                            {{ clearingReadNotifications ? 'Temizleniyor...' : 'Okunanları Temizle' }}
                        </button>
                        <button @click="fetchAdminNotifications()" class="text-xs text-primary hover:underline">Yenile</button>
                    </div>
                </div>

                <div v-if="notificationsLoading" class="p-4 text-xs text-slate-500 dark:text-slate-400">
                    Bildirimler yükleniyor...
                </div>

                <div v-else-if="adminNotifications.length === 0" class="p-4 text-xs text-slate-500 dark:text-slate-400">
                    Şu an otomatik iptal bildirimi bulunmuyor.
                </div>

                <div v-else class="max-h-96 overflow-y-auto">
                    <div
                        v-for="notification in adminNotifications"
                        :key="notification.id"
                        class="w-full text-left px-4 py-3 border-b border-slate-200 dark:border-slate-800 last:border-b-0 hover:bg-slate-50 dark:hover:bg-[#232d3f] transition-colors"
                        :class="notification.is_read ? 'opacity-80' : 'bg-red-50/40 dark:bg-red-900/10'"
                    >
                        <div class="flex items-start justify-between gap-3">
                            <button @click="openNotification(notification)" class="flex-1 text-left">
                                <p class="text-xs font-bold text-slate-900 dark:text-white">{{ notification.title }}</p>
                                <p class="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">{{ notification.message }}</p>
                            </button>
                            <div class="flex items-center gap-2 ml-2">
                                <span v-if="!notification.is_read" class="mt-1 w-2 h-2 rounded-full bg-red-500"></span>
                                <button
                                    @click="deleteNotification(notification.id)"
                                    class="text-slate-400 hover:text-red-500 transition-colors"
                                    title="Bildirimi Sil"
                                    :disabled="deletingNotificationId === notification.id"
                                >
                                    <span class="material-symbols-outlined" style="font-size: 16px;">
                                        {{ deletingNotificationId === notification.id ? 'progress_activity' : 'delete' }}
                                    </span>
                                </button>
                            </div>
                        </div>
                        <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-2">{{ formatShortDate(notification.created_at) }}</p>
                    </div>
                </div>
            </div>
        </teleport>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminNotifications } from '@/composables/admin/useAdminNotifications'
import { formatShortDate } from '@/utils/admin/formatters'

const router = useRouter()
const notificationsDropdownRef = ref(null)
const portalRef = ref(null)
const portalStyle = ref({ position: 'absolute', top: '0px', left: '0px', width: '360px', zIndex: 120 })

const {
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
} = useAdminNotifications()

const handleDocumentClick = (event) => {
    if (!showNotificationsDropdown.value) return
    const clickedInsideToggle = notificationsDropdownRef.value && notificationsDropdownRef.value.contains(event.target)
    const clickedInsidePortal = portalRef.value && portalRef.value.contains(event.target)
    if (!clickedInsideToggle && !clickedInsidePortal) {
        showNotificationsDropdown.value = false
    }
}

const openNotification = async (notification) => {
    await markNotificationAsRead(notification)
    if (notification?.reservation_id) {
        router.push({ name: 'admin-reservation-detail', params: { id: notification.reservation_id } })
        showNotificationsDropdown.value = false
    }
}

onMounted(() => {
    // `useAdminNotifications()` now performs the initial fetch on mount; just attach listeners here
    document.addEventListener('click', handleDocumentClick, true)
    // Reposition portal when dropdown opens
    const computePortalPosition = () => {
        if (!notificationsDropdownRef.value) return
        const rect = notificationsDropdownRef.value.getBoundingClientRect()
        const width = Math.min(360, window.innerWidth - 32)
        let left = rect.right - width
        if (left < 8) left = 8
        const top = rect.bottom + window.scrollY + 8
        portalStyle.value = { position: 'absolute', top: `${top}px`, left: `${left + window.scrollX}px`, width: `${width}px`, zIndex: 120 }
    }

    watch(showNotificationsDropdown, async (val) => {
        if (val) {
            await nextTick()
            computePortalPosition()
            window.addEventListener('resize', computePortalPosition)
            window.addEventListener('scroll', computePortalPosition, true)
        } else {
            window.removeEventListener('resize', computePortalPosition)
            window.removeEventListener('scroll', computePortalPosition, true)
        }
    })
})

onUnmounted(() => {
    document.removeEventListener('click', handleDocumentClick, true)
})
</script>
