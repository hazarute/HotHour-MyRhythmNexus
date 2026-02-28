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
  <div class="flex flex-col min-h-screen">
    <!-- Top Navigation -->
    <header v-if="!isAdminRoute" class="sticky top-0 z-50 w-full border-b border-white/10 bg-background-dark/80 backdrop-blur-md">
      <div class="px-6 md:px-12 py-4 flex items-center justify-between">
        <div class="flex items-center gap-10">
          <router-link to="/" class="flex items-center gap-4 group">
            <BrandLogo className="w-12 h-12 transition-transform duration-300 group-hover:scale-110" />
            <span class="text-2xl font-bold tracking-tight text-white mb-0.5">HotHour</span>
          </router-link>
          
          <nav class="hidden md:flex items-center gap-8">
            <router-link to="/" class="text-sm font-medium text-neon-blue drop-shadow-[0_0_8px_rgba(0,240,255,0.5)]">Ana Sayfa</router-link>
            <router-link to="/auctions" class="text-sm font-medium text-slate-400 hover:text-white transition-colors" active-class="text-white">Canlı Oturumları Gör</router-link>
            <template v-if="authStore.isAuthenticated">
                <router-link to="/my-reservations" class="text-sm font-medium text-slate-400 hover:text-white transition-colors" active-class="text-white">Rezervasyonlarım</router-link>
            </template>
            <template v-else>
                <router-link to="/how-it-works" class="text-sm font-medium text-slate-400 hover:text-white transition-colors">Nasıl Çalışır</router-link>
            </template>
            <router-link v-if="authStore.isAdmin" to="/admin" class="text-sm font-medium text-slate-400 hover:text-white transition-colors">Studio Panel</router-link>
          </nav>
        </div>

        <div class="flex items-center gap-4">
          <div class="hidden md:flex items-center relative group">
            <span class="absolute left-3 text-slate-500 material-symbols-outlined text-lg">search</span>
            <input class="bg-surface-dark border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-primary w-64 transition-all" placeholder="Search studios..." type="text">
          </div>
          
          <div class="hidden md:flex items-center gap-2">
            <template v-if="authStore.isAuthenticated">
               <router-link to="/profile" class="text-sm font-medium text-slate-400 hover:text-white transition-colors mr-2 px-3 py-2 rounded-full hover:bg-white/5">
                   Profil
               </router-link>
               <button @click="handleLogout" class="bg-surface-dark hover:bg-surface-dark/80 text-white text-sm font-bold py-2 px-6 rounded-full border border-white/10 transition-colors">
                  Çıkış Yap
              </button>
            </template>
            <template v-else>
              <router-link to="/login" class="bg-surface-dark hover:bg-surface-dark/80 text-white text-sm font-bold py-2 px-6 rounded-full border border-white/10 transition-colors">
                  Giriş Yap
              </router-link>
              <router-link to="/signup" class="bg-primary hover:bg-blue-600 text-white text-sm font-bold py-2 px-6 rounded-full shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/40">
                  Kayıt Ol
              </router-link>
            </template>
          </div>

          <!-- Mobile Menu Button -->
          <button @click="toggleMobileMenu" class="md:hidden text-white hover:text-primary transition-colors p-2">
            <span class="material-symbols-outlined text-3xl">menu</span>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div v-if="isMobileMenuOpen" class="md:hidden border-t border-white/10 bg-background-dark/95 backdrop-blur-xl absolute top-full left-0 w-full p-4 flex flex-col gap-4 shadow-2xl animate-fade-in-down">
        <router-link to="/" class="text-base font-medium text-neon-blue p-2 rounded-lg hover:bg-white/5" active-class="bg-white/5">Ana Sayfa</router-link>
        <router-link to="/auctions" class="text-base font-medium text-slate-300 p-2 rounded-lg hover:bg-white/5 hover:text-white" active-class="bg-white/5 text-white">Canlı Oturumları Gör</router-link>
        
        <template v-if="authStore.isAuthenticated">
            <router-link to="/my-reservations" class="text-base font-medium text-slate-300 p-2 rounded-lg hover:bg-white/5 hover:text-white" active-class="bg-white/5 text-white">Rezervasyonlarım</router-link>
            <router-link to="/profile" class="text-base font-medium text-slate-300 p-2 rounded-lg hover:bg-white/5 hover:text-white" active-class="bg-white/5 text-white">Profilim</router-link>
            <router-link v-if="authStore.isAdmin" to="/admin" class="text-base font-medium text-slate-300 p-2 rounded-lg hover:bg-white/5 hover:text-white" active-class="bg-white/5 text-white">Studio Panel</router-link>
            <button @click="handleLogout" class="text-left text-base font-medium text-red-400 p-2 rounded-lg hover:bg-white/5 hover:text-red-300">
                Çıkış Yap
            </button>
        </template>
        
        <template v-else>
            <router-link to="/how-it-works" class="text-base font-medium text-slate-300 p-2 rounded-lg hover:bg-white/5 hover:text-white">Nasıl Çalışır</router-link>
            <div class="flex flex-col gap-3 mt-2">
                <router-link to="/login" class="text-center bg-surface-dark hover:bg-surface-dark/80 text-white font-bold py-3 rounded-lg border border-white/10 transition-colors">
                    Giriş Yap
                </router-link>
                <router-link to="/signup" class="text-center bg-primary hover:bg-blue-600 text-white font-bold py-3 rounded-lg shadow-lg shadow-blue-500/20 transition-all">
                    Kayıt Ol
                </router-link>
            </div>
        </template>
      </div>
    </header>

    <main class="flex-grow flex flex-col items-center w-full">
        <router-view />
    </main>
  </div>
</template>
