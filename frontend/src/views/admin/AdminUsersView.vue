<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useAdminUsers } from '@/composables/admin/useAdminUsers'
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
    deleteUser,
    updateUser,
    cleanupSocketListeners
} = useAdminUsers()

onMounted(() => {
    fetchUsers()
})

onUnmounted(() => {
    cleanupSocketListeners()
})

const editingUser = ref(null)

const startEdit = (user) => {
    editingUser.value = { ...user, fullName: user.fullName || user.full_name } // clone and normalize name
}

const cancelEdit = () => {
    editingUser.value = null
}

const saveEdit = async () => {
    if (!editingUser.value) return
    const success = await updateUser(editingUser.value.id, {
        full_name: editingUser.value.fullName || editingUser.value.full_name,
        email: editingUser.value.email,
        phone: editingUser.value.phone,
        role: editingUser.value.role,
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
                                <td class="px-6 py-4">
                                    <input v-model="editingUser.fullName" class="w-full px-2 py-1 bg-slate-100 dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white mb-2" placeholder="Ad Soyad" />
                                    <select v-model="editingUser.gender" class="w-full px-2 py-1 bg-slate-100 dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white">
                                        <option value="FEMALE">Kadın</option>
                                        <option value="MALE">Erkek</option>
                                    </select>
                                </td>
                                <td class="px-6 py-4">
                                    <input v-model="editingUser.email" type="email" class="w-full px-2 py-1 bg-slate-100 dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white mb-2" placeholder="E-posta" />
                                    <input v-model="editingUser.phone" type="tel" class="w-full px-2 py-1 bg-slate-100 dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white" placeholder="Telefon" />
                                </td>
                                <td class="px-6 py-4">
                                    <select v-model="editingUser.role" class="w-full px-2 py-1 bg-slate-100 dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white">
                                        <option value="USER">Kullanıcı</option>
                                        <option value="ADMIN">Yönetici</option>
                                    </select>
                                </td>
                                <td class="px-6 py-4 text-slate-500">
                                    {{ formatDate(user.created_at || user.createdAt) }}
                                </td>
                                <td class="px-6 py-4 text-right">
                                    <div class="flex items-center justify-end gap-2">
                                        <button @click="saveEdit" class="p-1.5 bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50 rounded-lg transition-colors" title="Kaydet">
                                            <span class="material-symbols-outlined" style="font-size: 20px;">check</span>
                                        </button>
                                        <button @click="cancelEdit" class="p-1.5 bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors" title="İptal">
                                            <span class="material-symbols-outlined" style="font-size: 20px;">close</span>
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
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="flex flex-col gap-1">
                                        <div class="flex items-center gap-1.5 text-slate-700 dark:text-slate-300">
                                            <span class="material-symbols-outlined text-[16px] text-slate-400">mail</span>
                                            {{ user.email }}
                                            <span v-if="user.is_verified || user.isVerified" class="material-symbols-outlined text-[14px] text-green-500" title="Doğrulanmış">verified</span>
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
                                    <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button @click="startEdit(user)" class="p-2 text-slate-400 hover:text-primary dark:hover:text-neon-blue bg-white dark:bg-background-dark border border-slate-200 dark:border-slate-700 rounded-lg hover:border-primary dark:hover:border-neon-blue transition-all" title="Düzenle">
                                            <span class="material-symbols-outlined" style="font-size: 18px;">edit</span>
                                        </button>
                                        <button @click="deleteUser(user.id)" class="p-2 text-slate-400 hover:text-red-500 bg-white dark:bg-background-dark border border-slate-200 dark:border-slate-700 rounded-lg hover:border-red-500 transition-all" title="Sil">
                                            <span class="material-symbols-outlined" style="font-size: 18px;">delete</span>
                                        </button>
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
