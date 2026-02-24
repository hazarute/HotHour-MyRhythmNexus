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
      router.push('/admin') // Or the originally intended destination
    } else {
      error.value = 'Login failed. Please check your credentials.'
    }
  } catch (err) {
    error.value = err.message || 'An error occurred during login.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-bg px-4">
    <div class="w-full max-w-md bg-card-bg p-8 rounded-lg shadow-lg border border-gray-800">
      <div class="text-center mb-6">
        <h1 class="text-3xl font-bold text-neon-pink">Admin Login</h1>
        <p class="text-gray-400 mt-2 text-sm">Access the HotHour Control Center</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div v-if="error" class="bg-red-500/10 border border-red-500 text-red-400 p-3 rounded text-sm text-center">
          {{ error }}
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-300">Email Address</label>
          <input 
            v-model="email" 
            id="email" 
            type="email" 
            required 
            class="mt-1 block w-full bg-dark-bg/50 border border-gray-700 rounded-md py-2 px-3 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue"
            placeholder="admin@hothour.com"
          />
        </div>

        <div>
           <label for="password" class="block text-sm font-medium text-gray-300">Password</label>
           <input 
            v-model="password" 
            id="password" 
            type="password" 
            required 
            class="mt-1 block w-full bg-dark-bg/50 border border-gray-700 rounded-md py-2 px-3 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue"
            placeholder="••••••••"
          />
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full py-3 px-4 bg-neon-blue hover:bg-blue-600 text-dark-bg font-bold rounded shadow-lg shadow-neon-blue/20 transition-all duration-300 flex justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="flex items-center gap-2">
            <svg class="animate-spin h-5 w-5 text-dark-bg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Signing In...
          </span>
          <span v-else>Sign In</span>
        </button>
      </form>
      
      <div class="mt-6 text-center text-xs text-gray-500">
        Unauthorized access is strictly prohibited.
      </div>
    </div>
  </div>
</template>
