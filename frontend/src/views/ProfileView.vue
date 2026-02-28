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

// Renk paleti SignUpView ile eşleşecek şekilde neon tonlara güncellendi
const getPasswordStrengthColor = () => {
    const strength = getPasswordStrength()
    const colors = ['', 'text-red-500', 'text-amber-500', 'text-yellow-400', 'text-neon-green', 'text-green-400']
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
<div class="w-full min-h-screen bg-[#050505] relative overflow-hidden font-sans text-slate-200 selection:bg-neon-blue/30 selection:text-white pt-24 px-4 pb-12">
    
    <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-neon-blue/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen"></div>
    <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-[#f20d80]/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen"></div>
    <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')] opacity-50 z-0 pointer-events-none"></div>

    <div class="max-w-5xl mx-auto space-y-8 relative z-10">
        
        <div class="flex items-center gap-4 mb-10">
            <div class="w-14 h-14 rounded-2xl bg-neon-blue/10 border border-neon-blue/30 flex items-center justify-center backdrop-blur-md shadow-[0_0_20px_rgba(0,191,255,0.2)]">
                <span class="material-symbols-outlined text-neon-blue text-3xl">person</span>
            </div>
            <div>
                <h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Kullanıcı Profili</h1>
                <p class="text-neon-blue text-xs uppercase tracking-widest font-bold mt-1">Hesap Yönetimi</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div class="lg:col-span-1">
                <div class="bg-[#0a0f1a]/80 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_0_40px_rgba(0,0,0,0.5)] relative overflow-hidden group">
                    <div class="absolute -top-20 -right-20 w-48 h-48 bg-neon-blue/10 blur-[50px] rounded-full group-hover:bg-neon-blue/20 transition-colors duration-500"></div>
                    
                    <div class="relative z-10 flex flex-col items-center text-center">
                        <div class="w-28 h-28 rounded-full bg-black border-2 border-neon-blue/50 flex items-center justify-center mb-5 text-5xl text-white font-black shadow-[0_0_20px_rgba(0,191,255,0.3)] relative">
                            <div class="absolute inset-0 rounded-full border border-neon-blue animate-ping opacity-20"></div>
                            {{ user?.full_name?.charAt(0) || 'U' }}
                        </div>
                        
                        <h2 class="text-2xl font-black text-white mb-2">{{ user?.full_name }}</h2>
                        
                        <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-neon-blue/10 text-neon-blue text-[10px] uppercase tracking-widest font-black rounded-md border border-neon-blue/30 mb-8">
                            <span class="w-1.5 h-1.5 rounded-full bg-neon-blue animate-pulse"></span>
                            {{ user?.role === 'ADMIN' ? 'Sistem Yöneticisi' : 'Standart Üye' }}
                        </span>
                        
                        <div class="w-full space-y-3 text-left">
                            <div class="p-4 bg-black/40 rounded-xl border border-white/5 flex items-start gap-3 hover:border-white/10 transition-colors">
                                <span class="material-symbols-outlined text-slate-500 text-lg mt-0.5">mail</span>
                                <div>
                                    <p class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-0.5">E-posta</p>
                                    <p class="text-sm font-medium text-slate-300 break-all">{{ user?.email }}</p>
                                </div>
                            </div>
                            <div class="p-4 bg-black/40 rounded-xl border border-white/5 flex items-start gap-3 hover:border-white/10 transition-colors">
                                <span class="material-symbols-outlined text-slate-500 text-lg mt-0.5">phone_iphone</span>
                                <div>
                                    <p class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-0.5">Telefon</p>
                                    <p class="text-sm font-medium text-slate-300">{{ user?.phone || 'Belirtilmedi' }}</p>
                                </div>
                            </div>
                            <div class="p-4 bg-black/40 rounded-xl border border-white/5 flex items-start gap-3 hover:border-white/10 transition-colors">
                                <span class="material-symbols-outlined text-slate-500 text-lg mt-0.5">calendar_today</span>
                                <div>
                                    <p class="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-0.5">Kayıt Tarihi</p>
                                    <p class="text-sm font-medium text-slate-300">{{ formatDate(user?.created_at) }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="lg:col-span-2">
                <div class="bg-[#0a0f1a]/80 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_0_40px_rgba(0,0,0,0.5)] h-full">
                    
                    <div class="flex items-center gap-3 mb-8 border-b border-white/5 pb-6">
                        <span class="material-symbols-outlined text-slate-400 text-2xl">lock_reset</span>
                        <h3 class="text-xl font-bold text-white">Güvenlik ve Şifre</h3>
                    </div>

                    <form @submit.prevent="handleChangePassword" class="space-y-6">
                        
                        <div v-if="error" class="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-sm flex items-center gap-3">
                            <span class="material-symbols-outlined text-red-500">error</span>
                            <span class="flex-1">{{ error }}</span>
                        </div>
                        <div v-if="message" class="bg-neon-green/10 border border-neon-green/50 text-neon-green p-4 rounded-xl text-sm flex items-center gap-3">
                            <span class="material-symbols-outlined text-neon-green">check_circle</span>
                            <span class="flex-1">{{ message }}</span>
                        </div>

                        <div>
                            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Mevcut Şifre</label>
                            <input 
                                v-model="currentPassword"
                                type="password" 
                                required
                                class="block w-full bg-black/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-all"
                                placeholder="••••••••"
                            >
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-white/5">
                            <div>
                                <div class="flex items-center justify-between mb-2">
                                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest">Yeni Şifre</label>
                                    <span v-if="newPassword" :class="getPasswordStrengthColor()" class="text-[10px] font-bold uppercase tracking-wider">
                                        {{ getPasswordStrengthLabel() }}
                                    </span>
                                </div>
                                <input 
                                    v-model="newPassword"
                                    type="password" 
                                    required
                                    minlength="8"
                                    class="block w-full bg-black/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-all"
                                    placeholder="En az 8 karakter"
                                >
                                
                                <div v-if="newPassword" class="mt-3">
                                    <div class="flex gap-1 mb-2 h-1.5">
                                        <div v-for="i in 5" :key="i" class="flex-1 rounded-full transition-colors duration-300" 
                                            :class="[
                                            getPasswordStrength() >= i 
                                            ? (getPasswordStrength() === 1 ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 
                                                getPasswordStrength() === 2 ? 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' : 
                                                getPasswordStrength() === 3 ? 'bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.5)]' : 
                                                getPasswordStrength() === 4 ? 'bg-neon-green shadow-[0_0_8px_rgba(54,211,153,0.5)]' : 
                                                'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.5)]') 
                                            : 'bg-white/10'
                                            ]">
                                        </div>
                                    </div>
                                    <div class="grid grid-cols-2 gap-x-2 gap-y-1 text-[10px] mt-2">
                                        <span :class="newPassword.length >= 8 ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{newPassword.length >= 8 ? 'check' : 'close'}}</span> En az 8 krk</span>
                                        <span :class="/[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword) ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{/[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword) ? 'check' : 'close'}}</span> Büyük/Küçük harf</span>
                                        <span :class="/\d/.test(newPassword) ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{/\d/.test(newPassword) ? 'check' : 'close'}}</span> En az 1 rakam</span>
                                        <span :class="/[^a-zA-Z\d]/.test(newPassword) ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{/[^a-zA-Z\d]/.test(newPassword) ? 'check' : 'close'}}</span> Özel karakter</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div>
                                <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Yeni Şifre (Tekrar)</label>
                                <input 
                                    v-model="confirmPassword"
                                    type="password" 
                                    required
                                    minlength="8"
                                    class="block w-full bg-black/50 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-all"
                                    placeholder="••••••••"
                                >
                            </div>
                        </div>

                        <div class="flex justify-end pt-6">
                            <button 
                                type="submit" 
                                :disabled="loading"
                                class="relative group px-8 py-3.5 bg-white text-black font-black uppercase tracking-widest rounded-xl overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_20px_rgba(255,255,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                            >
                                <div class="absolute inset-0 bg-neon-blue/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
                                <span v-if="loading" class="relative flex items-center justify-center gap-2">
                                    <svg class="animate-spin h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Güncelleniyor...
                                </span>
                                <span v-else class="relative flex items-center gap-2">
                                    <span class="material-symbols-outlined text-sm">save</span>
                                    Şifreyi Güncelle
                                </span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
</template>