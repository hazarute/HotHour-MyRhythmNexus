<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-container font-sans text-white min-h-screen bg-dark-bg">
    <header class="p-4 flex justify-between items-center border-b border-gray-800 bg-card-bg/90 backdrop-blur sticky top-0 z-50">
      <router-link to="/" class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-neon-blue to-neon-pink">
        HotHour
      </router-link>
      <nav class="space-x-6 flex items-center">
        <router-link to="/" class="hover:text-neon-blue transition-colors text-sm font-medium">Home</router-link>
        
        <template v-if="authStore.isAuthenticated">
          <router-link to="/admin" class="hover:text-neon-pink transition-colors text-sm font-medium">Dashboard</router-link>
          <button @click="handleLogout" class="text-xs border border-gray-600 rounded px-3 py-1 hover:bg-gray-800 transition">
            Logout
          </button>
        </template>
        
        <template v-else>
           <router-link to="/login" class="text-gray-400 hover:text-white text-xs">Admin Access</router-link>
        </template>
      </nav>
    </header>

    <main class="container mx-auto py-8 px-4">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Global styles can go here or in style.css */
</style>
