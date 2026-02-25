<script setup>
import { useAuthStore } from './stores/auth'
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

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
          <router-link to="/" class="flex items-center gap-3 group">
            <div class="w-8 h-8 text-primary group-hover:text-neon-blue transition-colors duration-300">
              <svg class="w-full h-full" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path d="M24 4C12.9543 4 4 7.25611 4 11.2727C4 14.0109 8.16144 16.3957 14.31 17.6364C8.16144 18.877 4 21.2618 4 24C4 26.7382 8.16144 29.123 14.31 30.3636C8.16144 31.6043 4 33.9891 4 36.7273C4 40.7439 12.9543 44 24 44C35.0457 44 44 40.7439 44 36.7273C44 33.9891 39.8386 31.6043 33.69 30.3636C39.8386 29.123 44 26.7382 44 24C44 21.2618 39.8386 18.877 33.69 17.6364C39.8386 16.3957 44 14.0109 44 11.2727C44 7.25611 35.0457 4 24 4Z" fill="currentColor"></path>
              </svg>
            </div>
            <span class="text-xl font-bold tracking-tight text-white">HotHour</span>
          </router-link>
          
          <nav class="hidden md:flex items-center gap-8">
            <router-link to="/" class="text-sm font-medium text-neon-blue drop-shadow-[0_0_8px_rgba(0,240,255,0.5)]">Arena</router-link>
            <template v-if="authStore.isAuthenticated">
                <router-link to="/my-reservations" class="text-sm font-medium text-slate-400 hover:text-white transition-colors" active-class="text-white">My Reservations</router-link>
            </template>
            <template v-else>
                <a class="text-sm font-medium text-slate-400 hover:text-white transition-colors" href="#">Studios</a>
                <a class="text-sm font-medium text-slate-400 hover:text-white transition-colors" href="#">How it Works</a>
            </template>
            <router-link v-if="authStore.isAdmin" to="/admin" class="text-sm font-medium text-slate-400 hover:text-white transition-colors">Studio Panel</router-link>
          </nav>
        </div>

        <div class="flex items-center gap-4">
          <div class="hidden md:flex items-center relative group">
            <span class="absolute left-3 text-slate-500 material-symbols-outlined text-lg">search</span>
            <input class="bg-surface-dark border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-primary w-64 transition-all" placeholder="Search studios..." type="text">
          </div>
          
          <template v-if="authStore.isAuthenticated">
             <button @click="handleLogout" class="bg-surface-dark hover:bg-surface-dark/80 text-white text-sm font-bold py-2 px-6 rounded-full border border-white/10 transition-colors">
                Logout
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="bg-surface-dark hover:bg-surface-dark/80 text-white text-sm font-bold py-2 px-6 rounded-full border border-white/10 transition-colors">
                Sign In
            </router-link>
            <router-link to="/" class="bg-primary hover:bg-blue-600 text-white text-sm font-bold py-2 px-6 rounded-full shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/40">
                Join Free
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <main class="flex-grow flex flex-col items-center w-full">
        <router-view />
    </main>
  </div>
</template>
