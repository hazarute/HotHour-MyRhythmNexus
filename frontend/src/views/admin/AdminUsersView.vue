<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useAdminUsers } from '@/composables/admin/useAdminUsers'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/admin/formatters'
import AdminNotificationDropdown from '@/components/admin/AdminNotificationDropdown.vue'

const {
    users,
    loading,
    error,
    searchQuery,
    roleFilter,
    showRoleDropdown,
    currentPage,
    paginatedUsers,
    totalPages,
    fetchUsers,
    goNextPage,
    goPrevPage,
    updateUser,
    resendVerificationEmail,
    resetPassword,
    cleanupSocketListeners
} = useAdminUsers()

const authStore = useAuthStore()

const infoMessage = ref('')
const infoType = ref('success')
const pendingResetUserId = ref(null)

const showInfo = (message, type = 'success') => {
    infoMessage.value = message
    infoType.value = type
}

const clearInfo = () => {
    infoMessage.value = ''
}

const isCurrentAdmin = (user) => authStore.user?.id === user.id

const isReadOnlyAdminRow = (user) => user.role === 'ADMIN' && !isCurrentAdmin(user)

const canEditUser = (user) => !isReadOnlyAdminRow(user)

const canResetPassword = (user) => !isReadOnlyAdminRow(user)

const canResendVerification = (user) => !(user.is_verified || user.isVerified) && !isReadOnlyAdminRow(user)

const handleResendVerification = async (user) => {
    const result = await resendVerificationEmail(user.id)
    if (result?.success) {
        showInfo(result.message, 'success')
    } else {
        showInfo(result?.message || 'Doğrulama e-postası gönderilemedi.', 'error')
    }
}

const startResetPassword = (user) => {
    if (!canResetPassword(user)) {
        showInfo('Diğer admin kullanıcılar salt okunurdur.', 'error')
        return
    }
    pendingResetUserId.value = user.id
}

const cancelResetPassword = () => {
    pendingResetUserId.value = null
}

const confirmResetPassword = async (user) => {
    const result = await resetPassword(user.id)
    if (result?.success) {
        showInfo(result.message, 'success')
    } else {
        showInfo(result?.message || 'Şifre sıfırlanamadı.', 'error')
    }
    pendingResetUserId.value = null
}

onMounted(() => {
    fetchUsers()
})

onUnmounted(() => {
    cleanupSocketListeners()
})

const editingUser = ref(null)

const startEdit = (user) => {
    if (!canEditUser(user)) {
        showInfo('Diğer admin kullanıcıların bilgileri düzenlenemez.', 'error')
        return
    }
    editingUser.value = { ...user, fullName: user.fullName || user.full_name } // clone and normalize name
}

const cancelEdit = () => {
    editingUser.value = null
}

const saveEdit = async () => {
    if (!editingUser.value) return
    const success = await updateUser(editingUser.value.id, {
        full_name: editingUser.value.fullName || editingUser.value.full_name,
        phone: editingUser.value.phone,
        gender: editingUser.value.gender
    })
    if (success) {
        editingUser.value = null
    }
}
</script>

