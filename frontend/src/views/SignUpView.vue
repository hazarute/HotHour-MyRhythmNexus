<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import BrandLogo from '@/components/BrandLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  email: '',
  password: '',
  passwordConfirm: '',
  full_name: '',
  phone: '',
  gender: null
})

const loading = ref(false)
const error = ref('')
const success = ref('')
const passwordError = ref('')
const showGenderDropdown = ref(false)
const genderDropdownRef = ref(null)
const formErrors = ref({
  email: '',
  full_name: '',
  phone: '',
  gender: ''
})

const genderLabel = computed(() => {
  return {
    FEMALE: 'Kadın',
    MALE: 'Erkek'
  }[formData.value.gender] || 'Cinsiyet Seçiniz'
})

const handlePhoneInput = (event) => {
  let value = event.target.value
  const cleaned = value.replace(/[^\d\+\-() \.]/g, '')
  if (cleaned !== value) {
    formData.value.phone = cleaned
  }
}

const handleNameInput = (event) => {
  let value = event.target.value
  const cleaned = value.replace(/[^a-zA-ZçğıöşüÇĞİÖŞÜ\s\-]/g, '')
  if (cleaned !== value) {
    formData.value.full_name = cleaned
  }
}

const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validatePhone = (phone) => {
  const digits = phone.replace(/\D/g, '')
  return digits.length >= 10
}

const getPasswordStrength = () => {
  const pwd = formData.value.password
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
  const colors = ['', 'text-red-500', 'text-amber-500', 'text-yellow-400', 'text-neon-green', 'text-green-400']
  return colors[strength] || ''
}

const validateForm = () => {
  formErrors.value = {
    email: '',
    full_name: '',
    phone: '',
    gender: ''
  }

  if (!formData.value.email || !validateEmail(formData.value.email)) {
    formErrors.value.email = 'Geçerli bir e-posta adresi girin'
  }
  if (!formData.value.full_name || formData.value.full_name.trim().length < 3) {
    formErrors.value.full_name = 'Ad Soyadı en az 3 karakter olmalıdır'
  }
  if (!formData.value.phone || !validatePhone(formData.value.phone)) {
    formErrors.value.phone = 'Geçerli bir telefon numarası girin (en az 10 rakam)'
  }
  if (!formData.value.gender) {
    formErrors.value.gender = 'Lütfen cinsiyet seçiniz'
  }

  return !Object.values(formErrors.value).some(err => err !== '')
}

const validatePasswords = () => {
  if (formData.value.password !== formData.value.passwordConfirm) {
    passwordError.value = 'Şifreler eşleşmiyor'
    return false
  }
  if (formData.value.password.length < 8) {
    passwordError.value = 'Şifre en az 8 karakter olmalıdır'
    return false
  }
  passwordError.value = ''
  return true
}

