<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import BrandLogo from '@/components/BrandLogo.vue' // Logoyu buraya da ekledik

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
            error.value = data.detail || 'E-posta doğrulama başarısız oldu. Lütfen tekrar deneyiniz.'
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
  <div class="w-full min-h-screen bg-[#050505] flex items-center justify-center relative overflow-hidden font-sans text-slate-200 selection:bg-neon-blue/30 selection:text-white p-4">
    
    <div class="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-neon-blue/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen animate-pulse"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-[#f20d80]/15 rounded-full blur-[120px] pointer-events-none mix-blend-screen animate-pulse" style="animation-delay: 1s;"></div>
    <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')] opacity-50 z-0 pointer-events-none"></div>

    <div class="w-full max-w-md relative z-10">
      
      <div class="flex flex-col items-center mb-8">
        <div class="w-20 h-20 mb-4 bg-black/40 border border-white/10 rounded-2xl flex items-center justify-center backdrop-blur-xl shadow-[0_0_30px_rgba(0,191,255,0.2)]">
          <BrandLogo className="w-12 h-12" />
        </div>
        <h1 class="text-3xl font-black text-white tracking-tight">HotHour</h1>
        <p class="text-neon-blue text-xs uppercase tracking-widest font-bold mt-1">E-posta Doğrulama</p>
      </div>

      <div class="bg-[#0a0f1a]/80 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_0_40px_rgba(0,0,0,0.5)] text-center">
        
        <div v-if="loading" class="space-y-6">
          <div class="w-24 h-24 mx-auto rounded-full bg-black/50 border border-white/10 flex items-center justify-center relative shadow-[0_0_30px_rgba(0,191,255,0.2)]">
            <div class="absolute inset-0 rounded-full border-t-2 border-neon-blue animate-spin"></div>
            <div class="absolute inset-2 rounded-full border-r-2 border-purple-500 animate-spin opacity-70" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
            <span class="material-symbols-outlined text-neon-blue text-3xl animate-pulse">lock_open</span>
          </div>
          <div>
            <h2 class="text-xl font-bold text-white mb-2 uppercase tracking-wide">Bağlantı Şifresi Çözülüyor</h2>
            <p class="text-slate-400 text-sm">Lütfen bekleyin, hesabınız güvenli bir şekilde onaylanıyor.</p>
          </div>
        </div>

        <div v-else-if="success" class="space-y-6">
          <div class="w-24 h-24 mx-auto rounded-full bg-neon-green/10 border border-neon-green/30 flex items-center justify-center relative shadow-[0_0_40px_rgba(54,211,153,0.3)]">
            <div class="absolute inset-0 rounded-full border border-neon-green animate-ping opacity-20"></div>
            <span class="material-symbols-outlined text-neon-green text-5xl">check_circle</span>
          </div>
          <div>
            <h2 class="text-2xl font-black text-white mb-2">Arenaya Giriş İzni Verildi!</h2>
            <p class="text-slate-300 text-sm mb-4">Hesabınız başarıyla doğrulandı. Artık seanslara teklif verebilirsiniz.</p>
            <p class="text-[10px] text-neon-blue uppercase tracking-widest font-bold animate-pulse">Giriş sayfasına yönlendiriliyorsunuz...</p>
          </div>
          <div class="pt-4 border-t border-white/5">
            <button
              @click="router.push('/login')"
              class="w-full relative group px-8 py-4 bg-neon-blue text-black font-black uppercase tracking-widest rounded-xl overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_20px_rgba(0,191,255,0.3)]"
            >
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
              <span class="relative">Giriş Yap</span>
            </button>
          </div>
        </div>

        <div v-else class="space-y-6">
          <div class="w-24 h-24 mx-auto rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center shadow-[0_0_40px_rgba(239,68,68,0.3)]">
            <span class="material-symbols-outlined text-red-500 text-5xl">error</span>
          </div>
          <div>
            <h2 class="text-xl font-black text-white mb-2 uppercase tracking-wide">Erişim Reddedildi</h2>
            <div class="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-sm mt-4 text-center backdrop-blur-md">
              {{ error }}
            </div>
          </div>
          <div class="pt-6 space-y-3 border-t border-white/5">
            <button
              @click="router.push('/login')"
              class="w-full relative group px-8 py-3.5 bg-neon-blue text-black font-black uppercase tracking-widest rounded-xl overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_20px_rgba(0,191,255,0.3)]"
            >
              <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
              <span class="relative">Giriş Sayfasına Dön</span>
            </button>
            <button
              @click="router.push('/')"
              class="w-full py-3.5 bg-black/50 hover:bg-black/70 border border-white/10 text-white font-bold uppercase tracking-widest text-[11px] rounded-xl transition-all"
            >
              Ana Sayfaya Dön
            </button>
          </div>
          <div class="text-[10px] text-slate-500 uppercase tracking-widest pt-4">
            <p class="mb-1">Destek için:</p>
            <p class="text-slate-400 font-bold">support@hothour.com</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>