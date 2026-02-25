<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const success = ref(false)
const error = ref('')

onMounted(async () => {
    const token = route.query.token
    
    if (!token) {
        error.value = 'Doğrulama bağlantısı geçersiz.'
        loading.value = false
        return
    }

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/verify-email?token=${token}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })

        if (response.ok) {
            success.value = true
            // If user is logged in, update their verification status in store
            if (authStore.user) {
                authStore.user.isVerified = true
            }
            setTimeout(() => {
                router.push('/login')
            }, 3000)
        } else {
            const data = await response.json()
            error.value = data.detail || 'Doğrulama başarısız oldu.'
        }
    } catch (err) {
        error.value = 'Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyiniz.'
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="relative min-h-screen overflow-hidden bg-dark-bg flex items-center justify-center p-4">
        <!-- Background Effects -->
        <div class="absolute inset-0 z-0">
            <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px] animate-pulse-slow"></div>
            <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-neon-blue/20 rounded-full blur-[120px] animate-pulse-slow delay-1000"></div>
        </div>

        <div class="relative z-10 w-full max-w-md">
            <div class="hh-glass-card p-8 rounded-2xl text-center border border-white/10 shadow-glow backdrop-blur-xl bg-dark-bg/80">
                
                <!-- Loading State -->
                <div v-if="loading" class="flex flex-col items-center py-8">
                    <div class="w-16 h-16 border-4 border-primary/30 border-t-primary rounded-full animate-spin mb-6"></div>
                    <h2 class="text-2xl font-bold text-white mb-2">Doğrulanıyor...</h2>
                    <p class="text-slate-400">Lütfen bekleyiniz, e-posta adresiniz kontrol ediliyor.</p>
                </div>

                <!-- Success State -->
                <div v-else-if="success" class="flex flex-col items-center py-8">
                    <div class="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mb-6">
                        <span class="material-symbols-outlined text-green-500 text-4xl">check_circle</span>
                    </div>
                    <h2 class="text-2xl font-bold text-white mb-2">E-posta Doğrulandı!</h2>
                    <p class="text-slate-400 mb-6">Hesabınız başarıyla doğrulandı. Giriş sayfasına yönlendiriliyorsunuz...</p>
                    <button @click="router.push('/login')" class="hh-btn-primary w-full">
                        Giriş Yap
                    </button>
                </div>

                <!-- Error State -->
                <div v-else class="flex flex-col items-center py-8">
                    <div class="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mb-6">
                        <span class="material-symbols-outlined text-red-500 text-4xl">error</span>
                    </div>
                    <h2 class="text-2xl font-bold text-white mb-2">Doğrulama Başarısız</h2>
                    <p class="text-red-300 mb-6 bg-red-500/10 p-3 rounded-lg border border-red-500/30">
                        {{ error }}
                    </p>
                    <button @click="router.push('/')" class="hh-btn-secondary w-full">
                        Ana Sayfaya Dön
                    </button>
                </div>
                
            </div>
        </div>
    </div>
</template>
