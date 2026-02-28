<script setup>
import { useAuthStore } from './stores/auth'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BrandLogo from '@/components/BrandLogo.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
}

watch(() => route.path, () => {
    isMobileMenuOpen.value = false
})

onMounted(async () => {
  if (authStore.token) {
    await authStore.fetchUserProfile(authStore.token)
  }
})

const isAdminRoute = computed(() => route.path.startsWith('/admin'))

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="flex flex-col min-h-screen bg-[#050505] selection:bg-neon-blue/30 selection:text-white">
    
    <header v-if="!isAdminRoute" class="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0a0f1a]/70 backdrop-blur-2xl transition-all duration-300 shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        
        <div class="flex items-center gap-10">
          
          <router-link to="/" class="flex items-center gap-3 group">
            <div class="relative w-10 h-10 flex items-center justify-center bg-black/50 border border-white/10 rounded-xl group-hover:border-neon-blue/50 transition-colors shadow-[0_0_15px_rgba(0,191,255,0.1)] group-hover:shadow-[0_0_20px_rgba(0,191,255,0.3)]">
              <BrandLogo className="w-6 h-6 transition-transform duration-300 group-hover:scale-110" />
            </div>
            <span class="text-xl md:text-2xl font-black tracking-tighter text-white mb-0.5">HotHour</span>
          </router-link>
          
          <nav class="hidden lg:flex items-center gap-8">
            <router-link to="/" class="text-[11px] font-bold uppercase tracking-widest text-slate-400 hover:text-white transition-colors" active-class="text-neon-blue drop-shadow-[0_0_8px_rgba(0,191,255,0.5)]">
              Ana Sayfa
            </router-link>
            <router-link to="/all-auctions" class="text-[11px] font-bold uppercase tracking-widest text-slate-400 hover:text-white transition-colors" active-class="text-neon-blue drop-shadow-[0_0_8px_rgba(0,191,255,0.5)]">
              Canlı Arena
            </router-link>
            
            <template v-if="authStore.isAuthenticated">
                <router-link to="/my-reservations" class="text-[11px] font-bold uppercase tracking-widest text-slate-400 hover:text-white transition-colors" active-class="text-neon-blue drop-shadow-[0_0_8px_rgba(0,191,255,0.5)]">
                  Biletlerim
                </router-link>
            </template>
            <template v-else>
                <router-link to="/how-it-works" class="text-[11px] font-bold uppercase tracking-widest text-slate-400 hover:text-white transition-colors" active-class="text-neon-blue drop-shadow-[0_0_8px_rgba(0,191,255,0.5)]">
                  Nasıl Çalışır
                </router-link>
            </template>
            
            <router-link v-if="authStore.isAdmin" to="/admin" class="text-[11px] font-bold uppercase tracking-widest text-neon-magenta hover:text-white transition-colors flex items-center gap-1">
              <span class="material-symbols-outlined text-[14px]">admin_panel_settings</span> Studio Panel
            </router-link>
          </nav>
        </div>

        <div class="flex items-center gap-4 md:gap-6">
          
          <div class="hidden md:flex items-center relative group">
            <span class="absolute left-4 text-slate-500 material-symbols-outlined text-lg group-focus-within:text-neon-blue transition-colors">search</span>
            <input 
              class="bg-black/40 border border-white/10 rounded-full py-2.5 pl-11 pr-4 text-sm text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue w-48 lg:w-64 transition-all placeholder:text-slate-600" 
              placeholder="Oturum ara..." 
              type="text"
            >
          </div>
          
          <div class="hidden md:flex items-center gap-3">
            <template v-if="authStore.isAuthenticated">
               <router-link to="/profile" class="text-sm font-bold text-slate-300 hover:text-white transition-colors px-4 py-2.5 rounded-xl hover:bg-white/5 flex items-center gap-2 border border-transparent hover:border-white/10">
                   <span class="material-symbols-outlined text-lg">account_circle</span>
               </router-link>
               <button @click="handleLogout" class="bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-bold uppercase tracking-widest py-2.5 px-6 rounded-xl border border-red-500/20 hover:border-red-500/40 transition-colors flex items-center gap-2">
                  <span class="material-symbols-outlined text-[16px]">logout</span> Çıkış
              </button>
            </template>
            <template v-else>
              <router-link to="/login" class="bg-white/5 hover:bg-white/10 text-white text-[11px] font-bold uppercase tracking-widest py-2.5 px-6 rounded-xl border border-white/10 transition-colors">
                  Giriş Yap
              </router-link>
              <router-link to="/signup" class="bg-neon-blue hover:bg-blue-400 text-black text-[11px] font-black uppercase tracking-widest py-2.5 px-6 rounded-xl shadow-[0_0_15px_rgba(0,191,255,0.3)] hover:shadow-[0_0_25px_rgba(0,191,255,0.5)] transition-all hover:scale-105">
                  Kayıt Ol
              </router-link>
            </template>
          </div>

          <button @click="toggleMobileMenu" class="md:hidden text-white hover:text-neon-blue transition-colors p-2 bg-white/5 rounded-xl border border-white/10 focus:outline-none">
            <span class="material-symbols-outlined text-2xl">{{ isMobileMenuOpen ? 'close' : 'menu_open' }}</span>
          </button>
        </div>
      </div>

      <div v-if="isMobileMenuOpen" class="md:hidden absolute top-full left-0 w-full bg-[#0a0f1a]/95 backdrop-blur-3xl border-b border-white/10 shadow-[0_20px_40px_rgba(0,0,0,0.7)] flex flex-col origin-top animate-in slide-in-from-top-2 duration-300">
        <div class="px-4 py-6 flex flex-col gap-2">
            
            <router-link to="/" class="text-sm font-bold uppercase tracking-widest text-slate-300 p-4 rounded-xl hover:bg-white/5 hover:text-white border border-transparent flex items-center gap-3" active-class="bg-white/5 border-white/10 text-neon-blue">
                <span class="material-symbols-outlined">home</span> Ana Sayfa
            </router-link>
            
            <router-link to="/all-auctions" class="text-sm font-bold uppercase tracking-widest text-slate-300 p-4 rounded-xl hover:bg-white/5 hover:text-white border border-transparent flex items-center gap-3" active-class="bg-white/5 border-white/10 text-neon-blue">
                <span class="material-symbols-outlined">local_fire_department</span> Canlı Arena
            </router-link>
            
            <template v-if="authStore.isAuthenticated">
                <router-link to="/my-reservations" class="text-sm font-bold uppercase tracking-widest text-slate-300 p-4 rounded-xl hover:bg-white/5 hover:text-white border border-transparent flex items-center gap-3" active-class="bg-white/5 border-white/10 text-neon-blue">
                    <span class="material-symbols-outlined">local_activity</span> Biletlerim
                </router-link>
                
                <router-link to="/profile" class="text-sm font-bold uppercase tracking-widest text-slate-300 p-4 rounded-xl hover:bg-white/5 hover:text-white border border-transparent flex items-center gap-3" active-class="bg-white/5 border-white/10 text-neon-blue">
                    <span class="material-symbols-outlined">account_circle</span> Profilim
                </router-link>
                
                <router-link v-if="authStore.isAdmin" to="/admin" class="text-sm font-bold uppercase tracking-widest text-neon-magenta p-4 rounded-xl hover:bg-white/5 hover:text-white border border-transparent flex items-center gap-3" active-class="bg-white/5 border-white/10">
                    <span class="material-symbols-outlined">admin_panel_settings</span> Studio Panel
                </router-link>
                
                <div class="h-px bg-white/10 my-2"></div>
                
                <button @click="handleLogout" class="text-left text-sm font-bold uppercase tracking-widest text-red-400 p-4 rounded-xl hover:bg-red-500/10 hover:border-red-500/20 border border-transparent transition-colors flex items-center gap-3">
                    <span class="material-symbols-outlined">logout</span> Çıkış Yap
                </button>
            </template>
            
            <template v-else>
                <router-link to="/how-it-works" class="text-sm font-bold uppercase tracking-widest text-slate-300 p-4 rounded-xl hover:bg-white/5 hover:text-white border border-transparent flex items-center gap-3" active-class="bg-white/5 border-white/10 text-neon-blue">
                    <span class="material-symbols-outlined">help</span> Nasıl Çalışır
                </router-link>
                
                <div class="flex flex-col gap-3 mt-4 px-2">
                    <router-link to="/login" class="text-center bg-white/5 hover:bg-white/10 text-white text-xs font-bold uppercase tracking-widest py-4 rounded-xl border border-white/10 transition-colors">
                        Giriş Yap
                    </router-link>
                    <router-link to="/signup" class="text-center bg-neon-blue text-black text-xs font-black uppercase tracking-widest py-4 rounded-xl shadow-[0_0_20px_rgba(0,191,255,0.3)] transition-all">
                        Hemen Kayıt Ol
                    </router-link>
                </div>
            </template>
        </div>
      </div>
    </header>

    <main class="flex-grow flex flex-col items-center w-full relative z-10">
        <router-view />
    </main>
  </div>
</template>

<style scoped>
/* Mobil menü ikon geçişi için ufak bir animasyon sınıfı eklenebilir */
</style>