<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const success = await authStore.login(email.value, password.value)
    if (success) {
      if (authStore.isAdmin) {
        router.push('/admin')
      } else {
        router.push('/')
      }
    } else {
      error.value = authStore.error || 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.'
    }
  } catch (err) {
    error.value = err.message || 'Giriş sırasında bir hata oluştu.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-dark-bg">
    <div class="relative hh-section min-h-screen flex items-center justify-center px-4 sm:px-6 py-10">
      <div class="w-full max-w-md">
        <!-- Login Form -->
        <div class="w-full">
            <!-- Mobile Logo/Branding -->
            <div class="lg:hidden text-center mb-8">
                <div class="inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-br from-primary to-blue-600 shadow-lg shadow-primary/30 mb-4">
                     <span class="material-symbols-outlined text-white text-3xl">hourglass_top</span>
                </div>
                <h1 class="text-2xl font-bold text-white mb-2">HotHour</h1>
                <p class="text-slate-400 text-sm">Pilates Oturumları Platformu</p>
            </div>

          <div class="hh-glass-card rounded-2xl p-6 sm:p-8 border border-white/10 shadow-glow backdrop-blur-xl bg-dark-bg/80">
            <div class="mb-6 text-center lg:text-left">
              <p class="text-neon-blue text-xs uppercase tracking-widest mb-2 font-bold">Kullanıcı Girişi</p>
              <h2 class="text-2xl sm:text-3xl font-bold text-white">Hoşgeldiniz</h2>
              <p class="text-slate-400 mt-2 text-sm">Hesabınıza giriş yaparak oturumları keşfedin</p>
            </div>

            <form @submit.prevent="handleLogin" class="space-y-5">
              <div v-if="error" class="bg-red-500/10 border border-red-500 text-red-300 p-3 rounded-lg text-sm text-center">
                {{ error }}
              </div>

              <div>
                <label for="email" class="block text-sm font-medium text-slate-300 mb-1.5">E-posta Adresi</label>
                <input
                  v-model="email"
                  id="email"
                  type="email"
                  required
                  class="block w-full bg-dark-bg/60 border border-slate-700 rounded-lg py-2.5 px-3 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue"
                  placeholder="admin@hothourapp.com"
                />
              </div>

              <div>
                <label for="password" class="block text-sm font-medium text-slate-300 mb-1.5">Şifre</label>
                <input
                  v-model="password"
                  id="password"
                  type="password"
                  required
                  class="block w-full bg-dark-bg/60 border border-slate-700 rounded-lg py-2.5 px-3 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue"
                  placeholder=""
                />
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full hh-btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="loading" class="flex items-center gap-2">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Giriş Yapılıyor...
                </span>
                <span v-else>Giriş Yap</span>
              </button>

              <div class="text-center text-sm text-slate-400">
                Hesabın yok mu?
                <router-link to="/signup" class="ml-1 font-medium text-neon-blue hover:text-white transition-colors">
                  Hemen Kayıt Ol
                </router-link>
              </div>
            </form>

            <div class="mt-5 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-slate-500">
              <span>Güvenli ve şifreli bağlantı.</span>
              <router-link to="/" class="text-neon-blue hover:text-white transition-colors">Arenaya Dön</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
