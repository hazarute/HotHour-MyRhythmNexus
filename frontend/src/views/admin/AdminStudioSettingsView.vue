<script setup>
import { onMounted, computed } from 'vue'
import { useAdminStudio } from '@/composables/admin/useAdminStudio'
import AdminNotificationDropdown from '@/components/admin/AdminNotificationDropdown.vue'

const {
    studio,
    loading,
    error,
    successMessage,
    fetchStudio,
    updateStudio,
    uploadLogo // Added this line
} = useAdminStudio()

onMounted(() => {
    fetchStudio()
})

const handleSave = async () => {
    await updateStudio()
}

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    // Check type client side basic
    if (!file.type.startsWith('image/')) {
        error.value = "Lütfen sadece görsel dosyası yükleyin."
        return
    }
    
    // Call upload logic
    await uploadLogo(file)
    // Clear input after upload
    event.target.value = ''
}

// Ensure the domain is added to relative URLs if necessary
const fullLogoUrl = computed(() => {
    if (!studio.value.logoUrl) return ''
    if (studio.value.logoUrl.startsWith('http')) return studio.value.logoUrl
    const baseUrl = import.meta.env.VITE_API_URL || ''
    return `${baseUrl}${studio.value.logoUrl}`
})

// Very basic url validation visualization - adapted for partial paths
const isValidLogo = computed(() => {
    if (!studio.value.logoUrl) return true
    if (studio.value.logoUrl.startsWith('/uploads/')) return true
    try {
        new URL(studio.value.logoUrl)
        return true
    } catch {
        return false
    }
})
</script>

