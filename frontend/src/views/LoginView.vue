<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import BrandLogo from '@/components/BrandLogo.vue'

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
  <div class="w-full min-h-screen bg-[#050505] flex items-center justify-center relative overflow-hidden font-sans text-slate-200 selection:bg-neon-blue/30 selection:text-white p-4">
    
    <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-neon-blue/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-[#f20d80]/15 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
    <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')] opacity-50 z-0 pointer-events-none"></div>

    <div class="w-full max-w-md relative z-10">
      
      <div class="flex flex-col items-center mb-8">
        <div class="w-20 h-20 mb-4 bg-black/40 border border-white/10 rounded-2xl flex items-center justify-center backdrop-blur-xl shadow-[0_0_30px_rgba(0,191,255,0.2)]">
          <BrandLogo className="w-12 h-12" />
        </div>
        <h1 class="text-3xl font-black text-white tracking-tight">HotHour</h1>
        <p class="text-neon-blue text-xs uppercase tracking-widest font-bold mt-1">Sisteme Giriş Yap</p>
      </div>

      <div class="bg-[#0a0f1a]/80 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_0_40px_rgba(0,0,0,0.5)]">
        
        <form @submit.prevent="handleLogin" class="space-y-6">
          
          <div v-if="error" class="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-sm text-center flex items-center gap-3 backdrop-blur-md">
            <span class="material-symbols-outlined text-red-500">error</span>
            <span class="flex-1 text-left">{{ error }}</span>
          </div>

          <div>
            <label for="email" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">E-posta Adresi</label>
            <div class="relative group">
              <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-neon-blue transition-colors">mail</span>
              <input
                v-model="email"
                id="email"
                type="email"
                required
                class="block w-full bg-black/50 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-all"
                placeholder="ornek@email.com"
              />
            </div>
          </div>

          <div>
            <label for="password" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Şifre</label>
            <div class="relative group">
              <span class="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-neon-blue transition-colors">lock</span>
              <input
                v-model="password"
                id="password"
                type="password"
                required
                class="block w-full bg-black/50 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full relative group px-8 py-4 bg-neon-blue text-black font-black uppercase tracking-widest rounded-xl overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_20px_rgba(0,191,255,0.3)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 mt-2"
          >
            <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
            <span v-if="loading" class="relative flex items-center justify-center gap-3">
              <svg class="animate-spin h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Bağlanılıyor...
            </span>
            <span v-else class="relative">Giriş Yap</span>
          </button>

        </form>

        <div class="mt-8 text-center border-t border-white/5 pt-6">
          <p class="text-sm text-slate-400 mb-2">Hesabın yok mu?</p>
          <router-link to="/signup" class="inline-flex items-center gap-1 font-bold text-neon-blue hover:text-white transition-colors uppercase tracking-wider text-xs">
            Hemen Kayıt Ol <span class="material-symbols-outlined text-sm">arrow_forward</span>
          </router-link>
        </div>
        
        <div class="mt-6 text-center">
             <router-link to="/" class="text-xs text-slate-500 hover:text-slate-300 transition-colors inline-flex items-center gap-1">
                 <span class="material-symbols-outlined text-xs">arrow_back</span> Arenaya Dön
             </router-link>
        </div>

      </div>
    </div>
  </div>
</template>