<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const message = ref('')
const error = ref('')
const loading = ref(false)

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

// Password strength helpers
const getPasswordStrength = () => {
    const pwd = newPassword.value
    let strength = 0
    if (pwd.length >= 8) strength++
    if (pwd.length >= 12) strength++
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++
    if (/\d/.test(pwd)) strength++
    if (/[^a-zA-Z\d]/.test(pwd)) strength++
    return strength
}

const getPasswordStrengthLabel = () => {
    const strength = getPasswordStrength()
    const labels = ['', 'Zayıf', 'Orta', 'İyi', 'Güçlü', 'Çok Güçlü']
    return labels[strength] || ''
}

const getPasswordStrengthColor = () => {
    const strength = getPasswordStrength()
    const colors = ['', 'text-red-400', 'text-amber-400', 'text-yellow-400', 'text-lime-400', 'text-green-400']
    return colors[strength] || ''
}

const handleChangePassword = async () => {
    message.value = ''
    error.value = ''
    
    if (newPassword.value !== confirmPassword.value) {
        error.value = 'Yeni şifreler eşleşmiyor.'
        return
    }
    
    if (newPassword.value.length < 8) {
        error.value = 'Şifre en az 8 karakter olmalıdır.'
        return
    }

    loading.value = true
    const success = await authStore.changePassword(currentPassword.value, newPassword.value)
    loading.value = false
    
    if (success) {
        message.value = 'Şifreniz başarıyla güncellendi.'
        currentPassword.value = ''
        newPassword.value = ''
        confirmPassword.value = ''
    } else {
        error.value = authStore.error || 'Şifre değiştirilemedi.'
    }
}
</script>

<template>
<div class="w-full min-h-screen pt-24 px-4 pb-12">
    <div class="max-w-4xl mx-auto space-y-8">
        <!-- Header -->
        <div class="flex items-center gap-4 mb-8">
            <h1 class="text-3xl font-bold text-white">Profilim</h1>
            <div class="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Profile Info Card -->
            <div class="md:col-span-1">
                <div class="bg-surface-dark border border-white/10 rounded-2xl p-6 shadow-xl relative overflow-hidden group">
                    <!-- Glow effect -->
                    <div class="absolute -top-10 -right-10 w-32 h-32 bg-primary/20 blur-3xl rounded-full group-hover:bg-primary/30 transition-all duration-500"></div>
                    
                    <div class="relative z-10 flex flex-col items-center text-center">
                        <div class="w-24 h-24 rounded-full bg-surface-light border-2 border-primary/30 flex items-center justify-center mb-4 text-4xl text-primary font-bold">
                            {{ user?.full_name?.charAt(0) || 'U' }}
                        </div>
                        <h2 class="text-xl font-bold text-white mb-1">{{ user?.full_name }}</h2>
                        <span class="px-3 py-1 bg-primary/10 text-primary text-xs rounded-full border border-primary/20 mb-6">
                            {{ user?.role === 'ADMIN' ? 'Admin' : 'Üye' }}
                        </span>
                        
                        <div class="w-full space-y-4 text-left">
                            <div class="p-3 bg-background-dark/50 rounded-lg border border-white/5">
                                <p class="text-xs text-slate-500 mb-1">Email</p>
                                <p class="text-sm text-slate-300 break-all">{{ user?.email }}</p>
                            </div>
                            <div class="p-3 bg-background-dark/50 rounded-lg border border-white/5">
                                <p class="text-xs text-slate-500 mb-1">Telefon</p>
                                <p class="text-sm text-slate-300">{{ user?.phone }}</p>
                            </div>
                            <div class="p-3 bg-background-dark/50 rounded-lg border border-white/5">
                                <p class="text-xs text-slate-500 mb-1">Kayıt Tarihi</p>
                                <p class="text-sm text-slate-300">{{ formatDate(user?.created_at) }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Password Change Form -->
            <div class="md:col-span-2">
                <div class="bg-surface-dark border border-white/10 rounded-2xl p-6 md:p-8 shadow-xl relative">
                    <h3 class="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <span class="material-symbols-outlined text-primary">lock_reset</span>
                        Şifre Değiştir
                    </h3>

                    <form @submit.prevent="handleChangePassword" class="space-y-6">
                        <div v-if="error" class="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-sm">
                            {{ error }}
                        </div>
                        <div v-if="message" class="p-4 bg-green-500/10 border border-green-500/20 rounded-lg text-green-500 text-sm">
                            {{ message }}
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-slate-400 mb-2">Mevcut Şifre</label>
                            <input 
                                v-model="currentPassword"
                                type="password" 
                                required
                                class="w-full bg-background-dark border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                                placeholder="••••••••"
                            >
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-slate-400 mb-2">
                                    Yeni Şifre
                                    <span v-if="newPassword" :class="getPasswordStrengthColor()" class="text-xs ml-2">
                                        ({{ getPasswordStrengthLabel() }})
                                    </span>
                                </label>
                                <input 
                                    v-model="newPassword"
                                    type="password" 
                                    required
                                    minlength="8"
                                    class="w-full bg-background-dark border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                                    placeholder="En az 8 karakter"
                                >
                                <div v-if="newPassword" class="mt-2 text-xs text-slate-400">
                                    <div class="flex items-center gap-2 mb-1">
                                        <div class="h-1 w-full bg-slate-700 rounded flex items-center overflow-hidden">
                                            <div class="h-full transition-all duration-300" :class="{
                                                'w-1/5 bg-red-500': getPasswordStrength() === 1,
                                                'w-2/5 bg-amber-500': getPasswordStrength() === 2,
                                                'w-3/5 bg-yellow-500': getPasswordStrength() === 3,
                                                'w-4/5 bg-lime-500': getPasswordStrength() === 4,
                                                'w-full bg-green-500': getPasswordStrength() === 5
                                            }"></div>
                                        </div>
                                    </div>
                                    <ul class="space-y-0.5 mt-2">
                                        <li :class="newPassword.length >= 8 ? 'text-green-400' : 'text-slate-500'">✓ En az 8 karakter</li>
                                        <li :class="/[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword) ? 'text-green-400' : 'text-slate-500'">✓ Büyük ve küçük harf</li>
                                        <li :class="/\d/.test(newPassword) ? 'text-green-400' : 'text-slate-500'">✓ En az bir sayı</li>
                                        <li :class="/[^a-zA-Z\d]/.test(newPassword) ? 'text-green-400' : 'text-slate-500'">✓ Özel karakter</li>
                                    </ul>
                                </div>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-slate-400 mb-2">Yeni Şifre (Tekrar)</label>
                                <input 
                                    v-model="confirmPassword"
                                    type="password" 
                                    required
                                    minlength="8"
                                    class="w-full bg-background-dark border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                                    placeholder="••••••••"
                                >
                            </div>
                        </div>

                        <div class="flex justify-end pt-4">
                            <button 
                                type="submit" 
                                :disabled="loading"
                                class="bg-primary hover:bg-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                {{ loading ? 'Güncelleniyor...' : 'Şifreyi Güncelle' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
</template>