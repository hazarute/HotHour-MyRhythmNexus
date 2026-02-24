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
  <div class="relative min-h-screen overflow-hidden bg-dark-bg">
    <div class="absolute inset-0 opacity-35 bg-gradient-to-br from-neon-blue/10 via-primary/5 to-neon-magenta/10"></div>
    <div class="absolute inset-0 bg-gradient-to-r from-dark-bg via-dark-bg/95 to-dark-bg/70"></div>

    <div class="relative hh-section min-h-screen flex items-center py-10">
      <div class="w-full grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        <div class="hidden lg:block">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neon-blue mb-6">
            <span class="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
            Studio Control Center
          </div>

          <h1 class="text-5xl font-black text-white leading-tight tracking-tight mb-4">
            Manage Auctions.
            <span class="block text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-primary hh-text-glow">Control Revenue.</span>
          </h1>

          <p class="text-slate-400 text-lg max-w-xl leading-relaxed">
            Sign in to access the HotHour admin panel, manage live sessions, and verify reservation codes at studio speed.
          </p>
        </div>

        <div class="w-full max-w-md lg:ml-auto">
          <div class="hh-glass-card rounded-2xl p-8 border border-white/10 shadow-glow">
            <div class="mb-6">
              <p class="text-neon-blue text-xs uppercase tracking-widest mb-2">Admin Access</p>
              <h2 class="text-3xl font-bold text-white">Sign In</h2>
              <p class="text-slate-400 mt-2 text-sm">Access the HotHour Control Center</p>
            </div>

            <form @submit.prevent="handleLogin" class="space-y-5">
              <div v-if="error" class="bg-red-500/10 border border-red-500 text-red-300 p-3 rounded-lg text-sm text-center">
                {{ error }}
              </div>

              <div>
                <label for="email" class="block text-sm font-medium text-slate-300 mb-1.5">Email Address</label>
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
                <label for="password" class="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
                <input
                  v-model="password"
                  id="password"
                  type="password"
                  required
                  class="block w-full bg-dark-bg/60 border border-slate-700 rounded-lg py-2.5 px-3 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue"
                  placeholder="••••••••"
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
                  Signing In...
                </span>
                <span v-else>Sign In</span>
              </button>
            </form>

            <div class="mt-5 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-slate-500">
              <span>Unauthorized access is prohibited.</span>
              <router-link to="/" class="text-neon-blue hover:text-white transition-colors">Back to Arena</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