const handleSignUp = async () => {
  if (!validateForm()) return
  if (!validatePasswords()) return

  loading.value = true
  error.value = ''
  try {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
    const registerData = {
      email: formData.value.email,
      password: formData.value.password,
      full_name: formData.value.full_name,
      phone: formData.value.phone,
      gender: formData.value.gender
    }

    const response = await fetch(`${baseUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerData)
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || 'Kayıt başarısız')
    }

    success.value = 'Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...'
    error.value = ''
    setTimeout(() => { router.push('/login') }, 3000)
  } catch (err) {
    error.value = err.message || 'Kayıt sırasında bir hata oluştu'
  } finally {
    loading.value = false
  }
}

const selectGender = (gender) => {
  formData.value.gender = gender
  formErrors.value.gender = ''
  showGenderDropdown.value = false
}

const handleDocumentClick = (event) => {
  if (!showGenderDropdown.value) return
  if (genderDropdownRef.value && !genderDropdownRef.value.contains(event.target)) {
    showGenderDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})
onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<template>
  <div class="w-full min-h-screen bg-[#050505] flex items-center justify-center relative overflow-hidden font-sans text-slate-200 selection:bg-neon-blue/30 selection:text-white p-4 py-12">
    
    <div class="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-neon-magenta/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
    <div class="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-neon-blue/15 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
    <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wMykiLz48L3N2Zz4=')] opacity-50 z-0 pointer-events-none"></div>

    <div class="w-full max-w-lg relative z-10">
      
      <div class="flex flex-col items-center mb-8">
        <div class="w-16 h-16 mb-4 bg-black/40 border border-white/10 rounded-2xl flex items-center justify-center backdrop-blur-xl shadow-[0_0_30px_rgba(242,13,128,0.2)]">
          <BrandLogo className="w-10 h-10" />
        </div>
        <h1 class="text-3xl font-black text-white tracking-tight">Yeni Hesap</h1>
        <p class="text-neon-magenta text-xs uppercase tracking-widest font-bold mt-1">Aramıza Katıl</p>
      </div>

      <div class="bg-[#0a0f1a]/80 backdrop-blur-2xl border border-white/10 rounded-3xl p-6 sm:p-8 shadow-[0_0_40px_rgba(0,0,0,0.5)]">
        
        <form @submit.prevent="handleSignUp" class="space-y-5">
          
          <div v-if="error" class="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-sm flex items-center gap-3">
            <span class="material-symbols-outlined text-red-500">error</span>
            <span class="flex-1">{{ error }}</span>
          </div>
          <div v-if="success" class="bg-neon-green/10 border border-neon-green/50 text-neon-green p-4 rounded-xl text-sm flex items-center gap-3">
            <span class="material-symbols-outlined text-neon-green">check_circle</span>
            <span class="flex-1">{{ success }}</span>
          </div>

          <div>
            <label for="full_name" class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Ad Soyad</label>
            <input
              v-model="formData.full_name"
              @input="handleNameInput"
              id="full_name"
              type="text"
              required
              class="block w-full bg-black/50 border rounded-xl py-2.5 px-4 text-white focus:outline-none focus:ring-1 transition-all"
              :class="formErrors.full_name ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-white/10 focus:border-neon-blue focus:ring-neon-blue'"
              placeholder="Adınız Soyadınız"
            />
            <p v-if="formErrors.full_name" class="text-red-400 text-xs mt-1 font-medium">{{ formErrors.full_name }}</p>
          </div>

          <div>
            <label for="email" class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">E-posta</label>
            <input
              v-model="formData.email"
              id="email"
              type="email"
              required
              class="block w-full bg-black/50 border rounded-xl py-2.5 px-4 text-white focus:outline-none focus:ring-1 transition-all"
              :class="formErrors.email ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-white/10 focus:border-neon-blue focus:ring-neon-blue'"
              placeholder="ornek@email.com"
            />
            <p v-if="formErrors.email" class="text-red-400 text-xs mt-1 font-medium">{{ formErrors.email }}</p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div>
              <label for="phone" class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Telefon</label>
              <input
                v-model="formData.phone"
                @input="handlePhoneInput"
                id="phone"
                type="tel"
                required
                class="block w-full bg-black/50 border rounded-xl py-2.5 px-4 text-white focus:outline-none focus:ring-1 transition-all"
                :class="formErrors.phone ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-white/10 focus:border-neon-blue focus:ring-neon-blue'"
                placeholder="5XX XXX XX XX"
              />
              <p v-if="formErrors.phone" class="text-red-400 text-[10px] mt-1 font-medium">{{ formErrors.phone }}</p>
            </div>

            <div>
              <label for="gender" class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Cinsiyet</label>
              <div ref="genderDropdownRef" class="relative" @click.stop>
                <button
                  id="gender"
                  type="button"
                  @click="showGenderDropdown = !showGenderDropdown"
                  class="w-full flex items-center justify-between bg-black/50 border rounded-xl py-2.5 px-4 text-white focus:outline-none focus:ring-1 transition-all"
                  :class="[
                    formErrors.gender ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-white/10 focus:border-neon-blue focus:ring-neon-blue',
                    showGenderDropdown ? 'border-neon-blue ring-1 ring-neon-blue' : ''
                  ]"
                >
                  <span :class="formData.gender ? 'text-white' : 'text-slate-500'">{{ genderLabel }}</span>
                  <span class="material-symbols-outlined text-slate-400 transition-transform duration-300" :class="{ 'rotate-180 text-neon-blue': showGenderDropdown }">expand_more</span>
                </button>

                <div v-if="showGenderDropdown" class="absolute top-full left-0 mt-2 w-full bg-[#1a2230] border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden backdrop-blur-xl">
                  <button type="button" @click="selectGender('FEMALE')" class="w-full text-left px-4 py-3 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors border-b border-white/5">Kadın</button>
                  <button type="button" @click="selectGender('MALE')" class="w-full text-left px-4 py-3 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors">Erkek</button>
                </div>
              </div>
              <p v-if="formErrors.gender" class="text-red-400 text-[10px] mt-1 font-medium">{{ formErrors.gender }}</p>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1.5">
                <label for="password" class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest">Şifre</label>
                <span v-if="formData.password" :class="getPasswordStrengthColor()" class="text-[10px] font-bold uppercase tracking-wider">
                  {{ getPasswordStrengthLabel() }}
                </span>
            </div>
            <input
              v-model="formData.password"
              id="password"
              type="password"
              required
              class="block w-full bg-black/50 border border-white/10 rounded-xl py-2.5 px-4 text-white focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-all"
              placeholder="En az 8 karakter"
            />
            
            <div v-if="formData.password" class="mt-3">
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
                <span :class="formData.password.length >= 8 ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{formData.password.length >= 8 ? 'check' : 'close'}}</span> En az 8 karakter</span>
                <span :class="/[A-Z]/.test(formData.password) && /[a-z]/.test(formData.password) ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{/[A-Z]/.test(formData.password) && /[a-z]/.test(formData.password) ? 'check' : 'close'}}</span> Büyük & Küçük harf</span>
                <span :class="/\d/.test(formData.password) ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{/\d/.test(formData.password) ? 'check' : 'close'}}</span> En az 1 rakam</span>
                <span :class="/[^a-zA-Z\d]/.test(formData.password) ? 'text-neon-green' : 'text-slate-500'" class="flex items-center gap-1"><span class="material-symbols-outlined text-[12px]">{{/[^a-zA-Z\d]/.test(formData.password) ? 'check' : 'close'}}</span> Özel karakter</span>
              </div>
            </div>
          </div>

          <div>
            <label for="passwordConfirm" class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Şifre Tekrarı</label>
            <input
              v-model="formData.passwordConfirm"
              id="passwordConfirm"
              type="password"
              required
              class="block w-full bg-black/50 border rounded-xl py-2.5 px-4 text-white focus:outline-none focus:ring-1 transition-all"
              :class="passwordError && formData.passwordConfirm ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-white/10 focus:border-neon-blue focus:ring-neon-blue'"
              placeholder="Şifreyi tekrarla"
            />
            <p v-if="passwordError" class="text-red-400 text-[10px] mt-1 font-medium">{{ passwordError }}</p>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full relative group px-8 py-3.5 bg-white text-black font-black uppercase tracking-widest rounded-xl overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_20px_rgba(255,255,255,0.2)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 mt-6"
          >
            <div class="absolute inset-0 bg-neon-blue/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out"></div>
            <span v-if="loading" class="relative flex items-center justify-center gap-3">
              <svg class="animate-spin h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Hesap Oluşturuluyor...
            </span>
            <span v-else class="relative">Kayıt Ol</span>
          </button>
        </form>

        <div class="mt-8 text-center border-t border-white/5 pt-6">
          <p class="text-sm text-slate-400 mb-2">Zaten bir hesabın var mı?</p>
          <router-link to="/login" class="inline-flex items-center gap-1 font-bold text-neon-magenta hover:text-white transition-colors uppercase tracking-wider text-xs">
            Giriş Yap <span class="material-symbols-outlined text-sm">login</span>
          </router-link>
        </div>

      </div>
    </div>
  </div>
</template>