<template>
    <div class="h-full flex flex-col pt-16 md:pt-0">
        <!-- Top Header -->
        <header class="hidden md:flex bg-white dark:bg-background-dark border-b border-slate-200 dark:border-slate-800 px-8 py-5 items-center justify-between sticky top-0 z-20">
            <div>
                <h1 class="text-2xl font-bold text-slate-800 dark:text-white mb-1">Stüdyo Ayarları</h1>
                <p class="text-sm border-0 bg-transparent text-slate-500 dark:text-slate-400">
                    Stüdyonuza ait görünüm ve iletişim bilgilerini güncelleyin.
                </p>
            </div>
            <div class="flex items-center gap-4">
                <AdminNotificationDropdown />
            </div>
        </header>

        <!-- Main Content (Scrollable) -->
        <div class="flex-1 overflow-y-auto bg-slate-50/50 dark:bg-transparent p-4 md:p-8">
            <div class="max-w-4xl mx-auto space-y-6">
                
                <!-- Status Messages -->
                <div v-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl border border-red-100 dark:border-red-900/50 text-sm flex items-center justify-between gap-3">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined">error</span>
                        {{ error }}
                    </div>
                </div>

                <div v-if="successMessage" class="p-4 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 rounded-xl border border-emerald-100 dark:border-emerald-900/50 text-sm flex items-center justify-between gap-3">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined">check_circle</span>
                        {{ successMessage }}
                    </div>
                </div>

                <!-- Settings Card -->
                <div class="bg-white dark:bg-background-dark rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                    <div class="p-6 md:p-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                        <h2 class="text-lg font-semibold text-slate-800 dark:text-white">Genel Bilgiler</h2>
                    </div>

                    <form @submit.prevent="handleSave" class="p-6 md:p-8 space-y-8">
                        <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
                            
                            <!-- Left Column: Form Fields -->
                            <div class="md:col-span-8 space-y-5">
                                <!-- Name -->
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Stüdyo Adı</label>
                                    <input 
                                        v-model="studio.name" 
                                        type="text" 
                                        required
                                        placeholder="Örn: SoundHub Kadıköy"
                                        class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary text-slate-800 dark:text-white transition-colors"
                                    />
                                </div>
                                
                                <!-- Address -->
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Açık Adres</label>
                                    <textarea 
                                        v-model="studio.address" 
                                        rows="3"
                                        placeholder="Stüdyonuzun açık adresini girin..."
                                        class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary text-slate-800 dark:text-white transition-colors resize-none"
                                    ></textarea>
                                </div>

                                <!-- Logo URL -->
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Stüdyo Logosu</label>
                                    <div class="relative">
                                        <input 
                                            type="file" 
                                            accept="image/*"
                                            @change="handleFileUpload"
                                            :disabled="loading"
                                            class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary text-slate-800 dark:text-white transition-colors file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary-dark cursor-pointer disabled:opacity-50"
                                        />
                                    </div>
                                    <p class="mt-1.5 border-0 bg-transparent text-xs text-slate-500">Stüdyo logonuzu bilgisayarınızdan seçip yükleyin. (Seçtiğiniz an yüklenecektir)</p>
                                    
                                    <div v-if="studio.logoUrl" class="mt-3">
                                        <label class="block text-xs font-medium text-slate-500 mb-1">Mevcut Logo Yolu:</label>
                                        <input 
                                            v-model="studio.logoUrl" 
                                            type="text" 
                                            disabled
                                            class="w-full px-3 py-1.5 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-md text-slate-500 dark:text-slate-400 text-xs"
                                        />
                                    </div>
                                </div>

                                <!-- Google Maps URL -->
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Google Maps URL</label>
                                    <input 
                                        v-model="studio.googleMapsUrl" 
                                        type="text" 
                                        placeholder="Örn: https://goo.gl/maps/..."
                                        class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary text-slate-800 dark:text-white transition-colors"
                                    />
                                    <p class="mt-1.5 border-0 bg-transparent text-xs text-slate-500">Kullanıcıların stüdyonuza kolayca ulaşabilmesi için harita linki.</p>
                                </div>
                            </div>

                            <!-- Right Column: Logo Preview -->
                            <div class="md:col-span-4 flex flex-col items-center">
                                <label class="hidden md:block text-sm font-medium text-slate-700 dark:text-slate-300 mb-4 w-full text-center">Önizleme</label>
                                <div class="w-40 h-40 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center p-2 bg-slate-50 dark:bg-slate-800/30 overflow-hidden relative">
                                    <template v-if="studio.logoUrl && isValidLogo">
                                        <img :src="fullLogoUrl" alt="Studio Logo Preview" class="w-full h-full object-contain" />
                                    </template>
                                    <template v-else>
                                        <span class="material-symbols-outlined text-4xl text-slate-400 mb-2">image</span>
                                        <span class="text-xs text-slate-500 text-center">Logo bulunamadı</span>
                                    </template>
                                </div>
                                
                                <div v-if="studio.name" class="mt-6 w-full max-w-sm">
                                    <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-[#1a2230] shadow-sm">
                                        <div class="flex items-center gap-3">
                                            <div class="w-10 h-10 rounded-lg bg-slate-100 flex-shrink-0 flex items-center justify-center overflow-hidden">
                                                <img v-if="studio.logoUrl && isValidLogo" :src="fullLogoUrl" class="w-full h-full object-cover"/>
                                                <span v-else class="material-symbols-outlined text-slate-400">store</span>
                                            </div>
                                            <div class="flex flex-col min-w-0">
                                                <span class="text-sm font-semibold truncate text-slate-900 dark:text-white">{{ studio.name }}</span>
                                                <span class="text-xs text-slate-500 truncate">{{ studio.address || 'Adres belirtilmedi' }}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <p class="mt-2 text-center text-xs text-slate-500 border-0 bg-transparent">Kullanıcılara böyle görünecek</p>
                                </div>
                            </div>

                        </div>

                        <!-- Actions -->
                        <div class="pt-6 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3">
                            <button 
                                type="button" 
                                @click="fetchStudio"
                                :disabled="loading"
                                class="px-5 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-300 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 rounded-xl transition-colors min-w-[120px] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer border-0"
                            >
                                Değişiklikleri Geri Al
                            </button>
                            <button 
                                type="submit" 
                                :disabled="loading"
                                class="px-5 py-2.5 text-sm font-medium text-white bg-primary hover:bg-primary-dark rounded-xl shadow-sm shadow-primary/20 transition-all flex items-center justify-center gap-2 min-w-[140px] disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer border-0"
                            >
                                <span v-if="loading" class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span>
                                <span v-else>Değişiklikleri Kaydet</span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>