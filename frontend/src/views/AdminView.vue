<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter, RouterLink, RouterView } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
    authStore.logout()
    router.push({ name: 'home' })
}
</script>

<template>
  <div class="min-h-screen bg-dark-bg text-gray-100 flex flex-col md:flex-row">
    
    <!-- Sidebar -->
    <aside class="w-full md:w-64 bg-card-bg/50 border-r border-gray-800 flex-shrink-0">
        <div class="p-6 border-b border-gray-800">
             <h1 class="text-2xl font-bold text-neon-pink tracking-tight drop-shadow-neon">Studio<br/><span class="text-white">Manager</span></h1>
             <p class="text-xs text-gray-500 mt-2">Admin Control Panel</p>
        </div>
        
        <nav class="p-4 space-y-2">
             <RouterLink :to="{ name: 'admin-dashboard' }" 
                class="block px-4 py-3 rounded hover:bg-white/5 text-gray-300 hover:text-white transition-colors"
                active-class="bg-neon-blue/10 text-neon-blue font-bold border-l-2 border-neon-blue">
                Auctions & Dashboard
             </RouterLink>
             
             <RouterLink :to="{ name: 'admin-reservations' }" 
                class="block px-4 py-3 rounded hover:bg-white/5 text-gray-300 hover:text-white transition-colors"
                active-class="bg-neon-blue/10 text-neon-blue font-bold border-l-2 border-neon-blue">
                Reservations
             </RouterLink>

             <hr class="border-gray-800 my-4" />
             
             <button @click="logout" class="w-full text-left px-4 py-3 rounded hover:bg-red-900/20 text-red-400 hover:text-red-300 transition-colors flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                </svg>
                Logout
             </button>
        </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-4 md:p-8 overflow-y-auto h-screen">
        <RouterView />
    </main>

  </div>
</template>