<template>
  <div>
    <!-- Header -->
    <header class="sticky top-0 z-40 bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3 md:px-8 md:py-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">Kullanıcılar</h2>
            <p class="text-slate-500 dark:text-slate-400 text-xs md:text-sm mt-1">Platformdaki tüm kullanıcıları yönet</p>
        </div>
        <div class="flex items-center gap-2 md:gap-4 w-full md:w-auto justify-end">
            <AdminNotificationDropdown />
        </div>
    </header>

    <div class="p-4 md:p-8 flex flex-col gap-6">
        <!-- Error State -->
        <div v-if="error" class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-xl border border-red-200 dark:border-red-800 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined">error</span>
                <span>{{ error }}</span>
            </div>
            <button @click="fetchUsers" class="text-sm font-semibold hover:underline">Tekrar Dene</button>
        </div>

        <!-- Info Message -->
        <div v-if="infoMessage" :class="['p-4 rounded-xl border flex items-start justify-between gap-4', infoType === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-200' : 'bg-rose-50 border-rose-200 text-rose-700 dark:bg-rose-900/20 dark:text-rose-200']">
            <div class="flex items-start gap-2">
                <span class="material-symbols-outlined text-2xl" :class="infoType === 'success' ? 'text-emerald-500' : 'text-rose-500'">
                    {{ infoType === 'success' ? 'check_circle' : 'error' }}
                </span>
                <div class="text-sm leading-relaxed">{{ infoMessage }}</div>
            </div>
            <button @click="clearInfo" class="text-sm font-semibold hover:underline">Kapat</button>
        </div>

        <!-- Table Section -->
        <div class="flex flex-col rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#1a2230] shadow-sm overflow-hidden">
            <!-- Table Header / Filters -->
            <div class="flex flex-wrap items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800 gap-4">
                <div class="relative max-w-sm w-full">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500 dark:text-slate-400">
                        <span class="material-symbols-outlined" style="font-size: 20px;">search</span>
                    </span>
                    <input v-model="searchQuery" class="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-50 dark:bg-background-dark border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder-slate-400 dark:placeholder-slate-600 text-sm" placeholder="İsim, e-posta, tel ara..." type="text">
                </div>
                
                <div class="flex items-center gap-2 relative">
                    <button @click="showRoleDropdown = !showRoleDropdown" class="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors">
                        <span class="material-symbols-outlined" style="font-size: 18px;">filter_list</span>
                        {{ 
                            {
                                'ALL': 'Tüm Roller',
                                'ADMIN': 'Yönetici',
                                'USER': 'Kullanıcı'
                            }[roleFilter] 
                        }}
                        <span class="material-symbols-outlined transition-transform duration-200" :class="showRoleDropdown ? 'rotate-180' : ''" style="font-size: 18px;">expand_more</span>
                    </button>
                    <!-- Dropdown -->
                    <div v-if="showRoleDropdown" class="absolute right-0 top-full mt-2 w-40 bg-white dark:bg-[#1a2230] border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg overflow-hidden z-50">
                        <button v-for="(label, key) in {'ALL':'Tüm Roller','ADMIN':'Yönetici','USER':'Kullanıcı'}" :key="key" @click="roleFilter = key; showRoleDropdown = false" class="w-full text-left px-4 py-2 text-sm hover:bg-slate-50 dark:hover:bg-background-dark text-slate-700 dark:text-slate-300">
                            {{ label }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading && users.length === 0" class="p-12 flex flex-col items-center justify-center text-slate-500 dark:text-slate-400">
                <span class="material-symbols-outlined animate-spin text-4xl mb-4 text-primary">sync</span>
                <p>Kullanıcılar yükleniyor...</p>
            </div>

            <!-- Results List (Mobile cards vs Desktop table) -->
            <div v-else class="overflow-x-auto">
                <table class="w-full text-left border-collapse min-w-[800px]">
                    <thead>
                        <tr class="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#232d3f]/50">
                            <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Kullanıcı Bilgisi</th>
                            <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">İletişim</th>
                            <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Rol</th>
                            <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Kayıt Tarihi</th>
                            <th class="px-6 py-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right">İşlemler</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 dark:divide-slate-800 text-sm">
                        <tr v-for="user in paginatedUsers" :key="user.id" class="hover:bg-slate-50/50 dark:hover:bg-[#232d3f]/30 transition-colors group">
                            
                            <!-- Editing Row -->
                            <template v-if="editingUser && editingUser.id === user.id">
                                <td class="px-6 py-4 bg-slate-50 dark:bg-[#161e2b]">
                                    <input v-model="editingUser.fullName" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-background-dark dark:text-white" placeholder="Ad Soyad" />
                                    <select v-model="editingUser.gender" class="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-background-dark dark:text-white">
                                        <option value="FEMALE">Kadın</option>
                                        <option value="MALE">Erkek</option>
                                    </select>
                                </td>
                                <td class="px-6 py-4 bg-slate-50 dark:bg-[#161e2b]">
                                    <div class="flex flex-col gap-2">
                                        <input :value="editingUser.email" type="email" disabled class="w-full cursor-not-allowed rounded-xl border border-slate-200 bg-slate-100 px-3 py-2.5 text-sm text-slate-500 opacity-90 dark:border-slate-700 dark:bg-slate-800/80 dark:text-slate-400" placeholder="E-posta" />
                                        <p class="text-xs text-slate-500 dark:text-slate-400">E-posta adresi güvenlik nedeniyle salt okunur tutulur.</p>
                                        <button
                                            v-if="canResendVerification(editingUser)"
                                            @click="handleResendVerification(editingUser)"
                                            type="button"
                                            class="mt-1 inline-flex items-center gap-2 rounded-lg border border-amber-300/70 bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700 transition-all hover:-translate-y-0.5 hover:bg-amber-100 dark:border-amber-500/40 dark:bg-amber-500/10 dark:text-amber-300 dark:hover:bg-amber-500/20"
                                        >
                                            <span class="material-symbols-outlined text-[14px]">outgoing_mail</span>
                                            Onay bağlantısını gönder
                                        </button>
                                        <input v-model="editingUser.phone" type="tel" class="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-background-dark dark:text-white" placeholder="Telefon" />
                                    </div>
                                </td>
                                <td class="px-6 py-4 bg-slate-50 dark:bg-[#161e2b]">
                                    <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                                        <span v-if="editingUser.role === 'ADMIN'" class="material-symbols-outlined text-[14px]">shield_person</span>
                                        <span v-else class="material-symbols-outlined text-[14px]">person</span>
                                        {{ editingUser.role === 'ADMIN' ? 'Yönetici' : 'Kullanıcı' }}
                                    </div>
                                    <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">Bu alandan rol değiştirilemez.</p>
                                </td>
                                <td class="px-6 py-4 text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-[#161e2b]">
                                    {{ formatDate(user.created_at || user.createdAt) }}
                                </td>
                                <td class="px-6 py-4 bg-slate-50 dark:bg-[#161e2b]">
                                    <div class="flex flex-col items-end gap-2">
                                        <button @click="saveEdit" class="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 transition-all hover:-translate-y-0.5 hover:bg-emerald-600" title="Kaydet">
                                            <span class="material-symbols-outlined" style="font-size: 18px;">check</span>
                                            Kaydet
                                        </button>
                                        <button @click="cancelEdit" class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 transition-all hover:-translate-y-0.5 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700" title="İptal">
                                            <span class="material-symbols-outlined" style="font-size: 18px;">close</span>
                                            Vazgeç
                                        </button>
                                    </div>
                                </td>
                            </template>

                            <!-- Normal Row -->
                            <template v-else>
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-3">
                                        <div class="size-10 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 font-bold text-slate-600 dark:text-slate-400">
                                            {{ (user.fullName || user.full_name) ? (user.fullName || user.full_name)[0].toUpperCase() : '?' }}
                                        </div>
                                        <div>
                                            <p class="font-medium text-slate-900 dark:text-white">{{ user.fullName || user.full_name }}</p>
                                            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ user.gender === 'FEMALE' ? 'Kadın' : 'Erkek' }}</p>
                                            <p v-if="isReadOnlyAdminRow(user)" class="mt-1 text-[11px] font-semibold text-amber-600 dark:text-amber-300">Salt okunur admin hesabı</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="flex flex-col gap-1">
                                        <div class="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                                            <span class="material-symbols-outlined text-[16px] text-slate-400">mail</span>
                                            <span>{{ user.email }}</span>
                                            <span v-if="user.is_verified || user.isVerified" class="material-symbols-outlined text-[14px] text-green-500" title="Doğrulanmış">verified</span>
                                            <button
                                                v-else-if="canResendVerification(user)"
                                                @click="handleResendVerification(user)"
                                                type="button"
                                                class="inline-flex items-center gap-1.5 rounded-lg border border-amber-300/70 bg-amber-50 px-2.5 py-1.5 text-[11px] font-semibold text-amber-700 transition-all hover:-translate-y-0.5 hover:bg-amber-100 dark:border-amber-500/40 dark:bg-amber-500/10 dark:text-amber-300 dark:hover:bg-amber-500/20"
                                                title="Doğrulama e-postasını tekrar gönder"
                                            >
                                                <span class="material-symbols-outlined text-[14px]">outgoing_mail</span>
                                                Onay bağlantısını gönder
                                            </button>
                                        </div>
                                        <div class="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
                                            <span class="material-symbols-outlined text-[16px]">call</span>
                                            {{ user.phone }}
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
                                          :class="user.role === 'ADMIN' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'">
                                          <span v-if="user.role === 'ADMIN'" class="material-symbols-outlined text-[14px]">shield_person</span>
                                          <span v-else class="material-symbols-outlined text-[14px]">person</span>
                                          {{ user.role === 'ADMIN' ? 'Yönetici' : 'Kullanıcı' }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-slate-500 dark:text-slate-400">
                                    {{ formatDate(user.created_at || user.createdAt) }}
                                </td>
                                <td class="px-6 py-4">
                                    <div class="relative flex items-center justify-end gap-2 transition-opacity" :class="canEditUser(user) ? 'opacity-0 group-hover:opacity-100' : 'opacity-100'">
                                        <template v-if="canEditUser(user)">
                                            <button @click="startEdit(user); clearInfo()" class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition-all hover:-translate-y-0.5 hover:border-primary hover:text-primary dark:border-slate-700 dark:bg-background-dark dark:text-slate-300 dark:hover:border-neon-blue dark:hover:text-neon-blue" title="Düzenle">
                                                <span class="material-symbols-outlined" style="font-size: 18px;">edit</span>
                                                Düzenle
                                            </button>
                                            <div class="relative flex items-center gap-2">
                                                <template v-if="pendingResetUserId === user.id">
                                                    <div class="mt-2 w-full max-w-xs rounded-2xl border border-amber-300/70 bg-white p-4 text-left shadow-lg shadow-black/5 dark:border-amber-500/30 dark:bg-[#182132]">
                                                        <div class="flex items-start gap-3">
                                                            <div class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300">
                                                                <span class="material-symbols-outlined text-[20px]">lock_reset</span>
                                                            </div>
                                                            <div class="min-w-0 flex-1">
                                                                <p class="text-sm font-semibold text-slate-900 dark:text-white">Şifre sıfırlama onayı</p>
                                                                <p class="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">Bu kullanıcının şifresi <span class="font-semibold">sifredegistir</span> olarak güncellenecek.</p>
                                                            </div>
                                                        </div>
                                                        <div class="mt-4 flex items-center justify-end gap-2 border-t border-slate-200 pt-3 dark:border-slate-700">
                                                            <button @click="cancelResetPassword" class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition-all hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700">İptal</button>
                                                            <button @click="confirmResetPassword(user)" class="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-3.5 py-2 text-sm font-semibold text-white shadow-lg shadow-amber-500/20 transition-all hover:bg-amber-600">
                                                                <span class="material-symbols-outlined text-[18px]">check</span>
                                                                Şifreyi sıfırla
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <button @click="cancelResetPassword" class="inline-flex items-center gap-2 rounded-xl border border-amber-300 bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-700 transition-all hover:bg-amber-100 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-200 dark:hover:bg-amber-500/20">
                                                        <span class="material-symbols-outlined text-[18px]">close</span>
                                                        Vazgeç
                                                    </button>
                                                </template>
                                                <template v-else>
                                                    <button @click="startResetPassword(user); clearInfo()" class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition-all hover:-translate-y-0.5 hover:border-amber-400 hover:text-amber-600 dark:border-slate-700 dark:bg-background-dark dark:text-slate-300 dark:hover:border-amber-400 dark:hover:text-amber-300" title="Şifreyi sifredegistir olarak sıfırla">
                                                        <span class="material-symbols-outlined" style="font-size: 18px;">lock_reset</span>
                                                        Şifre Sıfırla
                                                    </button>
                                                </template>
                                            </div>
                                        </template>
                                        <span v-else class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-300">
                                            Salt okunur
                                        </span>
                                    </div>
                                </td>
                            </template>
                        </tr>
                        
                        <tr v-if="!loading && paginatedUsers.length === 0">
                            <td colspan="5" class="px-6 py-12 text-center text-slate-500 dark:text-slate-400">
                                <span class="material-symbols-outlined text-4xl mb-3 opacity-50">group_off</span>
                                <p>Kullanıcı bulunamadı.</p>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="flex items-center justify-between p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-background-dark/50">
                <p class="text-sm text-slate-500 dark:text-slate-400">
                    Toplam <span class="font-medium text-slate-900 dark:text-white">{{ users.length }}</span> kullanıcı
                </p>
                <div class="flex items-center gap-2">
                    <button @click="goPrevPage" :disabled="currentPage === 1" class="flex items-center justify-center size-8 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1a2230] disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                        <span class="material-symbols-outlined" style="font-size: 20px;">chevron_left</span>
                    </button>
                    <span class="text-sm font-medium text-slate-700 dark:text-slate-300 px-2 text-center min-w-[3rem]">
                        {{ currentPage }} / {{ totalPages }}
                    </span>
                    <button @click="goNextPage" :disabled="currentPage >= totalPages" class="flex items-center justify-center size-8 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1a2230] disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                        <span class="material-symbols-outlined" style="font-size: 20px;">chevron_right</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>
