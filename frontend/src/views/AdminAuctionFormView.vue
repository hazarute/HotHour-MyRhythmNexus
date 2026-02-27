<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuctionStore } from '@/stores/auction'
import AuctionCreateForm from '@/components/AuctionCreateForm.vue'

const route = useRoute()
const router = useRouter()
const store = useAuctionStore()

const loading = ref(false)
const error = ref(null)
const auctionData = ref(null)

const isEditMode = computed(() => !!route.params.id)

onMounted(async () => {
    if (isEditMode.value) {
        loading.value = true
        try {
            // Check if we have the auction in store, otherwise fetch
            const id = route.params.id
            await store.fetchAuctionById(id)
            auctionData.value = store.currentAuction
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }
})

const handleFormSubmit = async (formData) => {
    try {
        if (isEditMode.value) {
            await store.updateAuction(formData)
            alert('Oturum başarıyla güncellendi.')
        } else {
            await store.createAuction(formData)
            alert('Oturum başarıyla oluşturuldu.')
        }
        router.push({ name: 'admin-dashboard' })
    } catch (err) {
        alert((isEditMode.value ? 'Güncelleme' : 'Oturum oluşturma') + ' hatası: ' + err.message)
    }
}
</script>

<template>
    <div class="flex flex-col h-full w-full bg-background-light dark:bg-background-dark overflow-hidden relative">
        <!-- Header -->
        <header class="sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between px-4 py-3 md:px-8 md:py-5 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-[#111811]/80 backdrop-blur-md gap-4">
            <div class="flex items-center gap-4">
                <button @click="router.back()" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                    <span class="material-symbols-outlined">arrow_back</span>
                </button>
                <div class="flex flex-col gap-1">
                    <h2 class="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">
                        {{ isEditMode ? 'Oturumu Düzenle' : 'Yeni Oturum Oluştur' }}
                    </h2>
                    <p class="text-slate-500 dark:text-slate-400 text-xs md:text-sm">
                        {{ isEditMode ? `#${route.params.id} numaralı oturumu düzenliyorsunuz.` : 'Yeni bir dinamik fiyatlandırma oturumu tanımlayın.' }}
                    </p>
                </div>
            </div>
        </header>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 md:p-8">
            <div class="max-w-4xl mx-auto">
                <div v-if="loading" class="flex items-center justify-center h-64">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>

                <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-900/30 mb-6">
                    {{ error }}
                </div>

                <div v-else class="bg-white dark:bg-[#1a2230] p-4 md:p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative z-20">
                    <AuctionCreateForm 
                        :initialData="auctionData" 
                        :isEdit="isEditMode" 
                        @create-auction="handleFormSubmit" 
                        @update-auction="handleFormSubmit" 
                    />
                </div>
            </div>
        </div>
    </div>
</template>