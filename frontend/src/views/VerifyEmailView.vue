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
        error.value = 'Geçersiz doğrulama linki. Token bulunamadı.'
        loading.value = false
        return
    }

    try {
        const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
        const response = await fetch(`${baseUrl}/api/v1/auth/verify-email?token=${token}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })

        if (response.ok) {
            success.value = true
            // If user is logged in, update their verification status in store
            if (authStore.user) {
                authStore.user.is_verified = true
            }
            setTimeout(() => {
                router.push('/login')
            }, 3000)
        } else {
            const data = await response.json()
            error.value = data.detail || 'Email doğrulama başarısız oldu. Lütfen tekrar deneyiniz.'
        }
    } catch (err) {
        error.value = 'Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyiniz.'
        console.error('Verification error:', err)
    } finally {
        loading.value = false
    }
})
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-dark-bg flex items-center justify-center px-4">
    <!-- Background Effects -->
    <div class="absolute inset-0 z-0">
      <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px] animate-pulse-slow"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-neon-blue/20 rounded-full blur-[120px] animate-pulse-slow delay-1000"></div>
    </div>

    <div class="relative z-10 w-full max-w-md">
      <div class="hh-glass-card rounded-2xl p-8 border border-white/10 shadow-glow backdrop-blur-xl bg-dark-bg/80 text-center">
        <!-- Loading State -->
        <div v-if="loading" class="space-y-6">
          <div class="inline-flex items-center justify-center p-4 rounded-2xl bg-gradient-to-br from-primary to-blue-600 shadow-lg shadow-primary/30">
            <svg class="animate-spin h-12 w-12 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-white mb-2">E-posta Doğrulanıyor...</h2>
            <p class="text-slate-400">Lütfen bekleyiniz. Hesabınız doğrulanıyor.</p>
          </div>
        </div>

        <!-- Success State -->
        <div v-else-if="success" class="space-y-6">
          <div class="inline-flex items-center justify-center p-4 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg shadow-green-500/30">
            <span class="material-symbols-outlined text-white text-5xl">check_circle</span>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-white mb-2">✨ Doğrulama Başarılı!</h2>
            <p class="text-slate-400 mb-4">Hesabınız başarıyla doğrulanmıştır. Artık HotHour'ı tam olarak kullanabilirsiniz.</p>
            <p class="text-sm text-slate-500">Giriş sayfasına yönlendiriliyorsunuz...</p>
          </div>
          <div class="flex gap-3 mt-6">
            <button
              @click="router.push('/login')"
              class="w-full hh-btn-primary py-2.5"
            >
              Giriş Yap
            </button>
          </div>
        </div>

        <!-- Error State -->
        <div v-else class="space-y-6">
          <div class="inline-flex items-center justify-center p-4 rounded-2xl bg-gradient-to-br from-red-500 to-rose-600 shadow-lg shadow-red-500/30">
            <span class="material-symbols-outlined text-white text-5xl">error</span>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-white mb-2">❌ Doğrulama Başarısız</h2>
            <div class="bg-red-500/10 border border-red-500 text-red-300 p-4 rounded-lg text-sm mt-4 text-center">
              {{ error }}
            </div>
          </div>
          <div class="pt-6 space-y-3">
            <button
              @click="router.push('/login')"
              class="w-full hh-btn-primary py-2.5"
            >
              Giriş Sayfasına Dön
            </button>
            <button
              @click="router.push('/')"
              class="w-full bg-slate-700 hover:bg-slate-600 text-white py-2.5 rounded-lg transition-colors"
            >
              Ana Sayfaya Dön
            </button>
          </div>
          <div class="text-sm text-slate-400 pt-6 border-t border-white/10">
            <p class="mb-2">Sorun devam ediyorsa:</p>
            <p>support@hothour.com ile iletişime geçebilirsiniz.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
